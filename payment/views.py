from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from content.models import Pricing
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


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
