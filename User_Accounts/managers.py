# from User_Accounts.models import Users
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class Custom_Manager(BaseUserManager):

    def create_user(self,email,password,**extra_field):

        if not email:
            raise ValueError(_('The Email can not be blank'))

        email=self.normalize_email(email)
        user = self.model(email=email, **extra_field)
        user.set_password(raw_password=password)
        user.save()
        return user

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        user=BaseUserManager.get_by_natural_key(self,username=username)
        return user

    # def u