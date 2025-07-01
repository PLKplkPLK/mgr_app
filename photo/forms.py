from django import forms

MAX_FILE_SIZE = 1e7

class SendPhotoForm(forms.Form):
    image_file = forms.ImageField(label="Zdjęcie", required=True)
    is_private = forms.BooleanField(label="Czy zdjęcie ma być prywatne?", required=False)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > MAX_FILE_SIZE:
                raise forms.ValidationError("Plik jest za duży. Maksymalnie 10 MB")
        return image
