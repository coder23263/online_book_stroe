from django.shortcuts import reverse, redirect, render
from django.http import HttpResponse




def home(request):
    return render(request, 'home.html')

