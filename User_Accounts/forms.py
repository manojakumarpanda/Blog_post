from django import forms
from .models import Users


class Login(forms.Form):
    email = forms.CharField(max_length=50, label='Email', widget=forms.TextInput(
        attrs={
            'placeholder': ' Username/email '
        }
    ))
    password = forms.CharField(max_length=50,
                               label='password',
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': ' Enter password Here'}
                               )

                               )


class Users_Form(forms.ModelForm):
    # def clean_city(self):
    #     if self.changed_data['city']==None:
    #         data=self.cleaned_data['city']
    #         data.city_name='Berhampur Municipal Corporation'
    #     return data

    class Meta:
        model   =Users
        fields=['username','email','password','first_name',
                'last_name','house_num','countrey','state',
                'dist','city','house_num','address','pin_code','photo']


class User_Edit(forms.ModelForm):
    class Meta:
        model=Users
        fields=['first_name','last_name','house_num',
                'countrey','state','dist','city','house_num','address',
                'pin_code','photo']