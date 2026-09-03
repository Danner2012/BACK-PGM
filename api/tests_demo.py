from django.test import TestCase
from django.urls import reverse
from rest_framework import status

class DemoQATest(TestCase):
    """
    Este es un test de demostración para QA.
    Valida que las rutas básicas del sistema respondan correctamente.
    """

    def test_verificar_acceso_api(self):
        # Intentamos acceder a la raíz de la API o una ruta conocida
        # Cambia 'api-root' por una ruta válida en tu urls.py si es necesario
        response = self.client.get('/')
        print(f"\n[QA DEBUG] Probando acceso a la API... Status: {response.status_code}")
        
        # Un QA esperaría que el servidor esté vivo (cualquier status < 500)
        self.assertLess(response.status_code, 500)

    def test_escenario_exitoso_qa(self):
        """Simula una prueba que siempre pasa para mostrar el Pipeline en VERDE"""
        self.assertEqual(1 + 1, 2)

    # def test_escenario_error_qa(self):
    #     """
    #     DESCOMENTA ESTO PARA LA DEMO: 
    #     Para mostrar cómo el Pipeline falla (se pone ROJO)
    #     """
    #     self.assertEqual(1 + 1, 3)
