from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from itertools import cycle
from django.utils import timezone
import re

class PersonaManager(BaseUserManager):
    def create_user(self, email, password=None, rut=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico debe ser proporcionado')
        if not rut or not self.validar_rut(rut):
            raise ValueError('El RUT ingresado no es válido.')
        email = self.normalize_email(email)
        rut = rut.replace(".", "").replace("-", "").upper()  # Limpiar el RUT aquí
        user = self.model(email=email, rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, rut=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not email:
            raise ValueError('El correo electrónico debe ser proporcionado para administradores')
        return self.create_user(email, password, rut, **extra_fields)

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

class Persona(AbstractUser):
    rut = models.CharField(max_length=9, unique=True, blank=False)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateTimeField(default=timezone.now)
    telefono = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    comuna = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido']

    class Meta:
        db_table = 'tPersona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    objects = PersonaManager()

    def save(self, *args, **kwargs):
        if not self.username:  # Si no se especifica username, usa el RUT
            self.username = self.rut
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.nombre} {self.apellido}'

    # Añade related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='persona_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='persona',
    )
    # Añade related_name para evitar conflictos
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='persona_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='persona',
    )