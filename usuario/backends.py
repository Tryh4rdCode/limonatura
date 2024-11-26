# limonatura/usuario/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Persona

class RUTAuthBackend(BaseBackend):
    def authenticate(self, request, rut=None, password=None):
        if rut:
            rut = rut.replace(".", "").replace("-", "").upper()  # Limpiar el RUT
        try:
            user = Persona.objects.get(rut=rut)
            if user.check_password(password):
                return user
        except Persona.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return Persona.objects.get(pk=user_id)
        except Persona.DoesNotExist:
            return None
