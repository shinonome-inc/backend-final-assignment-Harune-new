from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, RedirectView

from tweets.models import Tweet

from .forms import SignupForm
from .models import FriendShip

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=profile_user)
        context["is_following"] = self.request.user.followings.filter(username=profile_user).exists()
        context["follower_count"] = profile_user.followers.count()
        context["following_count"] = profile_user.followings.count()
        return context


class FollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])

        if self.request.user == target_user:
            messages.error(self.request, "自分自身をフォローできません")
            return HttpResponseBadRequest()
        else:
            self.request.user.followings.add(target_user)

        return super().post(request, *args, **kwargs)


class UnfollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])

        if self.request.user == target_user:
            messages.error(self.request, "自分自身をフォロー解除できません")
            return HttpResponseBadRequest()
        else:
            self.request.user.followings.remove(target_user)

        return super().post(request, *args, **kwargs)


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "accounts/following_list.html"
    model = FriendShip

    def get_queryset(self):
        list = self.model.objects.filter(following__username=self.kwargs["username"])
        return list.order_by("-created_at")


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "accounts/follower_list.html"
    model = FriendShip

    def get_queryset(self):
        list = self.model.objects.filter(follower__username=self.kwargs["username"])
        return list.order_by("-created_at")
