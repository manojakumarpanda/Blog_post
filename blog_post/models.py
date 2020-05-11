from django.db import models
from django.urls import reverse

from User_Accounts.models import Users
from django.dispatch import receiver
from django.db.models.signals import pre_save,pre_delete
from django.utils import timezone
from django.utils.text import slugify
import string
import random



def image_storage(instance,filename):
    title=instance.title[:10]
    path='blog/images/%s-%s-%s'%(instance.auther.username,title,filename)
    return path

def file_storage(instance,filename):
    path='blog/files/%s-%s'%(instance.title[:7:],filename)
    return path

class Blog_type(models.Model):
    auther      = models.ForeignKey(Users,on_delete=models.CASCADE,default='e628e007347043aea0afad515a45d7bd')
    catagory    = models.CharField(max_length=20,blank=True,null=True,unique=True)

    def __str__(self):
        return self.catagory

class Blog_post(models.Model):
    blog_id     = models.AutoField(primary_key=True,blank=False,null=False,unique=True)
    auther      = models.ForeignKey(Users,on_delete=models.CASCADE,blank=False,null=False,verbose_name='Created by')
    #auther       = models.ManyToManyField(Users,on_delete=models.CASCADE,blank=False,null=False,verbose_name='Created by')
    title       = models.CharField(max_length=100,blank=False,null=False,verbose_name='Blog Title')
    content     = models.TextField(max_length=10000,blank=True,null=True,verbose_name='Blog content')
    catagory    = models.ForeignKey(Blog_type,on_delete=models.CASCADE)
    region      = models.CharField(max_length=20,null=True,blank=True)
    slug        = models.SlugField(max_length=100,verbose_name='Link Name',blank=False,null=False)
    image       = models.ImageField(upload_to=image_storage,blank=True,null=True)
    file_att    = models.FileField(blank=True,null=True,upload_to=file_storage)
    url_author  = models.URLField(null=True,blank=True,verbose_name='Author url')
    published   = models.BooleanField(default=False,verbose_name='status')

    created_on  = models.DateTimeField(auto_created=True,auto_now_add=timezone.now(),auto_now=False)
    updated_on  = models.DateTimeField(auto_now_add=False,auto_now=timezone.now())
    last_seen   = models.DateTimeField(auto_created=False,auto_now=False,auto_now_add=False,blank=True,null=True)

    def __str__(self):
        return self.title[:10]

    class Meta:
        db_table='Blogs'
        ordering=['-created_on']

    @property
    def status(self):
        if self.published==True:
            return Blog_post

    def get_absolute_url(self):
        return reverse('Blog_post:Detail_blog',kwargs={'slug':self.slug})

    # def get_Update_url(self):
    #     pass
    # def get_delete_url(self):
    #     pass

def uniq_slug_gen(instance,new_slug=None):
    slug=slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    quary=Blog_post.objects.filter(slug=slug)
    exist=quary.exists()
    if exist:
        random_str=''
        for i in range(7):
            random_str+=random.choice(string.ascii_letters)
        new_slug= '{}-{}'.format(slug,random_str)
        return uniq_slug_gen(instance,new_slug=new_slug)
    return slug

@receiver(pre_save,sender=Blog_post)
def slug_generation(instance,*args,**kwargs):
    if not instance.slug:
        instance.slug=uniq_slug_gen(instance)

class Blog_Views(models.Model):
    blog_view   = models.ForeignKey(Blog_post,on_delete=models.CASCADE,verbose_name='Viewed_by')
    user        = models.ForeignKey(Users,on_delete=models.SET_NULL,default='',null=True)
    num_view    = models.IntegerField(default=0)
    view_at     = models.DateTimeField(auto_now=timezone.now(),auto_now_add=False)

    def __str__(self):
        return self.blog_view.content

    class Meta:
        db_table='Blog_View'
        ordering=['view_at']

class Comment(models.Model):
    blog_id     = models.AutoField(primary_key=True)
    blog_post   = models.ForeignKey(Blog_post, on_delete=models.CASCADE, verbose_name='To blog')
    user        = models.ForeignKey(Users, on_delete=models.CASCADE,verbose_name='comment by')
    comments    = models.CharField(max_length=300,blank=False,null=False)
    likes       = models.IntegerField(default=0,verbose_name='likes')
    shares      = models.IntegerField(default=0,verbose_name='shard')
    parent      = models.ForeignKey('self',on_delete=models.CASCADE,verbose_name='Replayed to',blank=True,null=True)
    comented_on = models.DateTimeField(auto_now=False, auto_now_add=timezone.now())

    def __str__(self):
        return self.comments[:10] +' posted by '+self.user.username

    @property
    def replys(self):
        return self.comment_set.filter(parent_id=self.blog_id)

    class Meta:
        db_table='Comments'
        ordering=['comented_on']

class Background(models.Model):
    back_ground = models.ImageField(blank=True,null=True,upload_to='background')
    catagory    = models.CharField(max_length=10,blank=True,null=True)

    uploaded_on = models.DateTimeField(auto_now_add=timezone.now(),auto_now=False)

    def __str__(self):
        return self.catagory

    class Meta:
        db_table='Background_img'