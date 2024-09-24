from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('socios/', views.lista_socios, name='lista_socios'),
    path('prestamos/', views.prestamos, name='prestamos'),
    path('detalles_socio/', views.detalles_socio, name='detalles_socio'),  # Ruta para los detalles del socio
    path('reportes/', views.reportes, name='reportes'),
    path('prestamo/', views.prestamos, name='prestamo'),  # Ruta para buscar socio y registrar préstamo
    path('registrar_prestamo/', views.registrar_prestamo, name='registrar_prestamo'),  # Ruta para registrar préstamo
    path('registrar_socio/', views.registrar_socio, name='registrar_socio'),  # Ruta para registrar nuevo socio
    path('socios/', views.lista_socios, name='lista_socios'),  # Asegúrate de tener la ruta de la lista de socios
    path('socios/detalles_socio/<int:id>/', views.detalles_socio, name='detalles_socio'),
    path('socios/registrar_prestamo/', views.registrar_prestamo, name='registrar_prestamo'),
    path('socios/eliminar/<int:id>/', views.eliminar_socio, name='eliminar_socio'),
    path('socios/editar/<int:id>/', views.editar_socio, name='editar_socio'),
    path('obtener_cuota_prestamo/', views.obtener_cuota_prestamo, name='obtener_cuota_prestamo'),
    path('registrar_pagos/', views.registrar_pago, name='registrar_pagos'),
    path('registrar_pagos/', views.buscar_socio, name='buscar_socio'),
    path('registrar_pago/', views.registrar_pago, name='registrar_pago'),
    path('reportes/', views.reportes, name='reportes'),
    path('guardar_reporte/', views.guardar_reporte, name='guardar_reporte'),

]