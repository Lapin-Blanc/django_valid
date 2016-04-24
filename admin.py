import copy
from django.contrib import admin
from djangobeid.admin import PersonneAdmin
from .models import (
    Evaluateur,
    Observateur,
    Candidat,
    Epreuve,
    Candidat_Epreuve,
    Metier,
    UniteCompetence
)
from .widgets import ShortClearableFileInput
from django import forms


class UniteCompetenceInline(admin.StackedInline):
    model = UniteCompetence
    extra = 0


class MetierAdmin(admin.ModelAdmin):
    inlines = [UniteCompetenceInline]


class CandidatAdmin(PersonneAdmin):
    fieldsets = copy.deepcopy(PersonneAdmin.fieldsets)
    fieldsets[0][1]["fields"].insert(2, "email")


class EvaluateurAdmin(PersonneAdmin):
    pass


class ObservateurAdmin(PersonneAdmin):
    pass


class Candidat_Epreuve_addform(forms.ModelForm):

    class Meta:
        model = Candidat_Epreuve
        widgets = {
            "contrat": ShortClearableFileInput,
            "grille_evaluateur": ShortClearableFileInput,
            "grille_observateur": ShortClearableFileInput,
        }
        fields = [
            "candidat",
            "present",
            "contrat",
            "heure_fin",
            "grille_evaluateur",
            "grille_observateur",
            "resultat",
        ]


class Candidat_EpreuveInline(admin.TabularInline):
    model = Candidat_Epreuve
    max_num = 3
    form = Candidat_Epreuve_addform


class EpreuveAdmin(admin.ModelAdmin):
    fieldsets = [
        [
            None,
            {
                "fields":
                    [
                        "unite_competence",
                        "date",
                        "evaluateur",
                        "observateur",
                        "checklist_observateur",
                        "heure_debut",
                        "recepisse",
                        "enquete"
                    ]
            }
        ],
        [
            "Gestion des améliorations",
            {
                "classes":
                    [
                        "collapse",
                    ],
                "fields":
                    [
                        "observations",
                        "ameliorations"
                    ]
            }
        ]
    ]
    inlines = [Candidat_EpreuveInline]
    list_display = [
        "date",
        "unite_competence",
        "checklist_uploaded",
        "recepisse_uploaded",
        "grille_eval_uploaded",
        "grille_obs_uploaded",
    ]
    list_filter = [
        "date",
        "unite_competence__code"
    ]
    date_hierarchy = "date"

admin.site.register(Metier, MetierAdmin)
admin.site.register(Evaluateur, EvaluateurAdmin)
admin.site.register(Observateur, ObservateurAdmin)
admin.site.register(Candidat, CandidatAdmin)
admin.site.register(Epreuve, EpreuveAdmin)
