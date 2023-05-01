from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()
    # あるユーザーがフォローしている相手
    followings = models.ManyToManyField(
        "self",
        through="FriendShip",
        related_name="followers",
        through_fields=("following", "follower"),
        symmetrical=False,
        blank=True,
    )


class FriendShip(models.Model):
    # フォローされている側の人
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follow")
    # フォローしている側の人
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="be_followed_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_friendship"),
        ]
