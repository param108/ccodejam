from django import forms

class admin_user_form(forms.Form):
    error_css_class = 'error'
    username=forms.CharField(max_length=90)

