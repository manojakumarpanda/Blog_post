from django.contrib import admin
from .models import Blog_type,Blog_post,Background,Blog_Views,Comment

# Register your models here.
class Blog_type_Admin(admin.ModelAdmin):
    list_display = ['id','catagory']

admin.site.register(Blog_type,Blog_type_Admin)

class Blog_Admin(admin.ModelAdmin):
    list_display = ['title','slug']
    list_filter = ['title','slug']
    # list_display_links = []

admin.site.register(Blog_post,Blog_Admin)

class Background_Admin(admin.ModelAdmin):
    list_display = ['id',]
admin.site.register(Background,Background_Admin)

class Comment_Admin(admin.ModelAdmin):
    list_display = ['blog_id','replys']
    list_filter =  ['blog_id','comments','user']
admin.site.register(Comment,Comment_Admin)

class Last_View_Admin(admin.ModelAdmin):
    list_display = ['id','view_at']
    list_filter = ['id']

admin.site.register(Blog_Views,Last_View_Admin)