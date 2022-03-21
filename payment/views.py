from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from content.models import Pricing
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

import stripe


stripe.api_key = "sk_test_51JuBBUBQiGyA5MbMg18MgW2S3r5Cmnie1B8gPp5sMBcPySHEIVTwx4LeTeKHEz9FHAKrT7wLWaU6zWeZQJq1dAy200d52eeXkb"

from django.conf import settings


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
                "trial_period_days": 7,
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
                metadata={},
                subscription_data=trial_period,
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)
