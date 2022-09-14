from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.models import User
from .models import Persona, Cargo, Candidato, Voto


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        votante_obj = Persona.objects.get(user = request.user)

        if votante_obj.es_fiscal == True:
            return render (request, "Votacion/opciones_resultados.html")
            #return  HttpResponseRedirect(reverse("Votacion:resultados"))

        else:
            logout(request)
            return render(request, 'Votacion/cierre.html')



def login_view(request):
    if request.method == "POST":
        u = request.POST["username"]
        p = request.POST["password"]

        username = u.lower()
        password = p.lower()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("Votacion:index"))
        else:
            return render(request, "Votacion/login.html", {
            "message": "Parece que hubo un error; vuelta a intentarlo, por favor"
            })
    else:
        return render(request, "Votacion/login.html", {
        })

def logout_view(request):
	logout(request)
	return render(request, "Votacion/logout.html", {
	})

@csrf_protect
def salida(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        saliente = Persona.objects.get(user= request.user.pk)
        votos_set = Voto.objects.filter(votante = saliente)
        votaciones_hechas = []
        votaciones_sinhacer = []
        cargos_set = Cargo.objects.all()
        for c in cargos_set.iterator():
            votaciones_sinhacer.append(c.cargo)

        for v in votos_set.iterator():
            votaciones_hechas.append(v.cargo.cargo)
            for sv in votaciones_sinhacer:
                if sv == v.cargo.cargo:
                    votaciones_sinhacer.remove(sv)

        if request.method == "POST" and "blanco" in request.POST:
                for v in votaciones_sinhacer:
                    c = Cargo.objects.get(cargo = v)
                    if c == "Vocales":
                        Voto.objects.create(votante = saliente, cargo = c, enblanco = True)
                        Voto.objects.create(votante = saliente, cargo = c, enblanco = True)
                        Voto.objects.create(votante = saliente, cargo = c, enblanco = True)
                    else:
                        Voto.objects.create(votante = saliente, cargo = c, enblanco = True)
                logout(request)
                return HttpResponseRedirect(reverse('Votacion:logout'))
        else:
            return render(request, 'Votacion/salida.html', {
                "votaciones_hechas": votaciones_hechas,
                "votaciones_sinhacer": votaciones_sinhacer,
                "pendientes": len(votaciones_sinhacer)
                })

def chequeovotacion(request, cargo):

    puesto = Cargo.objects.get(cargo = cargo)

    try:
        Voto.objects.get(votante = request.user.pk, cargo = puesto.pk)
    except Voto.DoesNotExist:
        candidatos = Candidato.objects.filter(puesto = puesto)
        return HttpResponseRedirect(f'/Votacion/paginadevotacion/{cargo}', {
            "candidatos": candidatos,
            "puesto": puesto
        })
    return HttpResponseRedirect(reverse("Votacion:index"), {
        "message": "Ya voto por este cargo"
        })

@csrf_protect
def paginadevotacion(request, puesto):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        if request.method == "POST":
            if "voto" in request.POST:
                return HttpResponseRedirect(f'/Votacion/confirmar/{request.POST["voto"]}')

            else:
                puesto = puesto
                return HttpResponseRedirect(f'/Votacion/confirmar_blanco/{puesto}')

        else:
            cargo = Cargo.objects.get(cargo = puesto)
            candidatos = Candidato.objects.filter(puesto = cargo)
            return render(request, "Votacion/paginadevotacion.html", {
                "candidatos": candidatos,
                "puesto": cargo,
            })

@csrf_protect
def confirmar(request, voto):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        votado = Candidato.objects.get(pk = voto)

        if request.method == "POST":
            guardarvoto(request, votado)
            return HttpResponseRedirect(reverse("Votacion:index"), {
                "message": "Emitió su voto. Puede seleccionar otro cargo"
           })

        else:
            return render(request, "Votacion/confirmacion.html", {
                "votado": votado
            })

@csrf_protect
def varios_blancos(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        if request.method == "POST":
            blancos = request.POST.getlist('blanco')

            for b in blancos:
                guardarenblanco(request, b)

            return HttpResponseRedirect(reverse("Votacion:index"), {
                "message": "Emitió su voto. Puede seleccionar otro cargo"
                })


@csrf_protect
def confirmar_blanco(request, puesto):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        if request.method == "POST" and "blanco" in request.POST:
            guardarenblanco(request, puesto)
            return HttpResponseRedirect(reverse("Votacion:index"), {
                    "message": "Emitió su voto. Puede seleccionar otro cargo"
                    })
        else:
            return render(request, "Votacion/confirmacion.html", {
                "puesto": puesto,
           })

@csrf_protect
def confirmar_vocalias(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        if request.method == "POST":
            vocales = request.POST.getlist('vocal')
            vocales_votados = []
            for v in vocales:
                vocal = User.objects.get(username = v)
                vocales_votados.append(vocal)
            enblanco = 3 - len(vocales_votados)
            if "vocalias_votadas" in request.POST:
                return render(request, "Votacion/confirmar_vocalias.html", {
                    "vocales": vocales_votados,
                    "enblanco": enblanco
                    })
            elif "confirmar" in request.POST:
                for x in range(0, enblanco):
                    guardarenblanco(request, "Vocales")

                for v in vocales:
                    vocal = User.objects.get(username = v)
                    votado = Candidato.objects.get(id= vocal)
                    guardarvoto(request, votado)

                return HttpResponseRedirect(reverse("Votacion:index"), {
                    "message": "Emitió su voto. Puede seleccionar otro cargo"
                    })
            else:
                return HttpResponseRedirect('/Votacion/paginadevotacion/Vocales',)

        else:
            return HttpResponseRedirect('/Votacion/paginadevotacion/Vocales',)

def guardarvoto(request, votado):
    votante = Persona.objects.get(pk = request.user)
    Voto.objects.create(votante = votante, votado = votado, cargo = votado.puesto)
    votado.votos = votado.votos +1
    votado.save()
    return

def guardarenblanco(request, puesto):
    votante = Persona.objects.get(pk = request.user)
    cargo = Cargo.objects.get(cargo = puesto)
    Voto.objects.create(votante = votante, cargo = cargo, enblanco=True)
    return

def participacion(request, territorio):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))

    else:
        if territorio == 'globales':
            padron = Persona.objects.filter(es_fiscal = False, es_comite = False).exclude(territorio = '-').count()
            votos = len(Persona.objects.filter(votacion_confirmada= True))
            particpcn = votos * 100 / padron

        else:
            padron = Persona.objects.filter(territorio = territorio).count()
            votos = len(Persona.objects.filter(votacion_confirmada= True, territorio=territorio))
            particpcn = votos * 100 / padron

        return render(request, "Votacion/participacion.html", {
            "padron": padron,
            "votos": votos,
            "particpcn_porcentaje": round(particpcn),
            "abstencion_porcentaje": round(100 - particpcn),
            "particpcn": votos,
            "abstencion": padron - votos,
            "territorio": territorio,
        })


def resultados(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        c_presidencia = Candidato.objects.filter(puesto= Cargo.objects.get(cargo= "Presidencia")).order_by("-votos", "id")
        blancos_presidencia = Voto.objects.filter(cargo = Cargo.objects.get(cargo= "Presidencia"), votado__isnull = True).count()
        c_vicepresidencia = Candidato.objects.filter(puesto= Cargo.objects.get(cargo= "Vicepresidencia")).order_by("-votos", "id")
        blancos_vicepresidencia = Voto.objects.filter(cargo = Cargo.objects.get(cargo= "Vicepresidencia"), votado__isnull = True).count()
        c_secretaria = Candidato.objects.filter(puesto= Cargo.objects.get(cargo= "Secretaría")).order_by("-votos", "id")
        blancos_secretaria = Voto.objects.filter(cargo = Cargo.objects.get(cargo= "Secretaría"), votado__isnull = True).count()
        c_tesoreria = Candidato.objects.filter(puesto= Cargo.objects.get(cargo= "Tesorería")).order_by("-votos", "id")
        blancos_tesoreria = Voto.objects.filter(cargo = Cargo.objects.get(cargo= "Tesorería"), votado__isnull = True).count()
        c_vocalias = Candidato.objects.filter(puesto= Cargo.objects.get(cargo= "Vocales")).order_by("-votos", "id")
        #(Persona.objects.filter(votacion_confirmada = True).count() * 3) - Votos.objects.filter(cargo = "Vocales").count()
        blancos_vocales = Voto.objects.filter(cargo = Cargo.objects.get(cargo= "Vocales"), enblanco = True).count()

        return render(request, "Votacion/resultados.html", {
            "c_presidencia": c_presidencia,
            "blancos_presidencia": blancos_presidencia,
            "c_vicepresidencia": c_vicepresidencia,
            "blancos_vicepresidencia": blancos_vicepresidencia,
            "c_secretaria": c_secretaria,
            "blancos_secretaria": blancos_secretaria,
            "c_tesoreria": c_tesoreria,
            "blancos_tesoreria": blancos_tesoreria,
            "c_vocalias": c_vocalias,
            "blancos_vocales": blancos_vocales,
        })

def opciones(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("Votacion:login"))
    else:
        return render (request, "Votacion/opciones_resultados.html")

def cierre(request):
    logout(request)
    return render(request, "Votacion/cierre.html")

