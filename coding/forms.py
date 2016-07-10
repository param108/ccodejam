from django import forms

# The forms only have the file submit button
# the hidden data will be the question's primary key and the random
# used to generate the problem set.
class smallsolution(forms.Form):
  solution = forms.FileField(required=False, allow_empty_file=False)

class bigsolution
  solution = forms.FileField(required=False, allow_empty_file=False)
