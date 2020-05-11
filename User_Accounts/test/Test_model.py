from User_Accounts.models import Users,Cities,Districts,States,Countrey
from unittest import TestCase
from django.contrib.auth import get_user_model


# class Test_Models(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.User=get_user_model
#         cls.count=Countrey.objects.create(countrey_name='india')
#         cls.state = States.objects.create(state_name='Odisha',count=cls.count)
#         cls.dist = Districts.objects.create(district_name='Ganjam',state=cls.state)
#         cls.city = Cities.objects.create(city_name='Berhampur',dist=cls.dist)
#
#     def test_Cities(self):
#         city=Cities(city_name='Berhampur',dist_id=1)
#         city.save()
#         self.assertEquals(city.city_name,'Berhampur')
#         self.assertEquals(city.dist_id,1)
#         self.assertNotEquals(city.city_name,'berhampur')
#
#     def test_Districts(self):
#         city=Districts(district_name='Ganjam',state=self.state)
#         city.save()
#         self.assertEquals(city.district_name,'Ganjam')
#         self.assertNotEquals(city.district_name,'berhampur')
#         self.assertEquals(city.state_id,1)
#
#     def test_States(self):
#             self.dist=Countrey.objects.get(id=1)
#             city=States(state_name='Odisha',count=self.dist)
#             city.save()
#             self.assertEquals(city.state_name,'Odisha')
#             self.assertNotEquals(city.state_name,'berhampur')
#             self.assertNotEquals(city.count_id,2)
#             self.assertEquals(city.count_id,1)
#
#     def test_countrey(self):
#         self.count=Countrey.objects.create(countrey_name='India')
#         self.assertEquals(self.count.countrey_name,'India')
#         self.assertNotEquals(self.count.countrey_name,'india')
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.count = Countrey.objects.get(countrey_name='india').delete()


# class Test_User(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.User = get_user_model
#         cls.count = Countrey.objects.create(countrey_name='india')
#         cls.state = States.objects.create(state_name='Odisha', count=cls.count)
#         cls.dist = Districts.objects.create(district_name='Ganjam', state=cls.state)
#         cls.city = Cities.objects.create(city_name='Berhampur', dist=cls.dist)
#
#     def test_Users(self):
#         state=self.state
#         self.user=self.User.objects.create(email='username@email.com',password='superuser1',username='superuser'
#                                        ,first_name='super',last_name='user',address='Some address'
#                                        ,countrey_id=1,state_id=1,dist=self.dist,city_id=1
#                                        )
#
#         self.user1=self.User.objects.create(email='username@email.com',password='superuser1',username='superuser'
#                                            ,first_name='super',last_name='user',address='Some address',house_num='4/21'
#                                         ,pin_code='760006'
#                                            ,countrey_id=1,state_id=1,dist=self.dist,city_id=1
#                                            )
#
#         self.assertEquals(self.user.email,'username@email.com')
#         self.assertEquals(self.user.first_name,'super')
#         self.assertEquals(self.user.last_name,'user')
#         self.assertEquals(self.user.username,'superuser')
#         self.assertEquals(self.user.full_name,'super user')
#         self.assertEquals(self.user.house_num,'4/1')
#         self.assertEquals(self.user1.house_num,'4/21')
#         self.assertEquals(self.user.address,'Some address')
#         self.assertEquals(self.user.pin_code,'760008')
#         self.assertEquals(self.user1.pin_code,'760006')
#         self.assertFalse(self.user.photo)
#         self.assertTrue(self.user.state)
#         self.assertTrue(self.user.city)
#         self.assertTrue(self.user.countrey)
#         self.assertTrue(self.user.dist)
#         self.assertTrue(self.user.is_active)
#         self.assertFalse(self.user.is_staff)
#         self.assertFalse(self.user.is_superuser)


