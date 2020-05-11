from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import pre_save
from .managers import Custom_Manager
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
# Create your models here.


class Countrey(models.Model):
    countrey_name =models.CharField(max_length=30,default='india',verbose_name='countrey')

    def __str__(self):
        return self.countrey_name

    class Meta:
        db_table='countrey'
        ordering=['countrey_name']

    @property
    def state(self):
        return States.objects.filter(count__country__iexact=self.countrey_name)

class States(models.Model):
    state_name  = models.CharField(max_length=30,blank=True,null=True,default='Odisha')
    count = models.ForeignKey(Countrey, on_delete=models.CASCADE, related_name='Districts',default=1)

    def __str__(self):
        return self.state_name

    class Meta:
        db_table='states'
        ordering=['state_name']

    @property
    def dist(self):
        return Districts.objects.filter(state__state_name__iexact=self.state_name)

class Districts(models.Model):
    district_name   = models.CharField(max_length=30, blank=True, null=True,default='Ganjam')
    state = models.ForeignKey(States, on_delete=models.CASCADE,default=1)

    def __str__(self):
        return self.district_name

    class Meta:
        db_table='districts'
        ordering=['district_name']

    @property
    def districts(self):
        return Cities.objects.filter(dist__district_name__iexact=self.district_name)

class Cities(models.Model):
    city_name   = models.CharField(max_length=50, blank=True, null=True,default='Berhampur')
    dist        =models.ForeignKey(Districts,on_delete=models.CASCADE,default=1)

    def __str__(self):
        return self.city_name

    class Meta:
        db_table='cities'
        ordering=['city_name']

    # @property
    # def address(self):
    #     return Address.objects.filter(city__city_name__iexact=self.city_name)

def image_path(instance,filename):
        path= 'profile/%s-%s'%(instance.username,filename)
        return path

class Users(AbstractUser):
    id         = models.UUIDField(primary_key=True,default=uuid.uuid4())
    username   = models.CharField(max_length=30,blank=True,null=True,unique=True,
                                  verbose_name='username')
    first_name  = models.CharField(max_length=30,blank=False,null=False)
    last_name   = models.CharField(max_length=30,blank=False,null=False)
    full_name   = models.CharField(max_length=60,blank=True,null=True,
                                verbose_name='fullname')
    email       = models.EmailField(_('email address'),unique=True)
    photo = models.ImageField(verbose_name='profile_photo', upload_to=image_path, blank=True
                              , null=True)
    countrey    = models.ForeignKey(Countrey,on_delete=models.CASCADE,blank=True,null=True)
    state       = models.ForeignKey(States,on_delete=models.CASCADE,blank=True,null=True)
    dist        = models.ForeignKey(Districts,on_delete=models.CASCADE,blank=True,null=True)
    city        = models.ForeignKey(Cities,on_delete=models.CASCADE,blank=True,null=True)
    house_num = models.CharField(max_length=7, blank=False, null=False, verbose_name='House Numebr/Flat Number',
                                 default='4/1')
    address = models.CharField(max_length=300, blank=False, null=False, verbose_name='Address')
    pin_code = models.CharField(max_length=6, default='760008')
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    updated_at  = models.DateTimeField(auto_created=False,auto_now=now())

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    objects = Custom_Manager

    def get_absolute_url(self):
        return reverse('User_Accounts:Profile',kwargs={'uuid':self.pk})

    class Meta:
        db_table='Accounts'

    def __str__(self):
        return self.full_name


@receiver(pre_save,sender=Users)
def set_fullname(sender,instance,*args,**kwargs):
    if instance.full_name ==None:
        instance.full_name= instance.first_name+' '+instance.last_name
    else:
        instance.full_name=instance.full_name
    return instance.full_name

#(superuser@email.com,superpass1)


