from django.shortcuts import render
from .models import *
from .forms import *
import csv
from django.http import HttpResponseRedirect 
# Create your views here.

def project(request, name):
    project = Project.objects.get(name = name)
    recommendation = project.recommendByKNN(10).to_dict(orient='records')
    node_create_form = NodeCreateForm(project=project)
    for item in recommendation:
        print(item)
    files = project.fileobject_set.all()

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            file_instance = FileObject(file=csv_file, project=project, display_name=csv_file.name)
            file_instance.save()
            reader = csv.reader(csv_file.read().decode('utf-8-sig').splitlines())
            header = []
            for row in reader:
                header = row
                break
            for col in header:
                column_instance = ColumnObject(display_name=col, file=file_instance) 
                column_instance.save()
            # Process the CSV data as needed
            # Example: Parse CSV data using csv module
            # reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            # header = next(reader)
            # print(header)
            files = project.fileobject_set.all()
            Data = {'project': Project.objects.get(name = name),
                    'recommendation': recommendation,
                    'form':form,
                    'files':files,
                    'node_create_form':node_create_form}
            return render(request, 'project.html', Data)
    else:
        form = CSVUploadForm()
        Data = {'project': Project.objects.get(name = name),
                'recommendation': recommendation,
                'form':form,
                'files':files,
                'node_create_form':node_create_form}
        return render(request, 'project.html', Data)    

def create_project(request):
    user = request.user
    if request.method == 'POST':
        form = ProjectModelForm(request.POST)
        file_form = FileModelForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        if form.is_valid() and file_form.is_valid():
            project_instance = form.save(commit=False)
            project_instance.user = user
            project_instance.save()
            for f in files:
                file_instance = FileObject(file=f, project=project_instance, display_name=f.name)
                file_instance.save()
                reader = csv.reader(f.read().decode('utf-8-sig').splitlines())
                header = []
                for row in reader:
                    header = row
                    break
                for col in header:
                    column_instance = ColumnObject(display_name=col, file=file_instance) 
                    column_instance.save()
        return HttpResponseRedirect(f'/recommender/test/{project_instance.name}')
                
    else:
        form = ProjectModelForm()
        file_form = FileModelForm()
        Data = {'form': form, 'file_form':file_form}
        return render(request, 'create_project.html', Data)
    
def clear_files(request):
    user = request.user
    projects = user.project_set.all()
    for p in projects:
        files = p.fileobject_set.all()
        for f in files:
            f.delete()
    return HttpResponseRedirect('/')