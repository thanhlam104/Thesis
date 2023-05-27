from django.db import models
from . import neo4jRec as neorec
# Create your models here.

from django.contrib.auth.models import User
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    uri = models.TextField()
    database_name = models.TextField()
    username = models.TextField(blank=True)
    password = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank= True)
    def __str__(self):
        return f"Project: {self.name},\n Created at: {self.date}"
    
    def recommendByKNN(self,num):
        # if self.username != None and self.password != None:
        #     auth = (self.username,self.password)
        #     driver = neorec.Recommender(self.uri,auth)
        # else:
        driver = neorec.Recommender(self.uri)
        result = driver.byKNN(num)

        return result

class FileObject(models.Model):
    display_name = models.CharField(max_length=255,default=None)
    file = models.FileField(upload_to="files")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    
class ColumnObject(models.Model):
    display_name = models.CharField(max_length=100,default=None)
    file = models.ForeignKey(FileObject, on_delete=models.CASCADE)