from django.urls import path
from . import views

app_name='Blog_post'
urlpatterns=[
    path('',views.Blog_Post.as_view(),name='Create_blog'),
    path('list/',views.List_blog.as_view(),name='List_blog'),
    path('<str:slug>/detail/',views.Detail_blog.as_view(),name='Detail_blog'),
]