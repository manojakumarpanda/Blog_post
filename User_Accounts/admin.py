from django.contrib import admin
from .models import Users,States,Districts,Cities


class User_Admin(admin.ModelAdmin):
    list_display = ['id','full_name','email']

class State_Admin(admin.ModelAdmin):
    list_display = ['id','state_name']

class District_Admin(admin.ModelAdmin):
    list_display = ['id', 'district_name',]

class city_Admin(admin.ModelAdmin):
    list_display = ['id', 'city_name']

admin.site.register(Users,User_Admin)
admin.site.register(States,State_Admin)
admin.site.register(Districts,District_Admin)
admin.site.register(Cities,city_Admin)

# Register your models here.
