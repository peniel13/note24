from django.urls import path
from . import views 

urlpatterns = [
    path('ajouter_notation/', views.ajouter_notation, name='ajouter_notation'),
    path('signup',views.signup, name='signup'),
    path('signin',views.signin, name='signin'),
    path('signout',views.signout, name='signout'),
    path('profile',views.profile, name='profile'),
    path('update_profile',views.update_profile, name='update_profile'),
    path('load_eleves/', views.load_eleves, name='load_eleves'),
    path('load_matieres/', views.load_matieres, name='load_matieres'),
    path('success/', views.success_view, name='success_url'),
    path('classes/', views.liste_classes, name='liste_classes'),
    path('classes/<int:classe_id>/', views.details_classe, name='details_classe'),
    path('eleves/<int:eleve_id>/', views.details_eleve, name='details_eleve'),
    path('eleves/<int:eleve_id>/periode/<int:periode_id>/', views.details_periode, name='details_periode'),
    path('matiere/<int:matiere_id>/', views.details_matiere, name='details_matiere'),
    path('periode/<int:periode_id>/excel/', views.generer_excel, name='generer_excel')
]