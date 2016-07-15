from django import forms

# The forms only have the file submit button
class Solution(forms.Form):
  solution = forms.FileField(required=True, allow_empty_file=False)
  code = forms.FileField(required=True, allow_empty_file=False)

