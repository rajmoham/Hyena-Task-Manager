from django.shortcuts import render

def confirm(request):
    return render(request, 'confirm.html')