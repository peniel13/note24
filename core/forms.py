from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Notation, Classe, Periode,Eleve,Matiere

class RegisterForm(UserCreationForm):
    email= forms.CharField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder":"Enter email adress"}))
    username= forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder":"Enter username"}))
    password1= forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder":"Enter password"}))
    password2= forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder":"confirm password"}))
    class Meta:
        model = get_user_model()
        fields = ["email","username","password1","password2"]

class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter firstname"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter lastname"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter username"}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"class":"form-control", "placeholder": "Enter email address"}))
    profile_pic = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control", "placeholder": "Upload image"}))
    address = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter address"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter phone"}))
    bio = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "placeholder": "Enter bio"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter phone"}))
    role = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder": "Enter role"}))
    class Meta:
        model= get_user_model()
        fields= ["first_name", "last_name", "username", "email", "address", "bio", "phone", "role", "profile_pic"]


from django import forms
from .models import Notation

class NotationForm(forms.ModelForm):
    class Meta:
        model = Notation
        fields = ['eleve', 'matiere', 'periode', 'note_attendue', 'note_obtenue']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si une instance existe déjà, charge les notes existantes
        if self.instance and self.instance.pk:
            self.fields['note_attendue'].initial = self.instance.note_attendue
            self.fields['note_obtenue'].initial = self.instance.note_obtenue
        else:
            # Par défaut, initialiser à 0 si c'est une nouvelle entrée
            self.fields['note_attendue'].initial = 0
            self.fields['note_obtenue'].initial = 0

    def clean(self):
        cleaned_data = super().clean()
        eleve = cleaned_data.get('eleve')
        matiere = cleaned_data.get('matiere')
        periode = cleaned_data.get('periode')

        # Vérifie si une notation existe déjà pour cet élève, matière et période
        if eleve and matiere and periode:
            existing_notation = Notation.objects.filter(
                eleve=eleve,
                matiere=matiere,
                periode=periode
            ).first()
            if existing_notation:
                # Si une notation existe, on l'utilise pour la mise à jour
                self.instance = existing_notation

        return cleaned_data
