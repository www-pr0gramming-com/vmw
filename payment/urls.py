from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("enroll/", views.EnrollView.as_view(), name="enroll"),
    path("payment/<pk>/", views.PaymentView.as_view(), name="payment"),
    path(
        "create-checkout-session/<pk>/",
        views.CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
]
