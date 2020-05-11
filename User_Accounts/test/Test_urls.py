# from django.test import SimpleTestCase
# from django.test import RequestFactory
# from django.urls import reverse,resolve
# from User_Accounts import  views
# from User_Accounts.models import *
# from django.contrib.auth import get_user_model,authenticate,login,logout
#
# class Test_urls(SimpleTestCase):
#     #e25f05f84059434f9b6e653fb80e4227
#
#     def test_user_home(self):
#         self.url=reverse('User_Accounts:Home')
#         self.assertEquals(resolve(self.url).func.view_class,views.Home)
#
#     def test_user_create(self):
#         self.url=reverse('User_Accounts:Signup')
#         self.assertEquals(resolve(self.url).func.view_class,views.Create_user)
#
#     def test_user_login(self):
#         self.url=reverse('User_Accounts:Login')
#         assert resolve(self.url).func.view_class==views.Login_User,'Login url not match the expections'
#
#     def test_user_logout(self):
#         self.url=reverse('User_Accounts:Logout')
#         assert resolve(self.url).func==views.Logout_User,'You are not login to use this function'
#
#     def test_user_profile(self):
#         self.url=reverse('User_Accounts:Profile',kwargs={'uuid':'e25f05f84059434f9b6e653fb80e'})
#         assert resolve(self.url).func.view_class==views.Detail_profile,'You have not provided the id of the user'
#
#     def test_user_edit(self):
#         self.url=reverse('User_Accounts:Edit_profile',kwargs={'pk','80328fsf83284180'})
#
#         assert reverse(self.url).func.view_class==views.Detail_profile,'You have not provide a valid pk'
#