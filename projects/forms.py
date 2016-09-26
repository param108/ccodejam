from django import forms
from projects.models import(Batch)
# The forms only have the file submit button
class BatchForm(forms.Form):
  batchname=forms.CharField(max_length=20, label="Batch Name")
  numreadouts=forms.IntegerField(label="Number of readouts")
  start = forms.DateField(label="Date of first readout")
  interval = forms.IntegerField(label="Number of weeks between readouts")
  inputopen = forms.BooleanField(required = False, label="Can mentors still input project milestones?")
  showdashboard= forms.BooleanField(required = False, label="Can mentors see the dashboard?")


class ProjectForm(forms.Form):
  batch=forms.ChoiceField(choices=[])
  title=forms.CharField(max_length=50)
  def __init__(self, *args, **kwargs):
    super(ProjectForm, self).__init__(*args, **kwargs)
    self.fields["batch"].choices = [(x.batchname,str(x.id)) for x in Batch.objects.all()]

class MemberForm(forms.Form):
  username=forms.CharField(max_length=30, label="Username")
  projectid=forms.IntegerField()

class LineItemForm(forms.Form):
  milestoneid= forms.IntegerField()
  details= forms.CharField(max_length=300, widget=forms.Textarea)

class JudgeForm(forms.Form):
  username=forms.CharField(max_length=30, label="Username")


