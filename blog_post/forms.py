from django import forms
from .models import Blog_post,Background,Blog_type,Comment


class Blog_post_form(forms.ModelForm):
    class Meta:
        model=Blog_post
        fields=['title','content','catagory','region','image','file_att','published']

class Blog_EditForm(forms.ModelForm):
    class Meta:
        model=Blog_post
        fields=['title','content','catagory','region','image','file_att','published']

class Upload_background(forms.ModelForm):
    class Meta:
        model=Background
        exclude=['uploaded_on']

class Blog_type_form(forms.ModelForm):
    class Meta:
        model=Blog_type
        fields=['catagory']

class Comment_form(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['comments']

#    {% for field in form %}
#     <div class="fieldWrapper">
#         {{ field.errors }}
#         {{ field.label_tag }} {{ field }}
#         {% if field.help_text %}
#         <p class="help">{{ field.help_text|safe }}</p>
#         {% endif %}
#     </div>
# {% endfor %}