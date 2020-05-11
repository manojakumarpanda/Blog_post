from django.shortcuts import render,HttpResponse
from django.urls import reverse
from django.views.generic import View
from django.views.generic.edit import UpdateView,DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Blog_post
from .forms import Blog_post_form
from .Mixins import Get_objects,Update_Detail_view

# Create your views here.


@method_decorator(login_required(login_url='accounts/login/'),name='dispatch')
class Blog_Post(View):
    template_name   ='blog_post/New_blog.html'
    form_class      = Blog_post_form()

    def get(self,request,*args,**kwargs):
        context={'tittle':'Add New blog','form':self.form_class}
        return render(request,self.template_name,context=context)

    def post(self,request,*args,**kwargs):
        form=Blog_post_form()
        try:
            form = Blog_post_form(request.POST, request.FILES)
            if form.is_valid():
                blog = Blog_post(auther_id=request.user.id, title=request.POST['title'],
                                 content=request.POST['content'],
                                 catagory_id=request.POST['catagory']
                                 , region=request.POST['region'], image=request.FILES.get('image'),
                                 )
                if request.POST.get('published') is not None:
                    blog.published = True
                    blog.save()
                    return HttpResponse('saved')
                else:
                    blog.published = False
                    blog.save()
                    return HttpResponse('not saved')
            else:
                return render(request,self.template_name,context={'tittle':'Add New blog','form':form,'error':form.errors})
        except TypeError:
            messages.error(request,'You have enter some invalid data')
            return render(request,self.template_name,context={'tittle':'Add New blog','form':form})
        except OverflowError:
            messages.error(request, 'You have enter More data then it expected')
            return render(request, self.template_name, context={'tittle': 'Add New blog', 'form': form})
        except:
            messages.error(request,'There is something went wrong with the server please try agin')
            return render(request,self.template_name,context={'tittle': 'Add New blog', 'form': form})

class List_blog(View,Get_objects):

    def get(self,request,*args,**kwargs):
        context={}
        if request.user.is_authenticated:
            user_blogs=self.get_all(id=request.user.id).get('blogs')
            all_blogs=self.get_all(id=request.user.id).get('all_blogs')
            context={'tittle':'Blog List','user_blogs':user_blogs,'all_blogs':all_blogs}
            return render(request, 'blog_post/Blog_List.html', context=context)
        else:
            all_blogs=self.get_all()
            print(all_blogs)
            context={'tittle':'Blog List','all_blogs':all_blogs}
            return render(request,'blog_post/Blog_List.html',context=context)
from .models import Blog_Views
class Detail_blog(View,Update_Detail_view):

    def get(self,request,slug=None,*args,**kwargs):
        data=Blog_post.objects.get(slug=slug)
        updated=self.Update_detail(request,data.blog_id)
        print(updated.num_view)
        return HttpResponse('updated.num_view')
