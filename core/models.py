from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to="p_img", blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)
    
    def __str__(self):
        return self.email

class Classe(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Eleve(models.Model):
    nom = models.CharField(max_length=100)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Periode(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Notation(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    periode = models.ForeignKey(Periode, on_delete=models.CASCADE)
    note_attendue = models.FloatField()
    note_obtenue = models.FloatField()

    def __str__(self):
        return f"{self.eleve} - {self.matiere} - {self.periode}"