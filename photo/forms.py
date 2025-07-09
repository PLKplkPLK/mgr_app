from django import forms
from PIL import Image

MAX_FILE_SIZE = 1e7

class SendPhotoForm(forms.Form):
    image_file = forms.ImageField(
        label="",
        required=True,
        widget=forms.ClearableFileInput()
    )
    is_private = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )

    def clean_image_file(self):
        image = self.cleaned_data.get('image_file')
        if image:
            # check size of a file
            if image.size > MAX_FILE_SIZE:
                raise forms.ValidationError("Plik jest za duży. Maksymalnie 10 MB")

            # check type of a file
            try:
                img = Image.open(image)
                img.verify()
            except:
                raise forms.ValidationError("Podany plik nie jest odpowiednim plikiem obrazu")
            
            image.seek(0)

        return image

class PostReviewForm(forms.Form):
    review = forms.CharField(
        widget=forms.TextInput(attrs={'rows': 2, 'placeholder': 'Komentarz'}),
        label=""
    )
