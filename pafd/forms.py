from django import forms
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)

class StudentForm(forms.Form):
    school_id = forms.CharField(label='学号', max_length=11, min_length=11)
    password = forms.CharField(label='密码')
    name = forms.CharField(label='姓名')
    email = forms.EmailField(
        label='邮箱', required=False, 
        widget=forms.TextInput(attrs={'placeholder': '可选，默认使用学号邮箱'})
        )
    
    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     domain = email[email.find('@')+1:]
    #     whitelist = ['fudan.edu.cn']
    #     if not domain in whitelist:
    #         raise ValidationError("Invalid email !")
    #     else:
    #         return email
    

