from fpdf import FPDF
from datetime import datetime

class HerramientaReport(FPDF):
    def header(self):
        # Configuración de fuente para el encabezado
        self.set_font('Arial', 'B', 15)
        self.set_text_color(33, 150, 243) # Azul corporativo
        
        # Título
        self.cell(0, 10, 'CELUCENTRO - REPORTE DE INVENTARIO', 0, 1, 'C')
        
        # Subtítulo/Contexto
        self.set_font('Arial', '', 10)
        self.set_text_color(100)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(0, 5, f'Generado el: {fecha_actual}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def generate_table(self, herramientas):
        # Cabecera de la tabla
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(232, 232, 232)
        self.set_text_color(0)
        
        # Definir anchos de columna
        w = [60, 40, 25, 30, 30]
        cols = ['Nombre', 'Categoría', 'Stock Total', 'Stock Disp.', 'Estado']
        
        for i in range(len(cols)):
            self.cell(w[i], 10, cols[i], 1, 0, 'C', True)
        self.ln()
        
        # Datos de la tabla
        self.set_font('Arial', '', 9)
        for h in herramientas:
            # Color de stock bajo/agotado
            if h.stock_disponible <= 0:
                self.set_text_color(220, 53, 69) # Rojo
            elif h.stock_disponible <= 3:
                self.set_text_color(255, 193, 7) # Amarillo/Naranja
            else:
                self.set_text_color(0)
                
            self.cell(w[0], 8, self._truncate(h.nombre, 35), 1)
            self.set_text_color(0) # Reset color para el resto de la fila
            
            cat_nombre = h.id_categoria.nombre if h.id_categoria else 'N/A'
            self.cell(w[1], 8, self._truncate(cat_nombre, 20), 1)
            self.cell(w[2], 8, str(h.stock_total), 1, 0, 'C')
            self.cell(w[3], 8, str(h.stock_disponible), 1, 0, 'C')
            
            estado_str = 'Activo' if h.estado else 'Inactivo'
            self.cell(w[4], 8, estado_str, 1, 0, 'C')
            self.ln()

    def _truncate(self, text, max_len):
        return (text[:max_len-3] + '...') if len(text) > max_len else text
