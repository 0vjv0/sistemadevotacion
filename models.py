from django.db import models
from django.contrib.auth.models import User

class Persona(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name="votante")
    votacion_confirmada = models.BooleanField(default= False)
    es_fiscal = models.BooleanField(default= False)
    es_comite = models.BooleanField(default= False)
    territorio = models.CharField(max_length=64, default='')

    @property
    def full_name(self):
        return "%s %s"%(self.user.first_name, self.user.last_name)

    def __str__(self):
        return self.full_name

class Cargo(models.Model):
    cargo = models.CharField(max_length=64)

    def __str__(self):
        return self.cargo

class Candidato(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key= True)
    puesto = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    votos = models.IntegerField(default=0)

    @property
    def full_name(self):
        return "%s %s"%(self.id.first_name, self.id.last_name)

    def __str__(self):
        return self.full_name

class Fiscal(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    @property
    def full_name(self):
        return "%s %s"%(self.user.first_name, self.user.last_name)

    def __str__(self):
        return self.full_name

class Voto(models.Model):
    votante = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="votos_hechos")
    votado = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name="votos_recibidos", null= True,blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name="cargos_votados", default="no")
    enblanco = models.BooleanField(default=False)