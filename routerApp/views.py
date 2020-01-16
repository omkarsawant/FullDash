from django.shortcuts import render
from .models import Router4331
from .forms import Router4331Form


def test_view(request, *args, **kwargs):
    obj = Router4331.objects.get()
    kvpairs = {
        "items": [1, 2, 3],
        "name": "test"}
    # most logic in view
    return render(request, "test.html", context=kvpairs)
