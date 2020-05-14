from django.urls import path
from . import views

app_name='Blog_post'
urlpatterns=[
    path('',views.Home_page.as_view(),name='Home_Page'),
    path('blog-post/',views.Blog_Post.as_view(),name='Create_blog'),
    path('list/',views.List_blog.as_view(),name='List_blog'),
    path('<str:slug>/detail/',views.Detail_blog.as_view(),kwargs={'view':'Detail_page'},name='Detail_blog'),
    path('<str:slug>/edit/',views.Detail_blog.as_view(),kwargs={'view':'Edit_page'},name='Edit_blog'),
]