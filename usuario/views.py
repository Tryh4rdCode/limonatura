#limonatura/usuario/views.py: Este archivo contiene las vistas de la aplicación nsusuario
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import FormularioCreacionUsuario, FormularioAutenticacion
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import FormularioCreacionUsuario


def login_view(request):
    if request.method == 'POST':
        form = FormularioAutenticacion(data=request.POST)
        if form.is_valid():
            rut = form.cleaned_data.get('rut').replace(".", "").replace("-", "").upper()  # Limpiar el RUT
            password = form.cleaned_data.get('password')
            user = authenticate(request, rut=rut, password=password)
            if user is not None:
                login(request, user)
                return redirect('nsraiz:index')
            else:
                form.add_error(None, 'RUT o contraseña incorrectos')
    else:
        form = FormularioAutenticacion()
    return render(request, 'usuario/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('nsraiz:index')

def registro_view(request):
    if request.method == 'POST':
        form = FormularioCreacionUsuario(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                print(f'Usuario creado: {user.rut}')  # Verificar si el RUT se guarda correctamente
                messages.success(request, 'Usuario registrado exitosamente')
                return redirect('nsraiz:index')
            except IntegrityError as e:
                form.add_error(None, f'Error al registrar el usuario: {e}')
        else:
            form.add_error(None, 'Formulario no válido')
    else:
        form = FormularioCreacionUsuario()
    return render(request, 'usuario/registro.html', {'form': form})



@login_required
def perfil(request):
    return render(request, 'usuario/perfil.html')

@login_required
def actualizar_perfil(request):
    if request.method == 'POST':
        user = request.user
        user.rut = request.POST.get('rut', user.rut)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.telefono = request.POST.get('telefono', user.telefono)
        user.direccion = request.POST.get('direccion', user.direccion)
        user.region = request.POST.get('region', user.region)
        user.comuna = request.POST.get('comuna', user.comuna)
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('nsusuario:perfil')
    return render(request, 'usuario/perfil.html')

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Cuenta eliminada exitosamente')
        return redirect('nsraiz:index')
    return render(request, 'usuario/perfil.html')


def prueba_rut(request):

    data = {
        'rut': '201074673',  
        'nombre': 'Nombre3',
        'apellido': 'Apellido3',
        'email': 'prueba3@example.com',
        'password1': 'A_secure_password123!',
        'password2': 'A_secure_password123!',
    }
    
    form = FormularioCreacionUsuario(data)
    if form.is_valid():
        return HttpResponse("Formulario válido")
    else:
        print("Errores del formulario:")
        print(form.errors)
        return HttpResponse(f"Formulario no válido: {form.errors}")