from dataclasses import fields
from django import forms
from .models import Book
from django.core.validators import validate_image_file_extension

class BookCoverForm(forms.Form):
    front_cover = forms.ImageField(label='Front cover', required=False, validators=[validate_image_file_extension])
    back_cover = forms.ImageField(label='Back cover', required=False)
    

class FrontCoverForm(forms.Form):
    front_cover = forms.ImageField(required=False)


class BackCoverForm(forms.Form):
    back_cover = forms.ImageField(label='Back_cover', required=False)


class RelatedForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['related', ]

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = "__all__"


class BookStatusForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['status', ]
    

