from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import FriendShip

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_duplicated_user(self):
        User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        invalid_data = {
            "username": "testuser",
            "email": "test@gmail.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"], email=invalid_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "te",
            "password2": "te",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "20230228",
            "password2": "20230228",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword1",
            "password2": "testpassword2",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse(settings.LOGIN_URL)
        User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {
            "username": "testU",
            "password": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse(settings.LOGOUT_URL)
        user = User.objects.create_user(username="testuser", email="test@test.com", password="testpassword")
        self.client.force_login(user)

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test@test.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test@test.com", password="testpassword")
        self.client.force_login(self.user1)

        Tweet.objects.create(user=self.user1, content="testcontent")
        Tweet.objects.create(user=self.user2, content="testcontent")
        FriendShip.objects.create(following=self.user1, follower=self.user2)

        self.url = reverse("accounts:user_profile", args=[self.user1.username])

    def test_success_get(self):
        response = self.client.get(self.url)

        self.assertQuerysetEqual(response.context["tweet_list"], Tweet.objects.filter(user=self.user1), ordered=False)
        self.assertEqual(response.context["following_count"], FriendShip.objects.filter(following=self.user1).count())
        self.assertEqual(response.context["follower_count"], FriendShip.objects.filter(follower=self.user1).count())


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test@test.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test@test.com", password="testpassword")
        self.client.force_login(self.user1)

    def test_success_post(self):
        response = self.client.post(reverse("accounts:follow", args=[self.user2.username]))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(FriendShip.objects.filter(following=self.user1, follower=self.user2).exists())

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(reverse("accounts:follow", args=["testuser3"]))

        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.filter(following=self.user1, follower__username="testuser3").exists())

    def test_failure_post_with_self(self):
        response = self.client.post(reverse("accounts:follow", args=[self.user1.username]))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(FriendShip.objects.filter(following=self.user1, follower=self.user1).exists())


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test@test.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test@test.com", password="testpassword")
        self.client.force_login(self.user1)

        FriendShip.objects.create(following=self.user1, follower=self.user2)

    def test_success_post(self):
        response = self.client.post(reverse("accounts:unfollow", args=[self.user2.username]))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.filter(following=self.user1, follower=self.user2).exists())

    def test_failure_post_with_not_exist_user(self):
        count_former = FriendShip.objects.all().count()
        response = self.client.post(reverse("accounts:unfollow", args=["testuser3"]))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(FriendShip.objects.all().count(), count_former)

    def test_failure_post_with_self(self):
        count_former = FriendShip.objects.all().count()
        response = self.client.post(reverse("accounts:unfollow", args=[self.user1.username]))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendShip.objects.all().count(), count_former)


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test@test.com", password="testpassword")
        self.client.force_login(self.user1)

    def test_success_get(self):
        response = self.client.get(reverse("accounts:following_list", args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test@test.com", password="testpassword")
        self.client.force_login(self.user1)

    def test_success_get(self):
        response = self.client.get(reverse("accounts:follower_list", args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
