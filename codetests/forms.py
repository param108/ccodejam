from django import forms
import datetime
class CodeTestForm(forms.Form):
  testname=forms.CharField(max_length=50,label="Test Name")
  datetimefield = forms.DateTimeField(initial=datetime.datetime.now, label="Date of the Test")
  duration = forms.IntegerField(initial=3,label="duration in hours")

class CodeQnForm(forms.Form):
  title=forms.CharField(max_length=50, label="Question Title")
  description=forms.CharField(widget=forms.Textarea, label="Description")
  smalllimits=forms.CharField(label="small problem set limits", 
                              help_text="limits for the variables in the small problem set",
                              widget=forms.Textarea)
  largelimits=forms.CharField(required=False,
                              label="large problem set limits", 
                              help_text="limits for the variables in the large problem set",
                              widget=forms.Textarea)
  inputexample=forms.CharField(label="sample input",
                              widget=forms.Textarea)
  outputexample=forms.CharField(label="sample output", 
                                help_text="This should be the answer for the sample input",
                                widget=forms.Textarea)
  utimesmall=forms.IntegerField(label="small solution upload time(minutes)", 
    help_text="This is the time the user has to upload his solution file after downloading the small problem set")
  utimelarge=forms.IntegerField(required=False,
                                label="large solution upload time(minutes)", 
    help_text="This is the time the user has to upload his solution file after downloading the large problem set")
  difficulty=forms.IntegerField(label="difficulty 0-easiest, 5-very hard")
  smallscript=forms.FileField(required=False, label="script to generate small problem set", 
                              allow_empty_file=False)
  largescript=forms.FileField(required=False, label="script to generate large problem set",
                              allow_empty_file=False)
  need2questions=forms.BooleanField(required=False, 
    label="Does the question have a large question set?") 
  needdos2unix=forms.BooleanField(required=False,
    label="Does the answer need to pass through dos2unix?") 
  usesuploadedqns=forms.BooleanField(required=False,
    label="Will you upload the question sets yourself? (you can specify scripts otherwise)") 
  needtranslator=forms.BooleanField(required=False,
    label="Does the user submitted answer set need to pass through a translator script before comparison with the solution set")
  directupload=forms.FileField(required=False, label="a .tgz archive of qns and answers", help_text="archive should have 2 directories 'large' and 'small'. These directories should have numbered qn and ans files 1q.txt 1a.txt 2q.txt 2a.txt ... 1q.txt is the question file for 1a.txt")
  translatorscript=forms.FileField(required=False, label="script to translate the submitted answer set before comparison with the solution set")
  largescore=forms.IntegerField(required=False, label="score to give for the large question")
  smallscore=forms.IntegerField(label="score to give for the small question")
  language=forms.ChoiceField(label="Which language should the user write in?",
                             choices=(("any","any"),
                                      ("C","C"),
                                      ("Python","Python")), help_text="C,Python, any") 


class GenerateForm(forms.Form):
  numqns=forms.IntegerField(label="Number of qn-answer sets you want to generate")
