from django import forms
from PIL import Image

MAX_FILE_SIZE = 1e7

class SendPhotoForm(forms.Form):
    image_file = forms.ImageField(label="Zdjęcie", required=True)
    is_private = forms.BooleanField(label="Czy zdjęcie ma być prywatne?", required=False)

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
    review = forms.CharField(widget=forms.Textarea, label="Właściciel zdjęcia chce twojej pomocy w weryfikacji zwierzęcia:")
