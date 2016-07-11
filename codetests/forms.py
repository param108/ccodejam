from django import forms
import datetime
class CodeTestForm(forms.Form):
  testname=forms.CharField(max_length=50,label="Test Name")
  datetimefield = forms.DateTimeField(initial=datetime.datetime.now, label="Date of the Test")
  duration = forms.IntegerField(initial=3,label="duration in hours")

class CodeQnForm(forms.Form):
  title=forms.CharField(max_length=50, label="Question Title")
  description=forms.Textarea()
  smalllimits=forms.Textarea(label="small problem set limits", help_text="limits for the variables in the small problem set")
  largelimits=forms.Textarea(label="large problem set limits", help_text="limits for the variables in the large problem set")
  inputexample=forms.Textarea(label="sample input")
  outputexample=forms.Textarea(label="sample output", help_text="This should be the answer for the sample input")
  utimesmall=forms.IntegerField(label="small solution upload time(minutes)", help_text="This is the time the user has to upload his solution file after downloading the small problem set")
  utimelarge=forms.IntegerField(label="large solution upload time(minutes)", help_text="This is the time the user has to upload his solution file after downloading the large problem set")
  difficulty=forms.IntegerField(label="difficulty 0-easiest, 5-very hard")
  smallscript=forms.FileField(label="script to generate small problem set", 
                              allow_empty_file=False)
  largescript=forms.FileField(label="script to generate large problem set",
                              allow_empty_file=False)
