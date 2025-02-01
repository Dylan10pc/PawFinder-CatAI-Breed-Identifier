from django import forms

#a class that handles uploading images
class catimageformforupload(forms.Form):
    #handle image uploads
    #allow users to upload images
    image = forms.ImageField()