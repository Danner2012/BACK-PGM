from fpdf import FPDF
from datetime import datetime

class HerramientaReport(FPDF):
    def __init__(self, usuario_nombre="N/A", usuario_rol="N/A", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario_nombre = usuario_nombre
        self.usuario_rol = usuario_rol
        self.fecha_creacion = datetime.now().strftime("%d/%m/%Y %H:%M")

    def header(self):
        # Logo del negocio
        import os
        from django.conf import settings
        logo_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'public', 'logocel.png')
        
        if os.path.exists(logo_path):
            # Posicionamos el logo y calculamos su espacio
            self.image(logo_path, 10, 10, 30)
        
        # Título y Datos a la derecha
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 150, 243)
        self.cell(0, 12, 'CELUCENTRO - REPORTE DE INVENTARIO', 0, 1, 'R')
        
        # Información del documento
        self.set_font('Arial', '', 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, f'Generado por: {self.usuario_nombre}', 0, 1, 'R')
        self.cell(0, 6, f'Rol: {self.usuario_rol}', 0, 1, 'R')
        self.cell(0, 6, f'Fecha de Emisión: {self.fecha_creacion}', 0, 1, 'R')
        
        # Línea divisoria elegante (más abajo para no tocar el logo)
        self.ln(5)
        self.set_draw_color(33, 150, 243)
        self.set_line_width(0.8)
        self.line(10, 48, 200, 48)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        self.set_font('Arial', '', 8)
        self.cell(0, 10, 'Celucentro © 2024 - Sistema de Gestión', 0, 0, 'R')

    def generate_report_content(self, herramientas):
        # Resumen Rápido
        total = herramientas.count()
        bajo_stock = herramientas.filter(stock_disponible__gt=0, stock_disponible__lte=3).count()
        agotados = herramientas.filter(stock_disponible__lte=0).count()

        self.set_font('Arial', 'B', 12)
        self.set_text_color(50)
        self.cell(0, 10, 'Resumen de Inventario', 0, 1, 'L')
        
        self.set_font('Arial', '', 10)
        self.set_fill_color(245, 247, 251)
        self.cell(60, 8, f' Total Herramientas: {total}', 1, 0, 'L', True)
        self.cell(60, 8, f' Con Stock Bajo: {bajo_stock}', 1, 0, 'L', True)
        self.cell(0, 8, f' Agotadas: {agotados}', 1, 1, 'L', True)
        self.ln(10)

        # Cabecera de la tabla
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(33, 150, 243) # Azul sólido para cabecera
        self.set_text_color(255, 255, 255) # Blanco
        
        w = [65, 45, 25, 30, 25]
        cols = ['Nombre de Herramienta', 'Categoría', 'Total', 'Disponible', 'Estado']
        
        for i in range(len(cols)):
            self.cell(w[i], 10, cols[i], 1, 0, 'C', True)
        self.ln()
        
        # Datos de la tabla con efecto cebra
        self.set_font('Arial', '', 9)
        fill = False
        for h in herramientas:
            # Color de fondo alterno
            self.set_fill_color(240, 245, 255) if fill else self.set_fill_color(255, 255, 255)
            
            # Color del texto por stock
            if h.stock_disponible <= 0:
                self.set_text_color(220, 53, 69) # Rojo crítico
            elif h.stock_disponible <= 3:
                self.set_text_color(180, 120, 0) # Naranja/Ocre (más legible que amarillo)
            else:
                self.set_text_color(40, 40, 40)
            
            # Dibujar celdas
            self.cell(w[0], 9, f" {self._truncate(h.nombre, 38)}", 1, 0, 'L', True)
            self.set_text_color(40, 40, 40) # Reset para el resto
            
            cat = h.id_categoria.nombre if h.id_categoria else 'General'
            self.cell(w[1], 9, f" {self._truncate(cat, 22)}", 1, 0, 'L', True)
            self.cell(w[2], 9, str(h.stock_total), 1, 0, 'C', True)
            self.cell(w[3], 9, str(h.stock_disponible), 1, 0, 'C', True)
            
            estado = 'ACTIVO' if h.estado else 'INACT.'
            self.cell(w[4], 9, estado, 1, 1, 'C', True)
            
            fill = not fill # Alternar color

    def _truncate(self, text, max_len):
        return (text[:max_len-3] + '...') if len(text) > max_len else text

    def _truncate(self, text, max_len):
        return (text[:max_len-3] + '...') if len(text) > max_len else text
