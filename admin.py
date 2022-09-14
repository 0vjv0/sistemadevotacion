from django.contrib import admin
#from import_export.admin import ImportExportModelAdmin
#from import_export import resources
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


from .models import Persona, Cargo, Candidato, Fiscal, Voto

class PersonaAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'votacion_confirmada', 'territorio')

class VotoAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'enblanco')

class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'puesto', 'votos')

admin.site.register(Persona, PersonaAdmin)
admin.site.register(Cargo)
admin.site.register(Candidato, CandidatoAdmin)
admin.site.register(Fiscal)
admin.site.register(Voto, VotoAdmin)