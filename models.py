import os

from django.template.defaultfilters import date as _date
from django.db import models
from djangobeid.models import Personne
from django_survey.models import Survey, Questionnaire

from ckeditor.fields import RichTextField


class Observateur(Personne):

    class Meta:
        verbose_name = "Observateur"
        verbose_name_plural = "Observateurs"

    def __str__(self):
        return "%s %s" % (
            self.prenoms.split()[0],
            self.nom
        )


class Evaluateur(Personne):

    class Meta:
        verbose_name = "Évaluateur"
        verbose_name_plural = "Évaluateurs"

    def __str__(self):
        return "%s %s" % (
            self.prenoms.split()[0],
            self.nom
        )


class Metier(models.Model):
    nom = models.CharField("Métier", max_length=200)

    class Meta:
        verbose_name = "Métier"
        verbose_name_plural = "Métiers"

    def __str__(self):
        return self.nom


class UniteCompetence(models.Model):
    metier = models.ForeignKey(Metier, verbose_name="Métier")
    code = models.CharField("Code UC", max_length=10)
    intitule = models.TextField("Intitulé")

    class Meta:
        verbose_name = "Unité de compétence"
        verbose_name_plural = "Unités de compétence"

    def __str__(self):
        return self.code


class Candidat(Personne):
    email = models.EmailField()

    verbose_name = 'Candidat'


class Candidat_Epreuve(models.Model):

    RESULT_CHOICES = (
        (True, "Réussite"),
        (False, "Échec")
    )

    def upload_to_contrat(self, f):
        return os.path.join(
            self.epreuve.date.strftime("%Y-%m-%d"),
            "contrats",
            "contrat_" +
            self.candidat.nom.split()[0] + "." + f.split(".")[-1]
        )

    def upload_to_grille_eval(self, f):
        return os.path.join(
            self.epreuve.date.strftime("%Y-%m-%d"),
            "evaluations",
            "grille_eval_" +
            self.candidat.nom.split()[0] + "." + f.split(".")[-1]
        )

    def upload_to_grille_obs(self, f):
        return os.path.join(
            self.epreuve.date.strftime("%Y-%m-%d"),
            "evaluations",
            "grille_obs_" +
            self.candidat.nom.split()[0] + "." + f.split(".")[-1]
        )

    candidat = models.ForeignKey(Candidat)
    epreuve = models.ForeignKey("Epreuve", verbose_name="Épreuve")
    present = models.BooleanField("Présent", default=True)
    resultat = models.NullBooleanField(
        "Résultat",
        choices=RESULT_CHOICES,
        blank=True,
        null=True
    )
    contrat = models.FileField(
        "Contrat d'épreuve",
        upload_to=upload_to_contrat,
        blank=True, null=True)
    heure_fin = models.TimeField("Fin d'épreuve", blank=True, null=True)
    grille_evaluateur = models.FileField(
        "Grille d'évaluation évaluateur",
        upload_to=upload_to_grille_eval,
        blank=True,
        null=True
    )
    grille_observateur = models.FileField(
        "Grille d'évaluation observateur",
        upload_to=upload_to_grille_obs,
        blank=True,
        null=True
    )
    enquete = models.ForeignKey(
        Survey,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"

    def __str__(self):
        return ""

    def save(self, *args, **kwargs):
        if (self.present and
                self.resultat is not None and
                self.enquete is None):
            survey = Survey(
                subject="Épreuve %s du %s" % (
                    self.epreuve.unite_competence.metier,
                    _date(self.epreuve.date, "d F Y")
                ),
                email=self.candidat.email,
                questionnaire=self.epreuve.enquete,
                event_date=self.epreuve.date,
            )
            survey.save()
            self.enquete = survey
        super().save(*args, **kwargs)


class Epreuve(models.Model):
    def upload_to_checklist(self, f):
        return os.path.join(
            self.date.strftime("%Y-%m-%d"),
            "checklist_observateur." + f.split(".")[-1]
        )

    def upload_to_recepisse(self, f):
        return os.path.join(
            self.date.strftime("%Y-%m-%d"),
            "recepisse_fin_epreuve." + f.split(".")[-1]
        )
    unite_competence = models.ForeignKey(
        UniteCompetence, verbose_name="Unité de compétence")
    date = models.DateField("Date d'épreuve")
    heure_debut = models.TimeField("Heure de début", blank=True, null=True)
    evaluateur = models.ForeignKey(Evaluateur, verbose_name="Évaluateur")
    observateur = models.ForeignKey(Observateur)
    checklist_observateur = models.FileField(
        "Checklist de l'observateur",
        upload_to=upload_to_checklist,
        blank=True,
        null=True
    )
    recepisse = models.FileField(
        "Récépissé de de fin d'épreuve",
        upload_to=upload_to_recepisse,
        blank=True,
        null=True
    )
    enquete = models.ForeignKey(
        Questionnaire,
    )
    observations = RichTextField(verbose_name="Observations", blank=True)
    ameliorations = RichTextField(verbose_name="Améliorations", blank=True)

    class Meta:
        verbose_name = "Épreuve"
        verbose_name_plural = "Épreuves"

    def __str__(self):
        return "%s - %s" % (self.unite_competence.code, str(self.date))

    def nb_candidats(self):
        return len(self.candidat_epreuve_set.filter(present=True))
    nb_candidats.short_description = "Nombre de candidats présents"

    def checklist_uploaded(self):
        return bool(self.checklist_observateur)
    checklist_uploaded.short_description = "Checklist Observateur"
    checklist_uploaded.boolean = True

    def recepisse_uploaded(self):
        return bool(self.recepisse)
    recepisse_uploaded.short_description = "Récépissé"
    recepisse_uploaded.boolean = True

    def grille_eval_uploaded(self):
        nb_uploaded = len(
            self.candidat_epreuve_set.filter(grille_evaluateur__gt="")
        )
        return nb_uploaded == self.nb_candidats()
    grille_eval_uploaded.short_description = "Evaluation Évaluateur"
    grille_eval_uploaded.boolean = True

    def grille_obs_uploaded(self):
        nb_uploaded = len(
            self.candidat_epreuve_set.filter(grille_observateur__gt="")
        )
        return nb_uploaded == self.nb_candidats()
    grille_obs_uploaded.short_description = "Évaluation Observateur"
    grille_obs_uploaded.boolean = True
