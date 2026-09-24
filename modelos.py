import time
import random
import math


class RepuestoPesado:
    def __init__(self, codigo, nombre, categoria, costo_inversion, precio_venta,
                 stock_actual, vendidos=0, por_llegar=0, historial_ventas=None):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.costo_inversion = round(float(costo_inversion), 2)
        self.precio_venta = round(float(precio_venta), 2)
        self.stock_actual = int(stock_actual)
        self.vendidos = int(vendidos)
        self.por_llegar = int(por_llegar)
        self.historial_ventas = historial_ventas if historial_ventas is not None else []

    def calcular_ganancia_unitaria(self):
        return round(self.precio_venta - self.costo_inversion, 2)

    def calcular_margen_porcentaje(self):
        if self.costo_inversion == 0:
            return 0.0
        porcentaje = ((self.precio_venta - self.costo_inversion) / self.costo_inversion) * 100
        return math.ceil(porcentaje * 10) / 10.0

    def obtener_ultima_venta(self):
        if len(self.historial_ventas) == 0:
            return "Sin ventas registradas"
        ultimo_registro = self.historial_ventas[-1]
        return f"{ultimo_registro['fecha']} ({ultimo_registro['cantidad']} ud.)"

    def a_diccionario(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "costo_inversion": self.costo_inversion,
            "precio_venta": self.precio_venta,
            "stock_actual": self.stock_actual,
            "vendidos": self.vendidos,
            "por_llegar": self.por_llegar,
            "historial_ventas": self.historial_ventas
        }


class SistemaInventario:
    def __init__(self):
        # Estructura de datos anidada principal: Diccionario de objetos y métricas
        self.catalogo = {}

    def generar_codigo_unico(self, categoria):
        prefijo = categoria[:3].upper()
        # Bucle while para garantizar que el código aleatorio no se repita
        while True:
            numero_azar = random.randint(1000, 9999)
            nuevo_codigo = f"{prefijo}-{numero_azar}"
            if nuevo_codigo not in self.catalogo:
                return nuevo_codigo

    def agregar_o_actualizar_repuesto(self, nombre, categoria, costo, precio, stock, por_llegar):
        codigo = self.generar_codigo_unico(categoria)
        nuevo_repuesto = RepuestoPesado(
            codigo=codigo,
            nombre=nombre,
            categoria=categoria,
            costo_inversion=costo,
            precio_venta=precio,
            stock_actual=stock,
            vendidos=0,
            por_llegar=por_llegar
        )
        self.catalogo[codigo] = nuevo_repuesto
        return nuevo_repuesto

    def eliminar_repuesto(self, codigo):
        if codigo in self.catalogo:
            del self.catalogo[codigo]
            return True, "Repuesto eliminado correctamente del inventario."
        return False, "El repuesto no existe."

    def actualizar_datos_repuesto(self, codigo, nuevo_nombre, nuevo_costo, nuevo_precio, nuevo_stock, por_llegar):
        if codigo in self.catalogo:
            item = self.catalogo[codigo]
            item.nombre = nuevo_nombre
            item.costo_inversion = round(float(nuevo_costo), 2)
            item.precio_venta = round(float(nuevo_precio), 2)
            item.stock_actual = int(nuevo_stock)
            item.por_llegar = int(por_llegar)
            return True, "Datos actualizados exitosamente."
        return False, "Repuesto no encontrado."

    def registrar_venta(self, codigo, cantidad):
        if codigo not in self.catalogo:
            return False, "El código del repuesto no existe."

        repuesto = self.catalogo[codigo]
        if cantidad <= 0:
            return False, "La cantidad a vender debe ser mayor a cero."
        elif repuesto.stock_actual < cantidad:
            return False, f"Stock insuficiente. Solo quedan {repuesto.stock_actual} unidades."
        else:
            repuesto.stock_actual -= cantidad
            repuesto.vendidos += cantidad
            fecha_actual = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
            repuesto.historial_ventas.append({
                "fecha": fecha_actual,
                "cantidad": cantidad,
                "ingreso_operacion": round(cantidad * repuesto.precio_venta, 2),
                "ganancia_operacion": round(cantidad * repuesto.calcular_ganancia_unitaria(), 2)
            })
            return True, f"Venta registrada el {fecha_actual}."

    def recibir_mercancia(self, codigo):
        if codigo in self.catalogo:
            repuesto = self.catalogo[codigo]
            if repuesto.por_llegar > 0:
                recibidos = repuesto.por_llegar
                repuesto.stock_actual += recibidos
                repuesto.por_llegar = 0
                return True, f"Se sumaron {recibidos} unidades al stock disponible."
            return False, "No hay unidades pendientes por llegar para este ítem."
        return False, "Repuesto no encontrado."

    def obtener_resumen_financiero(self):
        total_invertido = 0.0
        ingreso_obtenido = 0.0
        ganancia_neta_ventas = 0.0

        for codigo, item in self.catalogo.items():
            unidades_totales = item.stock_actual + item.vendidos + item.por_llegar
            total_invertido += unidades_totales * item.costo_inversion
            ingreso_obtenido += item.vendidos * item.precio_venta
            ganancia_neta_ventas += item.vendidos * item.calcular_ganancia_unitaria()

        return {
            "total_invertido": math.fsum([round(total_invertido, 2)]),
            "ingreso_obtenido": math.fsum([round(ingreso_obtenido, 2)]),
            "ganancia_generada": math.fsum([round(ganancia_neta_ventas, 2)])
        }