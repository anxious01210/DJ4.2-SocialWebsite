from django import forms
from .models import Image
from django.utils.text import slugify
from django.core.files.base import ContentFile
import requests

class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description', ]
        widgets = {
            'url': forms.HiddenInput,
        }
    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given url does not match valid image extensions.')
        return url
    def save(self, force_insert=False, force_update=False, commit=True): # overridden the save() method, keeping the parameters required by ModelForm.
        image = super().save(commit=False) # A new image instance is created by calling the save() method of the form with commit=False.
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        # Dowload image from the given URL
        response = requests.get(image_url) # The Requests Python library is used to download the image by sending an HTTP GET request using the image URL. The response is stored in the response object.
        # The save() method of the image field is called, passing it a ContentFile object that is instantiated with the downloaded file content. In this way, the file is saved to the media directory of
        # the project. The save=False parameter is passed to avoid saving the object to the database yet.
        image.image.save(image_name, ContentFile(response.content), save=False)
        # To maintain the same behavior as the original save() method of the model form, the form is only saved to the database if the commit parameter is True.
        if commit:
            image.save()
        return image