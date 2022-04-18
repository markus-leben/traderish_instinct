from django import forms


class CardForm(forms.Form):
    name = forms.CharField(label="",
                           max_length=145,
                           widget= forms.TextInput(attrs={'class': 'input', 'placeholder': 'Schwarmagoyf'}))
