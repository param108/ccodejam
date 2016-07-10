from django import forms
import datetime
class CodeTestForm(forms.Form):
  testname=forms.CharField(max_length=50,label="Test Name")
  datetimefield = forms.DateTimeField(initial=datetime.datetime.now, label="Date of the Test")
  duration = forms.IntegerField(initial=3,label="duration in hours")
