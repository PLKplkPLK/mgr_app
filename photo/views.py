from django.shortcuts import render

def upload(request):
    """
    A site to upload a photo
    """
    return render(request, "upload.html")

def classify_image(request):
    """
    Site user's redirected to after uploading a photo.
    The view redirects user classifies an image and shows the results
    """
    # TODO image upload, classification and redirection to the output
    return render(request, "upload.html")
