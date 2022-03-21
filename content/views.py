from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Course, Video


class CourseListView(generic.ListView):
    queryset = Course.objects.all()


class CourseDetailView(generic.DetailView):
    queryset = Course.objects.all()


class VideoDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Video.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscription = self.request.user.subscription
        subscription_is_active = (
            subscription.status == "active" or subscription.status == "trialing"
        )
        course_pricing = self.get_object().course.pricing.all()
        subscription_pricing = subscription.pricing

        if subscription_pricing in course_pricing and subscription_is_active:
            has_permission = True
        else:
            has_permission = False

        context.update(
            {
                "has_permission": has_permission,
            }
        )
        return context
