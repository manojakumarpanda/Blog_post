from django.contrib import messages
from .models import Users
from django.shortcuts import get_object_or_404



class edit_objects(object):

    def get_users(self,id=None):
        user = get_object_or_404(Users, id=id)
        data={'first_name':user.first_name,'last_name':user.last_name,'house_num':user.house_num,
                'countrey':user.countrey,'state':user.state,'dist':user.dist,'city':user.city,'address':user.address,
                'pin_code':user.pin_code,'photo':user.photo}
        return data
        

