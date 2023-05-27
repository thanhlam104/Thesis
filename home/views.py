from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return render(request, 'pages/home.html')
def error404(request, exception):
   context = {}
   return render(request,'pages/error.html', context)

def error500(request):
   context = {}
   return render(request,'pages/error.html', context)
def new(request):
   return render(request, 'pages/new.html')

from .forms import RegistrationForm
from django.http import HttpResponseRedirect 

def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    return render(request, 'registration/register.html', {'form': form})

from .forms import CSVUploadForm
import csv

def dataImporter(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            csv_data = csv_file.read().decode('utf-8')
            # Process the CSV data as needed
            # Example: Parse CSV data using csv module
            reader = csv.reader(csv_data.splitlines())
            header = next(reader)
            print(header)
            return render(request, 'pages/dataImporter.html',{'form': form})
    else:
        form = CSVUploadForm()
    return render(request, 'pages/dataImporter.html', {'form': form})