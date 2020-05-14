from .models import Blog_post,Blog_type,Background,Blog_Views
from django.shortcuts import get_object_or_404,HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q


class Get_objects(object):

    def get_objects_with_id(self,id=None,slug=None):
        try:
            data=get_object_or_404(Blog_post,id or slug)
            return data
        except Exception as e:
            return reverse('Blog_post:Detail_post',kwargs={'slug':slug})

    def intial_data(self,id=None,slug=None):
        try:
            data=Blog_post.objects.filter(Q(auther_id__exact=id) or Q(slug__iexact=slug))
            return data[0]
        except Exception as e:
            return reverse('Blog_post:Detail_post',kwargs={'slug':slug})

    def get_all(self,id=None):
        try:
            if id:
                blogs=Blog_post.objects.filter(Q(published=True)&Q(auther_id__exact=id))
                all_blogs = Blog_post.objects.filter(published=False)
                blogs_dict={'blogs':blogs,'all_blogs':all_blogs}
                return blogs_dict
            else:
                blogs = Blog_post.objects.filter(published=False)
                return blogs

        except:
            return None

class Update_Detail_view(object):

    def Update_detail(self,request,slug=None):
        try:
            blog = Blog_post.objects.get(slug=slug)
            try:
                updated=Blog_Views.objects.get(blog_view_id=blog)
                updated.num_view=updated.num_view+1
                updated.save()
                return updated
            except Blog_Views.DoesNotExist:
                created = Blog_Views.objects.create(user=request.user, blog_view_id=blog, num_view=+1)
                return created
        except Blog_post.DoesNotExist:
            return reverse('Blog_post:Detail_blog')

    def get_intial_data(self,request,slug=None):
        intial_data={}
        data=Blog_post.objects.filter(Q(auther_id__exact=request.user.id) & Q(slug__iexact=slug)).values()

        for k,v in data[0].items():
            intial_data[k]=v
        return intial_data


