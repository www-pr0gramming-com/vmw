from django.views import generic

from .models import Course


class CourseListView(generic.ListView):
    queryset = Course.objects.all()


class CourseDetailView(generic.DetailView):
    queryset = Course.objects.all()
