from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.force_login(self.user)

    def test_success_get(self):
        Tweet.objects.create(user=self.user, content="testcontent")
        Tweet.objects.create(user=self.user, content="testcontent")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["tweet_list"], Tweet.objects.all(), ordered=False)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.force_login(self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {
            "user": self.user,
            "content": "testcontent",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Tweet.objects.filter(**valid_data).exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {
            "user": self.user,
            "content": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["content"])
        self.assertFalse(Tweet.objects.filter(**invalid_data).exists())

    def test_failure_post_with_too_long_content(self):
        invalid_data = {
            "user": self.user,
            "content": "x" * 256,
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("この値は 255 文字以下でなければなりません( 256 文字になっています)。", form.errors["content"])
        self.assertFalse(Tweet.objects.filter(**invalid_data).exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.force_login(user)
        self.tweet = Tweet.objects.create(user=user, content="testcontent")
        self.url = reverse("tweets:detail", args=[self.tweet.pk])

    def test_success_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tweet"], Tweet.objects.get(pk=self.tweet.pk))


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test@test.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test@test.com", password="testpassword")
        self.client.force_login(self.user1)
        self.tweet1 = Tweet.objects.create(user=self.user1, content="testcontent")
        self.tweet2 = Tweet.objects.create(user=self.user2, content="testcontent")

    def test_success_post(self):
        response = self.client.post(reverse("tweets:delete", args=[self.tweet1.pk]))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Tweet.objects.filter(pk=self.tweet1.pk).exists())

    def test_failure_post_with_not_exist_tweet(self):
        tweet_objects_all_former = Tweet.objects.all()
        response = self.client.post(reverse("tweets:delete", args=[Tweet.objects.order_by("pk").last().pk + 1]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.all(), tweet_objects_all_former)

    def test_failure_post_with_incorrect_user(self):
        self.client.force_login(self.user2)
        response = self.client.post(reverse("tweets:delete", args=[self.tweet1.pk]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.tweet1.pk).exists())


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
