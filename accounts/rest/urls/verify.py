from django.urls import path

from accounts.rest.views.verify import VerifyEmailAndUsernameView


urlpatterns = [
    path(
        "",
        VerifyEmailAndUsernameView.as_view(),
        name="verify_email_and_username",
    )
]
