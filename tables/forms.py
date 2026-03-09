from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Image
from datetime import date
from dal import autocomplete


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = [
            'author',
            'title',
            'description',
            'image',
            'place',
            'year',
            'category',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': _('Enter the image title...')
                },
            ),
            'image': forms.ClearableFileInput(),
            'description': forms.Textarea(
                attrs={
                    'placeholder': _('Enter a description...'),
                    'class': 'form-control',
                    'rows': 4,
                },
            ),

            'author': autocomplete.ModelSelect2Multiple(
                url='images:author-autocomplete',
                attrs={
                    'data-placeholder': _('Write names of image authors...')
                },
            ),
            'place': autocomplete.ModelSelect2(
                url='images:place-autocomplete',
                attrs={
                    'data-placeholder': _('Write the place of image capture...')
                },
            ),
            'year': autocomplete.ModelSelect2(
                url='images:year-autocomplete',
                attrs={
                    'data-placeholder': _('Write the capture year ...')
                },
            ),
            'category': autocomplete.ModelSelect2Multiple(
                url='images:category-autocomplete',
                attrs={
                    'data-placeholder': _('Write the image categories...')
                },
            ),
        }

        labels = {
            'author': _('Author'),
            'title': _('Title'),
            'image': _('Image'),
            'description': _('Description'),
            'place': _('Place'),
            'year': _('Year'),
            'category': _('Category')
        }

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year:
            year_value = year.name
            if year_value > date.today().year or year_value < 0:
                raise forms.ValidationError(_("Not a valid year"))
        return year
