# Limonatura/carro/tests.py

from django.test import TestCase, RequestFactory
from tienda.models import Categoria_Coleg, Categoria_Produ, Categoria_Sexo, Fabricante, Producto
from carro.appcarro import Carro

from django.test import TestCase, Client
from django.urls import reverse
from tienda.models import Producto
from django.contrib.auth import get_user_model


from django.test import TestCase, RequestFactory
from carro.context_processor import valor_total_carro
from tienda.models import Producto
from carro.appcarro import Carro

##################################################################################################################

class CarroTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = {}
        self.carro = Carro(self.request)
        
        # Crear categorías necesarias
        self.categoria_prod = Categoria_Produ.objects.create(nombre='Categoria Produ', descripcion='Descripcion', codigo='PROD')
        self.categoria_sexo = Categoria_Sexo.objects.create(nombre='Categoria Sexo', descripcion='Descripcion', codigo='SEXO')
        self.categoria_cole = Categoria_Coleg.objects.create(nombre='Categoria Cole', descripcion='Descripcion', codigo='COLE')
        
        # Crear fabricante
        self.fabricante = Fabricante.objects.create(nombre='Fabricante Test')
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre='Producto Test', 
            precio=100.0, 
            stock=10,
            categorias_prod=self.categoria_prod,
            categorias_sexo=self.categoria_sexo,
            categorias_cole=self.categoria_cole,
            fabricante=self.fabricante
        )

    def test_agregar_producto(self):
        self.carro.agregar(self.producto)
        self.assertEqual(len(self.carro.carro), 1)
        self.assertEqual(self.carro.carro[str(self.producto.id)]['cantidad'], 1)

    def test_restar_producto(self):
        self.carro.agregar(self.producto)
        self.carro.restar_producto(self.producto)
        self.assertEqual(len(self.carro.carro), 0)

    def test_eliminar_producto(self):
        self.carro.agregar(self.producto)
        self.carro.eliminar(self.producto)
        self.assertEqual(len(self.carro.carro), 0)

    def test_limpiar_carro(self):
        self.carro.agregar(self.producto)
        self.carro.limpiar_carro()
        self.assertEqual(len(self.carro.carro), 0)


######################################################################################################################

class CarroViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345', email='testuser@example.com', rut='12345678-9')
        self.client.login(username='testuser', password='12345')
        
        # Crear categorías necesarias
        self.categoria_prod = Categoria_Produ.objects.create(nombre='Categoria Produ', descripcion='Descripcion', codigo='PROD')
        self.categoria_sexo = Categoria_Sexo.objects.create(nombre='Categoria Sexo', descripcion='Descripcion', codigo='SEXO')
        self.categoria_cole = Categoria_Coleg.objects.create(nombre='Categoria Cole', descripcion='Descripcion', codigo='COLE')
        
        # Crear fabricante
        self.fabricante = Fabricante.objects.create(nombre='Fabricante Test', usuario=self.user)
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre='Producto Test', 
            precio=100.0, 
            stock=10,
            categorias_prod=self.categoria_prod,
            categorias_sexo=self.categoria_sexo,
            categorias_cole=self.categoria_cole,
            fabricante=self.fabricante
        )

    def test_agregar_producto(self):
        response = self.client.get(reverse('carro:agregar', args=[self.producto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['carro'][str(self.producto.id)]['cantidad'], 1)

    def test_restar_producto(self):
        self.client.get(reverse('carro:agregar', args=[self.producto.id]))
        response = self.client.get(reverse('carro:restar', args=[self.producto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(str(self.producto.id), self.client.session['carro'])

    def test_eliminar_producto(self):
        self.client.get(reverse('carro:agregar', args=[self.producto.id]))
        response = self.client.get(reverse('carro:eliminar', args=[self.producto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(str(self.producto.id), self.client.session['carro'])

    def test_limpiar_carro(self):
        self.client.get(reverse('carro:agregar', args=[self.producto.id]))
        response = self.client.get(reverse('carro:limpiar'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.client.session['carro']), 0)

    def test_fin_pedido(self):
        self.client.get(reverse('carro:agregar', args=[self.producto.id]))
        response = self.client.post(reverse('carro:fin_pedido'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.client.session['carro']), 0)


##############################################################################################################################

class ContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = {}
        self.carro = Carro(self.request)
        
        # Crear usuario
        self.user = get_user_model().objects.create_user(username='testuser', password='12345', email='testuser@example.com', rut='12345678-9')
        
        # Crear categorías necesarias
        self.categoria_prod = Categoria_Produ.objects.create(nombre='Categoria Produ', descripcion='Descripcion', codigo='PROD')
        self.categoria_sexo = Categoria_Sexo.objects.create(nombre='Categoria Sexo', descripcion='Descripcion', codigo='SEXO')
        self.categoria_cole = Categoria_Coleg.objects.create(nombre='Categoria Cole', descripcion='Descripcion', codigo='COLE')
        
        # Crear fabricante
        self.fabricante = Fabricante.objects.create(nombre='Fabricante Test', usuario=self.user)
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre='Producto Test', 
            precio=100.0, 
            stock=10,
            categorias_prod=self.categoria_prod,
            categorias_sexo=self.categoria_sexo,
            categorias_cole=self.categoria_cole,
            fabricante=self.fabricante
        )
        self.carro.agregar(self.producto)

    def test_valor_total_carro(self):
        context = valor_total_carro(self.request)
        self.assertEqual(context['valor_total_carro'], 100.0)