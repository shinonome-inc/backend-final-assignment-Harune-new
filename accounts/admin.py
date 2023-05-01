from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import FriendShip

User = get_user_model()


class FollowerFriendShipInline(admin.TabularInline):
    model = FriendShip
    fk_name = "follower"


class FollowingFriendShipInline(admin.TabularInline):
    model = FriendShip
    fk_name = "following"


class UserAdmin(admin.ModelAdmin):
    inlines = [FollowerFriendShipInline, FollowingFriendShipInline]


admin.site.register(User, UserAdmin)
