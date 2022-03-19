from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="thumbnails/")

    def __str__(self):
        return self.name


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="videos")
    vimeo_id = models.CharField(max_length=50)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.title


def pre_save_course(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name, allow_unicode=True)


pre_save.connect(pre_save_course, sender=Course)


def pre_save_video(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title, allow_unicode=True)


pre_save.connect(pre_save_video, sender=Video)