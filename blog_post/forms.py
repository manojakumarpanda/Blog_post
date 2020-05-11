from django import forms
from .models import Blog_post,Background,Blog_type


class Blog_post_form(forms.ModelForm):
    class Meta:
        model=Blog_post
        fields=['title','content','catagory','region','image','file_att','published']

#    {% for field in form %}
#     <div class="fieldWrapper">
#         {{ field.errors }}
#         {{ field.label_tag }} {{ field }}
#         {% if field.help_text %}
#         <p class="help">{{ field.help_text|safe }}</p>
#         {% endif %}
#     </div>
# {% endfor %}