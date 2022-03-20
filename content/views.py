from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Course, Video


class CourseListView(generic.ListView):
    queryset = Course.objects.all()


class CourseDetailView(generic.DetailView):
    queryset = Course.objects.all()


class VideoDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Video.objects.all()
