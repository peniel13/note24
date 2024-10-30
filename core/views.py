from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Classe, Eleve, Periode, Matiere,Notation
from .forms import NotationForm,RegisterForm, UpdateProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.db.models import Sum


def signup(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect("signup")
        
    context = {"form":form}
    return render(request, "core/signup.html", context)

def signin (request):
    if request.method == 'POST':
        email = request.POST["email"]
        password= request.POST["password"]

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    context= {}
    return render(request, "core/login.html", context)

def signout(request):
    logout(request)
    return redirect("index")

@login_required(login_url="signin")
def profile(request):
    user = request.user
    
    context={"user": user, }
    return render(request, "core/profile.html", context)

@login_required(login_url="signin")
def update_profile(request):
    if request.user.is_authenticated:
        user = request.user
        form = UpdateProfileForm(instance=user)
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully")
                return redirect("profile")
                
    context = {"form": form}
    return render(request, "core/update_profile.html", context)


def ajouter_notation(request):
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        matiere_id = request.POST.get('matiere')
        periode_id = request.POST.get('periode')

        # Récupérer ou créer la notation
        notation, created = Notation.objects.get_or_create(
            eleve_id=eleve_id,
            matiere_id=matiere_id,
            periode_id=periode_id,
            defaults={'note_attendue': 0, 'note_obtenue': 0}
        )

        # Remplir le formulaire avec les valeurs existantes
        form = NotationForm(request.POST, instance=notation)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Remplace par ton URL de succès
    else:
        classe_id = request.GET.get('classe_id')
        form = NotationForm()  # Initialisez sans instance

    classes = Classe.objects.all()
    periodes = Periode.objects.all()

    return render(request, 'core/ajouter_notation.html', {'form': form, 'classes': classes, 'periodes': periodes})

def load_eleves(request):
    classe_id = request.GET.get('classe_id')
    eleves = Eleve.objects.filter(classe_id=classe_id).values('id', 'nom')
    return render(request, 'core/eleve_dropdown_list_options.html', {'eleves': eleves})

def load_matieres(request):
    classe_id = request.GET.get('classe_id')
    matieres = Matiere.objects.filter(classe_id=classe_id).values('id', 'nom')
    return render(request, 'core/matiere_dropdown_list_options.html', {'matieres': matieres})



def success_view(request):
    return render(request, 'core/success.html')  # Assurez-vous que ce template existe

# Liste des classes
def liste_classes(request):
    classes = Classe.objects.all()
    return render(request, 'core/liste_classes.html', {'classes': classes})

# Détails d'une classe
def details_classe(request, classe_id):
    classe = get_object_or_404(Classe, id=classe_id)
    eleves = Eleve.objects.filter(classe=classe)
    matieres = Matiere.objects.filter(classe=classe)
    return render(request, 'core/details_classe.html', {'classe': classe, 'eleves': eleves, 'matieres': matieres})

# Détails d'un élève
# def details_eleve(request, eleve_id):
#     eleve = get_object_or_404(Eleve, id=eleve_id)
#     notations = Notation.objects.filter(eleve=eleve)
#     return render(request, 'core/details_eleve.html', {'eleve': eleve, 'notations': notations})

# from django.shortcuts import render, get_object_or_404
# from .models import Eleve, Notation, Periode

# def details_eleve(request, eleve_id):
#     eleve = get_object_or_404(Eleve, id=eleve_id)
#     periodes = Periode.objects.all()
#     matieres = Matiere.objects.filter(classe=eleve.classe)

#     notations_par_matiere = {matiere: {} for matiere in matieres}

#     for periode in periodes:
#         notations = Notation.objects.filter(eleve=eleve, periode=periode)
#         for notation in notations:
#             notations_par_matiere[notation.matiere][periode] = notation

#     return render(request, 'core/details_eleve.html', {
#         'eleve': eleve,
#         'periodes': periodes,
#         'notations_par_matiere': notations_par_matiere,
#     })

def details_eleve(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    periodes = Periode.objects.all()

    notations_par_periode = {}
    for periode in periodes:
        notations = Notation.objects.filter(eleve=eleve, periode=periode)
        if notations.exists():
            moyenne_attendue = notations.aggregate(Avg('note_attendue'))['note_attendue__avg']
            moyenne_obtenue = notations.aggregate(Avg('note_obtenue'))['note_obtenue__avg']
            notations_par_periode[periode] = {
                'notations': notations,
                'moyenne_attendue': moyenne_attendue,
                'moyenne_obtenue': moyenne_obtenue,
            }

    return render(request, 'core/details_eleve.html', {
        'eleve': eleve,
        'notations_par_periode': notations_par_periode,
        'periodes': periodes,
    })

def details_matiere(request, matiere_id):
    matiere = get_object_or_404(Matiere, id=matiere_id)
    notations = Notation.objects.filter(matiere=matiere).select_related('eleve', 'periode')

    # Regrouper les notations par période
    periodes_notes = {}
    for notation in notations:
        periode = notation.periode
        if periode not in periodes_notes:
            periodes_notes[periode] = []
        eleve = notation.eleve
        periodes_notes[periode].append({
            'eleve': eleve,
            'note_attendue': notation.note_attendue,
            'note_obtenue': notation.note_obtenue,
        })

    return render(request, 'core/details_matiere.html', {
        'matiere': matiere,
        'periodes_notes': periodes_notes,
    })


def details_periode(request, eleve_id, periode_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    periode = get_object_or_404(Periode, id=periode_id)
    notations = Notation.objects.filter(eleve=eleve, periode=periode)

    total_attendu = notations.aggregate(Sum('note_attendue'))['note_attendue__sum'] or 0
    total_obtenu = notations.aggregate(Sum('note_obtenue'))['note_obtenue__sum'] or 0

    # Calcul du pourcentage
    pourcentage = (total_obtenu / total_attendu * 100) if total_attendu > 0 else 0

    return render(request, 'core/details_periode.html', {
        'eleve': eleve,
        'periode': periode,
        'notations': notations,
        'total_attendu': total_attendu,
        'total_obtenu': total_obtenu,
        'pourcentage': pourcentage,
    })



import openpyxl
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import get_object_or_404

def generer_excel(request, periode_id):
    periode = get_object_or_404(Periode, id=periode_id)
    
    # Récupération des notations avec l'élève et la matière
    notations = Notation.objects.select_related('eleve', 'matiere').filter(periode=periode)
    
    if notations.exists():
        classe = notations.first().eleve.classe.nom
    else:
        return HttpResponse("Aucune notation disponible pour cette période.", status=404)

    # Création du fichier Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Rapport {periode.nom}"

    # Ajout du nom de la classe
    ws.append([f"Classe: {classe}"])
    ws.append([])  # Ligne vide

    # Dictionnaire pour stocker les totaux par élève et matière
    totals = {}

    for notation in notations:
        eleve_nom = notation.eleve.nom
        matiere_nom = notation.matiere.nom
        note_attendue = notation.note_attendue
        note_obtenue = notation.note_obtenue

        # Structure des totaux
        if eleve_nom not in totals:
            totals[eleve_nom] = {}
        
        if matiere_nom not in totals[eleve_nom]:
            totals[eleve_nom][matiere_nom] = {'attendue': 0, 'obtenue': 0}
        
        totals[eleve_nom][matiere_nom]['attendue'] += note_attendue
        totals[eleve_nom][matiere_nom]['obtenue'] += note_obtenue

    # Ajout du nom de chaque élève dans le fichier
    for eleve in totals.keys():
        ws.append([f"Élève: {eleve}"])
    
    # Ajout d'une ligne vide pour séparer les élèves des en-têtes
    ws.append([])

    # Ajout des en-têtes
    ws.append(["Élève", "Matière", "Total Note Attendue", "Total Note Obtenue"])

    # Remplissage du fichier avec les données
    for eleve, matieres in totals.items():
        for matiere, notes in matieres.items():
            total_attendue = notes['attendue']
            total_obtenue = notes['obtenue']
            ws.append([eleve, matiere, total_attendue, total_obtenue])

    # Enregistrement du fichier en mémoire
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Création de la réponse HTTP pour le fichier
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="rapport_{periode.nom}.xlsx"'
    
    return response

def situations_eleve(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    periodes = Periode.objects.all()
    matieres = Matiere.objects.filter(classe=eleve.classe)

    notations_par_matiere = {
        matiere: {periode: Notation.objects.filter(eleve=eleve, matiere=matiere, periode=periode).first() for periode in periodes}
        for matiere in matieres
    }

    total_obtenu = 0
    total_attendu = 0

    total_periode_obtenu = {periode: 0 for periode in periodes}
    total_periode_attendu = {periode: 0 for periode in periodes}

    for matiere, notations in notations_par_matiere.items():
        for periode, notation in notations.items():
            if notation:
                total_obtenu += notation.note_obtenue
                total_attendu += notation.note_attendue
                total_periode_obtenu[periode] += notation.note_obtenue
                total_periode_attendu[periode] += notation.note_attendue

    # Calculer le pourcentage par période
    pourcentage_periode = {}
    for periode in periodes:
        if total_periode_attendu[periode] > 0:
            pourcentage_periode[periode] = (total_periode_obtenu[periode] / total_periode_attendu[periode]) * 100
        else:
            pourcentage_periode[periode] = 0

    # Calculer le pourcentage total
    pourcentage_total = (total_obtenu / total_attendu * 100) if total_attendu > 0 else 0

    return render(request, 'core/situations_eleve.html', {
        'eleve': eleve,
        'periodes': periodes,
        'matieres': matieres,
        'notations_par_matiere': notations_par_matiere,
        'total_obtenu': total_obtenu,
        'total_attendu': total_attendu,
        'total_periode_obtenu': total_periode_obtenu,
        'total_periode_attendu': total_periode_attendu,
        'pourcentage_periode': pourcentage_periode,
        'pourcentage_total': pourcentage_total,
    })

from django.http import HttpResponse 
from openpyxl import Workbook
from django.shortcuts import get_object_or_404
from .models import Eleve, Notation, Periode, Matiere

def generer_excel2(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    periodes = Periode.objects.all()  # Récupérer toutes les périodes
    matieres = Matiere.objects.filter(classe=eleve.classe)  # Récupérer les matières de la classe de l'élève

    # Créer un classeur et une feuille
    wb = Workbook()
    ws = wb.active
    ws.title = f"Situation de {eleve.nom}"

    # Ajouter les en-têtes
    headers = ['Matières']
    for periode in periodes:
        headers.append(f"{periode.nom} - Note Obtenue")
        headers.append(f"{periode.nom} - Note Attendue")
    headers.append('Total Obtenu')
    headers.append('Total Attendu')
    for periode in periodes:
        headers.append(f"{periode.nom} - Pourcentage")
    ws.append(headers)

    # Variables pour accumuler les totaux
    total_obtenu_periode = [0] * len(periodes)
    total_attendu_periode = [0] * len(periodes)

    # Ajouter les données des notations
    for matiere in matieres:
        row = [matiere.nom]  # Commencer la ligne avec le nom de la matière
        for index, periode in enumerate(periodes):
            notation = Notation.objects.filter(eleve=eleve, matiere=matiere, periode=periode).first()
            if notation:
                row.append(notation.note_obtenue)
                row.append(notation.note_attendue)
                total_obtenu_periode[index] += notation.note_obtenue
                total_attendu_periode[index] += notation.note_attendue
            else:
                row.append('N/A')
                row.append('N/A')
        ws.append(row)

    # Ajouter la ligne de totaux
    total_row = ['Total']
    for total_obtenu, total_attendu in zip(total_obtenu_periode, total_attendu_periode):
        total_row.append(total_obtenu)
        total_row.append(total_attendu)
    ws.append(total_row)

    # Calculer et ajouter les pourcentages
    pourcentage_row = ['Pourcentage']
    for total_obtenu, total_attendu in zip(total_obtenu_periode, total_attendu_periode):
        if total_attendu > 0:
            pourcentage = (total_obtenu / total_attendu) * 100
        else:
            pourcentage = 0
        pourcentage_row.append(f"{pourcentage:.2f}%")
    ws.append(pourcentage_row)

    # Créer la réponse HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{eleve.nom}_situation.xlsx"'

    # Sauvegarder le classeur dans la réponse
    wb.save(response)
    
    return response
