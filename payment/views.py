from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from content.models import Pricing
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

import stripe


stripe.api_key = "sk_test_51JuBBUBQiGyA5MbMg18MgW2S3r5Cmnie1B8gPp5sMBcPySHEIVTwx4LeTeKHEz9FHAKrT7wLWaU6zWeZQJq1dAy200d52eeXkb"

from django.conf import settings

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()

from .forms import CancelSubscriptionForm


class EnrollView(generic.ListView):
    queryset = Pricing.objects.all()
    template_name = "payment/enroll.html"


class PaymentView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        subscription = request.user.subscription
        pricing = get_object_or_404(Pricing, id=self.kwargs["pk"])

        if subscription.is_active and subscription.pricing == pricing:
            messages.info(request, "already enrolled")
            return redirect("payment:enroll")

        ####################################################################
        if not subscription.stripe_subscription_id:
            return render(request, "payment/payment_create.html", {"pricing": pricing})

        elif subscription.stripe_subscription_id:
            return render(request, "payment/payment_update.html", {"pricing": pricing})


class CreateCheckoutSessionView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        user = self.request.user

        if not user.stripe_customer_id:
            stripe_customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = stripe_customer["id"]
            user.save()

        ####################################################
        pricing = Pricing.objects.get(id=self.kwargs["pk"])
        ######################################################

        domain = "https://domain.com"
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"

        ####################################################

        customer = request.user.stripe_customer_id

        ####################################################
        if pricing.name == "normal":
            trial_period = {
                "trial_period_days": 1,
            }
        else:
            trial_period = None

        ####################################################

        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer,
                line_items=[
                    {
                        "price": pricing.stripe_price_id,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                success_url=domain + reverse("content:course-list"),
                cancel_url=domain + reverse("content:course-list"),
                subscription_data=trial_period,
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)


class ChangeSubscriptionView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        if not self.request.user.subscription.stripe_subscription_id:
            return redirect("content:course-list")
        else:
            subscription_id = self.request.user.subscription.stripe_subscription_id
            subscription = stripe.Subscription.retrieve(subscription_id)
        #######################################################
        pricing = Pricing.objects.get(id=self.kwargs["pk"])
        #######################################################
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
                proration_behavior="always_invoice",
                items=[
                    {
                        "id": subscription["items"]["data"][0].id,
                        "price": pricing.stripe_price_id,
                    }
                ],
            )
            messages.success(self.request, "thank you, payment is successful")
            return redirect("content:course-list")

        except Exception as e:
            messages.error(self.request, f"{e}")
            return redirect("content:course-list")


@csrf_exempt
def webhook(request, *args, **kwargs):
    if request.method == "POST":
        webhook_secret = "whsec_xlNwdoMEHLNLPB9zIh7dsLtI3oMtpXHA"
        request_data = json.loads(request.body)

        if webhook_secret:
            signature = request.headers.get("stripe-signature")
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=signature, secret=webhook_secret
                )
                data = event["data"]
            except Exception as e:
                return e
            event_type = event["type"]
        else:
            data = request_data["data"]
            event_type = request_data["type"]

        data_object = data["object"]
        print("event " + event_type)

        if event_type == "checkout.session.completed":
            print("🔔 Payment succeeded!")
        elif event_type == "customer.subscription.trial_will_end":
            print("Subscription trial will end")
        elif event_type == "customer.subscription.created":
            print("Subscription created %s", event.id)

            stripe_customer_id = data_object["customer"]
            stripe_price_id = data_object["items"]["data"][0]["plan"]["id"]
            pricing = Pricing.objects.get(stripe_price_id=stripe_price_id)

            user = User.objects.get(stripe_customer_id=stripe_customer_id)
            user.subscription.status = data_object["status"]
            user.subscription.stripe_subscription_id = data_object["id"]
            user.subscription.pricing = pricing
            user.subscription.save()

        elif event_type == "customer.subscription.updated":
            print("Subscription created %s", event.id)

            stripe_customer_id = data_object["customer"]
            stripe_price_id = data_object["items"]["data"][0]["plan"]["id"]
            pricing = Pricing.objects.get(stripe_price_id=stripe_price_id)

            user = User.objects.get(stripe_customer_id=stripe_customer_id)
            user.subscription.status = data_object["status"]
            user.subscription.stripe_subscription_id = data_object["id"]
            user.subscription.pricing = pricing
            user.subscription.save()

        elif event_type == "customer.subscription.deleted":
            print("Subscription canceled: %s", event.id)
            stripe_customer_id = data_object["customer"]
            user = User.objects.get(stripe_customer_id=stripe_customer_id)

            user.subscription.status = None
            user.subscription.stripe_subscription_id = None
            user.subscription.pricing = None
            user.subscription.save()

        else:
            # Unexpected event type
            return HttpResponse(status=400)

        return HttpResponse()


class CancelSubscriptionView(LoginRequiredMixin, generic.FormView):
    form_class = CancelSubscriptionForm
    template_name = "payment/payment_cancel.html"

    def get_success_url(self):
        return reverse("content:course-list")

    def form_valid(self, form):
        if not self.request.user.subscription.stripe_subscription_id:
            messages.success(self.request, "no subscription")
            return redirect("content:course-list")

        stripe.Subscription.delete(
            self.request.user.subscription.stripe_subscription_id,
        )

        # stripe.Subscription.modify(
        #     "sub_49ty4767H20z6a",
        #     cancel_at_period_end=True,
        # )

        messages.success(self.request, "cancell your subscription")
        return super().form_valid(form)
