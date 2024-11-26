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
        initial="15387641K",  # Asignar temporalmente el RUT
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Ingrese el RUT sin puntos ni guion. Ejemplo: 12345678K'
    )

    class Meta:
        model = Persona
        fields = ('rut', 'nombre', 'apellido', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rut'].label = 'RUT'
        self.fields['nombre'].label = 'Nombre'
        self.fields['apellido'].label = 'Apellido'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        print(f"Original RUT: {rut}")
        rut = rut.replace(".", "").replace("-", "").upper()
        print(f"Cleaned RUT: {rut}")

        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            print("RUT no tiene el formato correcto.")
            raise forms.ValidationError('El RUT debe tener entre 8 y 9 caracteres sin puntos ni guion.')

        if not self.validar_rut(rut):
            print("RUT no es válido.")
            raise forms.ValidationError('El RUT ingresado no es válido. Asegúrate de usar el formato correcto (XXXXXXXX-X).')

        return rut

    @staticmethod
    def validar_rut(rut):
        rut = rut.upper().replace("-", "").replace(".", "")
        rut_aux = rut[:-1]
        dv = rut[-1:]

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
        initial="15387641K",  # Asignar temporalmente el RUT
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Ingrese el RUT sin puntos ni guion. Ejemplo: 12345678K'
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Persona
        fields = ('rut', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        print(f"Original RUT: {rut}")
        rut = rut.replace(".", "").replace("-", "").upper()
        print(f"Cleaned RUT: {rut}")

        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            print("RUT no tiene el formato correcto.")
            raise forms.ValidationError('El RUT debe tener entre 8 y 9 caracteres sin puntos ni guion.')

        if not self.validar_rut(rut):
            print("RUT no es válido.")
            raise forms.ValidationError('El RUT ingresado no es válido. Asegúrate de usar el formato correcto (XXXXXXXX-X).')

        return rut

    @staticmethod
    def validar_rut(rut):
        # Eliminar puntos y guiones
        rut = rut.replace(".", "").replace("-", "").upper()
        print(f"RUT limpio: {rut}")

        # Validar formato general (números + dígito verificador)
        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            print("Formato del RUT no es válido")
            return False

        cuerpo = rut[:-1]  # Parte numérica del RUT
        dv = rut[-1]       # Dígito verificador
        print(f"Cuerpo: {cuerpo}, DV: {dv}")

        # Cálculo del dígito verificador
        suma = 0
        multiplicador = 2

        for digito in reversed(cuerpo):
            suma += int(digito) * multiplicador
            multiplicador = 9 if multiplicador == 7 else multiplicador + 1

        resto = suma % 11
        dv_calculado = 'K' if resto == 10 else str(11 - resto)
        print(f"DV Calculado: {dv_calculado}")

        return dv == dv_calculado