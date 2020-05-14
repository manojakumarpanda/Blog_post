from django.contrib import messages
from django.urls import reverse



def Is_Admin(func):
    def wrap(request,*args,**kwargs):
        if request.user.is_superuser==True and request.user.is_staff:
            return func(request,*args,**kwargs)
        else:
            messages.error(request,'You need to be a admin to perofrm this operations')
            return reverse('User_Accounts:Login')
    return wrap