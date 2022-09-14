from django.urls import path
from . import views

app_name = "Votacion"

urlpatterns = [
    path("", views.index, name ="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("salida", views.salida, name="salida"),
    path("cargo/<str:cargo>", views.chequeovotacion, name ="chequeovotacion"),
    path("paginadevotacion/<str:puesto>", views.paginadevotacion, name ="paginadevotacion"),
    path("confirmar/<int:voto>", views.confirmar, name="confirmar"),
    path("confirmar_vocalias", views.confirmar_vocalias, name="confirmar_vocalias"),
    path("confirmar_blanco/<str:puesto>", views.confirmar_blanco, name="confirmar_blanco"),
    path("varios_blancos", views.varios_blancos, name="varios_blancos"),
    path("participacion/<str:territorio>", views.participacion, name="participacion"),
    path("resultados", views.resultados, name="resultados"),
    path("opciones", views.opciones, name="opciones"),
    path("cierre", views.cierre, name="cierre")

]