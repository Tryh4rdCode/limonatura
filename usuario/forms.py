from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Persona
import re
from itertools import cycle

class FormularioCreacionUsuario(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    rut = forms.CharField(
        max_length=9, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Ingrese el RUT sin puntos ni guion. Ejemplo: 12345678K'
    )

    class Meta:
        model = Persona
        fields = ('rut', 'nombre', 'apellido', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No es necesario definir etiquetas explícitamente si los nombres de los campos son suficientemente descriptivos.
        # Django generará las etiquetas automáticamente, pero si deseas personalizarlas, puedes dejar esta parte.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        rut = self.limpiar_rut(rut)  # Utilizamos la función de limpieza aquí

        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            raise forms.ValidationError('El RUT debe tener entre 8 y 9 caracteres sin puntos ni guion.')

        if not self.validar_rut(rut):
            raise forms.ValidationError('El RUT ingresado no es válido. Asegúrate de usar el formato correcto (XXXXXXXX-X).')

        return rut

    @staticmethod
    def limpiar_rut(rut):
        """Función para limpiar el RUT eliminando puntos y guiones"""
        return rut.replace(".", "").replace("-", "").upper()

    @staticmethod
    def validar_rut(rut):
        """Función para validar el RUT utilizando el dígito verificador"""
        rut_aux = rut[:-1]  # Parte numérica del RUT
        dv = rut[-1]  # Dígito verificador

        # Validar que el cuerpo del RUT sea numérico y dentro del rango
        if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
            return False

        revertido = map(int, reversed(rut_aux))
        factors = cycle(range(2, 8))
        suma = sum(d * f for d, f in zip(revertido, factors))
        residuo = suma % 11

        if dv == 'K':
            return residuo == 1
        if dv == '0':
            return residuo == 11
        return residuo == 11 - int(dv)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class FormularioAutenticacion(forms.Form):
    rut = forms.CharField(
        max_length=9, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Ingrese el RUT sin puntos ni guion. Ejemplo: 12345678K'
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Persona
        fields = ('rut', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aseguramos que todos los campos tengan la clase CSS correcta para el estilo.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        rut = self.limpiar_rut(rut)  # Utilizamos la función de limpieza aquí

        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            raise forms.ValidationError('El RUT debe tener entre 8 y 9 caracteres sin puntos ni guion.')

        if not self.validar_rut(rut):
            raise forms.ValidationError('El RUT ingresado no es válido. Asegúrate de usar el formato correcto (XXXXXXXX-X).')

        return rut

    @staticmethod
    def limpiar_rut(rut):
        """Función para limpiar el RUT eliminando puntos y guiones"""
        return rut.replace(".", "").replace("-", "").upper()

    @staticmethod
    def validar_rut(rut):
        """Función para validar el RUT utilizando el dígito verificador"""
        rut_aux = rut[:-1]  # Parte numérica del RUT
        dv = rut[-1]  # Dígito verificador

        # Validar que el cuerpo del RUT sea numérico y dentro del rango
        if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
            return False

        suma = 0
        multiplicador = 2
        for digito in reversed(rut_aux):
            suma += int(digito) * multiplicador
            multiplicador = 9 if multiplicador == 7 else multiplicador + 1

        residuo = suma % 11
        dv_calculado = 'K' if residuo == 10 else str(11 - residuo)

        return dv == dv_calculado
