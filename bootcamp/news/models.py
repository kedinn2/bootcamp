import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from bootcamp.notifications.models import Notification, notification_handler


class News(models.Model):
    """News model to contain small information snippets in the same manner as
    Twitter does."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name=_("Publisher"),
        on_delete=models.SET_NULL)
    parent = models.ForeignKey("self", blank=True,
        null=True, on_delete=models.CASCADE, related_name="thread")
    timestamp = models.DateTimeField(auto_now_add=True)
    uuid_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(max_length=280)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL,
        blank=True, related_name="liked")
    reply = models.BooleanField(verbose_name=_("Is a reply?"), default=False)

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ("-timestamp",)

    def __str__(self):
        return str(self.content)

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"uuid": self.uuid})

    def switch_like(self, user, news_obj):
        if user in self.liked.all():
            is_liked = False
            self.liked.remove(user)

        else:
            is_liked = True
            self.liked.add(user)
            notification_handler(user, self.user,
                Notification.LIKED, action_object=self)

        return is_liked

    def get_parent(self):
        if self.parent:
            return self.parent

        else:
            return self

    def count_answers(self):
        parent = self.get_parent()
        return parent.thread.all().count()

    def get_thread(self):
        parent = self.get_parent()
        return parent.thread.all()

    def count_likers(self):
        return self.liked.count()

    def get_likers(self):
        return self.liked.all()


def reply_news(parent_obj, user, text):
    """
    Handler function to create a News instance as a reply to any published
    news.

    :requires:
    :param parent_obj: News instance to which the reply is being made.
    :param user: The logged in user who is doing the reply.
    :param content: String with the reply.
    """
    # TODO
    # Implement the notification call in a proper manner, allowing the call to
    # the notification_handler
    parent = parent_obj.get_parent()
    reply_news = News.objects.create(
        user=user,
        content=text,
        reply=True,
        parent=parent
    )
    notification_handler(
        user, parent_obj.user, Notification.REPLY, action_object=reply_news)
