from django.shortcuts import render

# Create your views here.
from .models import Thread, Post
from .forms import 
@login_required
def create_thread(request):
    newthread= Thread()