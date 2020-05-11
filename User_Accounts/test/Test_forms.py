from User_Accounts.forms import *
from User_Accounts.models import *
from django.test import TestCase

class Test_Create_User_form(TestCase):


    def test_Create_user(self):
        self.user=Users_Form(data={'username': ['username1'], 'email': ['user4@gmail.com'],
'password': ['password13'], 'first_name': ['user4'], 'last_name': ['name'], 'house_num': ['4/1'], 'countrey': ['2'], 'state': ['1'], 'dist': ['6'], 'city': ['49'],
 'address': ['Tara devi temple street,'], 'pin_code': ['760010']})
        # self.user=Users_Form(data={'email':'username12@email.com','password':'superuser11','username':'superuser13'
        #                                        ,'first_name':'super','last_name':'user','address':'Some address'
        #                                        ,'countrey_id':2,'state_id':2,'dist':2,'city_id':2})

        self.assertFalse(self.user.is_valid())

    def test_edit_user(self):
        self.user=User_Edit(data={'first_name':'user','last_name':'name','house_num':'43/13',
                'countrey':12,'state':32,'dist':321,'city':34,'address':'same address',
                'pin_code':'433223','photo':'profile/superuser-background_8FB2pVN.jpg'})
        self.assertFalse(self.user.is_valid())

    def test_login(self):
            form1=Login(data={'email':'username@email.com','password':'password1'})
            form2=Login(data={'email':'','password':'password1'})
            form3=Login(data={'email':'username@emil.com','password':''})
            form4=Login(data={'username':'','password':''})

            self.assertTrue(form1.is_valid())
            self.assertFalse(form2.is_valid())
            self.assertFalse(form3.is_valid())
            self.assertFalse(form4.is_valid())