from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse

def index(request: HttpRequest):
    return redirect('https://pku.edu.cn')