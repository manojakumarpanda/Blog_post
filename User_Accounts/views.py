from django.shortcuts import render,HttpResponseRedirect,HttpResponse,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.views.generic import View
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Users
from django.utils.decorators import method_decorator
from .Mixins import edit_objects
from .forms import Users_Form,Login,User_Edit


class Home(View):

    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            data=get_object_or_404(Users,id=request.user.id)
            print(request.user.username)
            return render(request,'Accounts/Home.html',context={'tittle':'Login Home','user':data})
        else:
            data=request.user
            print(data)
            return render(request, 'Accounts/Home.html', context={'tittle': 'Login Home', 'user': data})

class Create_user(View):
    form_class = Users_Form
    template_name = 'Accounts/Signup.html'

    def get(self, request, *args, **kwargs):
        template=self.template_name
        form=self.form_class
        context={'tittle':'Signup','form':form}
        return render(request,template,context=context)

    def post(self, request, *args, **kwargs):
        template = self.template_name
        form = self.form_class(request.POST , request.FILES)
        try:
            if form.is_valid():
                print(request.POST['username'])
                user = Users(username=request.POST['username'], email=request.POST['email']
                             , first_name=request.POST['first_name'], last_name=request.POST['last_name']
                             , house_num=request.POST['house_num'], address=request.POST['address'],
                             pin_code=request.POST['pin_code'], countrey_id=request.POST['countrey'],
                             state_id=request.POST['state'], dist_id=request.POST['dist'], city_id=request.POST['city'],
                             photo=request.FILES['photo'])
                user.set_password(raw_password=request.POST['password'])
                user_created=user.save()
                user=authenticate(email=request.POST['email'],password=request.POST['password'])
                if user is not None:
                    if user.is_active==True:
                        logedin_user=login(request,user=user)
                        messages.success(request,user_created,'The user successfully')
                        return HttpResponseRedirect('/')
            else:
                print(form.errors)
                messages.error(request, form.errors)
                return HttpResponseRedirect('/')

        except TypeError:
            messages.error(request,'You have enterd some wrong data please check again')
            return render(request,template,{'tittle':'Signup','form':form})
        except FileExistsError:
            messages.error(request,'Some problem with the server please try again latter')
            return HttpResponseRedirect('/')
        except:
            messages.error(request, 'Something went please try again latter')
            return HttpResponseRedirect('/')

@method_decorator(login_required(login_url='/lgoin'),name='dispatch')
class Detail_profile(View):
    template_name   ='Accounts/profile.html'

    def get(self,request,uuid=None,*args,**kwargs):
        try:
            template=self.template_name
            user=get_object_or_404(Users,id=uuid)
            return render(request,template,context={'tittle':'Profile','user':user})
        except Users.DoesNotExist:
            messages.error(request,'NO such user exist with this request')
            return HttpResponseRedirect('/')
        except :
            messages.error(request,'Something went wrong please try again')
            return HttpResponseRedirect('/')

@method_decorator(login_required(login_url='login/'),name='dispatch')
class Edit_profile(UpdateView):
    template_name   ='Accounts/edit_profile.html'
    model           = Users
    fields          = ['first_name','last_name','house_num',
                'countrey','state','dist','city','house_num','address',
                'pin_code','photo']


class Login_User(View):
    form_class=Login
    template_name='Accounts/Login.html'

    def get(self,request,*args,**kwargs):
        context ={'tittle':'Login form','form':self.form_class}
        template=self.template_name
        return render(request,template,context=context)

    def post(self,request,*args,**kwargs):
        form    =self.form_class(request.POST or None)
        context = {'title': 'Login', 'form': form}
        template=self.template_name
        try:
            if form.is_valid():
                username=form.cleaned_data['email']
                user =authenticate(email=username,
                                  password=form.cleaned_data['password'])
                print(user)
                if user is not None:
                    print(request.POST['email'], form.cleaned_data['password'])
                    if user.is_active:
                        login(request,user)
                        return HttpResponseRedirect('/')
            return render(request,template,context=context)
        except TypeError:
            messages.error(request, 'You have enterd some wrong data please check again')
            return HttpResponseRedirect('Login')
        except TimeoutError:
            messages.error(request, 'Some problem with the server please try again latter')
            return HttpResponseRedirect('/')
        except:
            messages.error(request, 'Something went please try again latter')
            return HttpResponseRedirect('/')


@login_required(login_url='/login/')
def Logout_User(request):
    logout(request)
    return HttpResponseRedirect('/')