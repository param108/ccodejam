from django import forms

class VoteForm(forms.Form):
  Choice = forms.ChoiceField(label="Audience Choice", 
             widget=forms.RadioSelect, required=True)
  def setup_choices(self, choicelist):
    self.fields['Choice'].choices = choicelist 
