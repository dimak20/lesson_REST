from django.urls import path
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from user.views import CreateUserView, LoginUserView, ManageUserView

app_name = "users"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage-user"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path("login/", views.obtain_auth_token, name="get-token"),
    # path("login/", LoginUserView.as_view(), name="get-token"),
]
