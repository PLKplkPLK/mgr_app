from django.shortcuts import render#, redirect
from django.contrib.auth.decorators import login_required

app_name = 'gallery'

def browse(request):
    """
    View for browsing all images of other users
    """
    context = {"img1_url": "www.images.com/image1.jpg"}
    return render(request, "browse.html", context)

@login_required
def browse_my(request):
    """
    View for browsing photos of the user
    """

    context = {"img1_url_mine": "www.images.com/image2.jpg"}
    # return HttpResponseRedirect(reverse("photo:upload", args=(something,)))
    return render(request, "browse.html", context)
