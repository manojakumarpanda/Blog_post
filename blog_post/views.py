from django.shortcuts import render,HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.views.generic import View
from django.views.generic.edit import UpdateView,DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Blog_post,Background,Blog_type
from .forms import Blog_post_form,Blog_EditForm,Comment_form,Blog_type_form,Upload_background
from .Mixins import Get_objects,Update_Detail_view
from .decorators import Is_Admin



class Home_page(View):
    template_name='blog_post/Home.html'

    def get(self,request,*args,**kwargs):
        context={'tittle':'Index Page','msg':'welcome to index page'}
        return render(request,self.template_name,context=context)


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

@method_decorator(login_required(login_url='accounts/login/'),name='dispatch')
class Detail_blog(View,Update_Detail_view,Get_objects):
    edit_template='blog_post/edit_blog.html'
    detail_template='blog_post/blog_detail.html'
    form_class   = Blog_EditForm

    def get(self,request,slug=None,*args,**kwargs):

        if kwargs.get('view')=='Detail_blog':
            blog_post=self.get_objects_with_id(id=request.user.id,slug=slug)
            updated = self.Update_detail(request, slug=slug)
            context={'tittle':'Detail Blog','blog_post':blog_post}
            return render(request,self.detail_template,context=context)
        else:
            intial_deta = self.get_intial_data(request, slug=slug)
            blog_post   = self.get_objects_with_id(id=request.user.id,slug=slug)
            form=self.form_class(initial=intial_deta,instance=blog_post)
            return render(request,self.edit_template,context={'form':form,'tittle':'Edit_blog'})

    def post(self,request,slug=None,*args,**kwargs):
        form=self.form_class(request.POST,request.FILES or None)
        if form.is_valid():
            try:
                flag=False
                if request.POST.get('published') is not None:
                    flag=True
                data = Blog_post.objects.filter(Q(auther_id__exact=request.user.id) & Q(slug__iexact=slug))
                status=data.update({'title':request.POST.get('title'), 'content':request.POST.get['content'],
                             'catagory':request.POST.get('catagory'),'region':request.POST.get('region'),
                             'image':request.FILES.get('image'),'file_att':request.FILES.get('file_att'),'published':flag})
                # status = data.update(title= request.POST.get('title'), content=request.POST.get['content'],
                #                       catagory= request.POST.get('catagory'), region=request.POST.get('region'),
                #                      image=request.FILES.get('image'), file_att=request.FILES.get('file_att'),
                #                       published= flag)
                if status==1:
                    messages.success(request,'Your data is updated successfully')
                    return reverse('Blog_post:Detail_blog',kwargs={'slug':slug})
                else:
                    messages.error(request, 'Some wrong data entered check again')
                    return reverse('Blog_post:Detail_blog', kwargs={'slug': slug})
            except ValueError:
                messages.error(request, 'Something went wrong try again')
                return render(request,self.edit_template,context={'tittle':'Edit_blog','form':form})
            except:
                messages.error(request, 'Something went wrong try again')
                return reverse('Blog_post:Detail_blog', kwargs={'slug': slug})


@login_required(login_url='accounts/login/')
@Is_Admin
def Background_image(request):
    form=Upload_background()
    if request.method=='POST':
        form=Upload_background(request.POST,request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request,'Background immage is uploaded.')
                return reverse('/')
            except:
                messages.error(request,'You have enter some wrong data ')
                return render(request, 'blog_post/Add_backgorund.html',
                              context={'tittle': 'Add Background', 'form': form})
        else:
            messages.warning(request,form.errors)
            return render(request,'blog_post/Add_backgorund.html',context={'tittle':'Add Background','form':form})
    return render(request,'blog_post/Add_backgorund.html',context={'tittle':'Add Background','form':form})


@login_required(login_url='accounts/login/')
@Is_Admin
def Blog_catagory(request):
    form=Upload_background()
    if request.method=='POST':
        form=Upload_background(request.POST,request.FILES)
        if form.is_valid():
            try:
                Blog_cata=Blog_type(catagory=form.changed_data.get('catagory'),auther=request.user)
                messages.success(request,'Catagory is added.')
                return reverse('/')
            except:
                messages.error(request,'You have enter some wrong data ')
                return render(request, 'blog_post/Add_Catagory.html',
                              context={'tittle': 'Add Catagory', 'form': form})
        else:
            messages.warning(request,form.errors)
            return render(request,'blog_post/Add_Catagory.html',context={'tittle':'Add Background','form':form})
    return render(request,'blog_post/Add_Catagory.html',context={'tittle':'Add Background','form':form})


