from django import forms

class CatImageUploadForm(forms.Form):
    image = forms.ImageField()