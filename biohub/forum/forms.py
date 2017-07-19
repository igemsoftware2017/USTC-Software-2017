""" 
Details about ModelForms are located at https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/
"""
from django import forms
class PostForm(forms.ModelForm):
    class Meta():
        model=Post
        fields = ['thread','content','author','update_time','pub_time']
        