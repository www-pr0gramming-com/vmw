from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import pre_save

from django.contrib.auth import get_user_model

User = get_user_model()


from allauth.account.signals import email_confirmed


class Pricing(models.Model):
    name = models.CharField(max_length=100, unique=True)  # basic pro master
    slug = models.SlugField(unique=True, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=50)
    price = models.IntegerField()

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pricing = models.ForeignKey(
        Pricing,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,
        blank=True,
    )
    stripe_subscription_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Course(models.Model):
    pricing = models.ManyToManyField(Pricing, blank=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="thumbnails/")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("content:course-detail", kwargs={"slug": self.slug})


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="videos")
    vimeo_id = models.CharField(max_length=50)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("content:video-detail", kwargs={"slug": self.slug})


def pre_save_course(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name, allow_unicode=True)


def pre_save_video(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title, allow_unicode=True)


def pre_save_pricing(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name, allow_unicode=True)


def post_email_confirmed(request, email_address, *args, **kwargs):
    user = User.objects.get(email=email_address.email)
    subscription = Subscription.objects.create(user=user)
    subscription.save()


pre_save.connect(pre_save_course, sender=Course)
pre_save.connect(pre_save_video, sender=Video)
pre_save.connect(pre_save_pricing, sender=Pricing)
email_confirmed.connect(post_email_confirmed)
