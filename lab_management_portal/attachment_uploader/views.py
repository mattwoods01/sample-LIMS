from django.shortcuts import render

def index(request):
    return render(request, 'attachment_uploader.html')