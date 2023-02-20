from django import forms
from .models import Card


class AddCardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('serial', 'number', 'start_activate_date', 'finish_date', 'card_status', 'discount')


class AddSomeCards(forms.Form):
    serial = forms.CharField(max_length=2,
                             widget=forms.TextInput(attrs={
                                 'type': 'text',
                                 'class': 'form-control',
                             }))
    count = forms.CharField(widget=forms.TextInput(attrs={
                                 'type': 'text',
                                 'class': 'form-control',
                             }))
    activated = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
                                 'class': 'form-control',
                             }))
    deactivated = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
                                 'class': 'form-control',
                             }))
