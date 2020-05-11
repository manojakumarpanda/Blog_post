from django.urls import path,include
from .import views  #Login,Create_user,Logout_User


app_name='User_Accounts'
urlpatterns=[
    path('', views.Home.as_view(), name='Home'),
    path('signup/', views.Create_user.as_view(), name='Signup'),
    path('login/', views.Login_User.as_view(), name='Login'),
    path('<str:uuid>/profile/', views.Detail_profile.as_view(), name='Profile'),
    path('profile/<str:pk>/edit/', views.Edit_profile.as_view(), name='Edit_profile'),
    path('logout/', views.Logout_User, name='Logout'),
    # path('api/',include(api.urls)),
]