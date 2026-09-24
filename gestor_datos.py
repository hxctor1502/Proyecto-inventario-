import json
import time
from modelos import RepuestoPesado


class GestorJSON:
    def __init__(self, ruta_archivo="inventario_pesado.json"):
        self.ruta_archivo = ruta_archivo

    def guardar_datos(self, sistema_inventario):
        datos_serializables = {
            "ultima_actualizacion": time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()),
            "repuestos": {}
        }
        for codigo, objeto_repuesto in sistema_inventario.catalogo.items():
            datos_serializables["repuestos"][codigo] = objeto_repuesto.a_diccionario()

        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos_serializables, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def cargar_datos(self, sistema_inventario):
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
                diccionario_repuestos = contenido.get("repuestos", {})

                sistema_inventario.catalogo.clear()
                for codigo, datos in diccionario_repuestos.items():
                    sistema_inventario.catalogo[codigo] = RepuestoPesado(
                        codigo=datos["codigo"],
                        nombre=datos["nombre"],
                        categoria=datos["categoria"],
                        costo_inversion=datos["costo_inversion"],
                        precio_venta=datos["precio_venta"],
                        stock_actual=datos["stock_actual"],
                        vendidos=datos["vendidos"],
                        por_llegar=datos["por_llegar"],
                        historial_ventas=datos.get("historial_ventas", [])
                    )
        except FileNotFoundError:
            self._cargar_datos_iniciales(sistema_inventario)
            self.guardar_datos(sistema_inventario)

    def _cargar_datos_iniciales(self, sistema_inventario):
        fecha_demo = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
        muestras = [
            RepuestoPesado("MOT-4501", "Motor Cummins ISX 15L", "Motores",
                           8500.00, 11800.00, 3, 2, 1,
                           [{"fecha": fecha_demo, "cantidad": 2, "ingreso_operacion": 23600.0, "ganancia_operacion": 6600.0}]),
            RepuestoPesado("CAB-2094", "Cabina Completa Kenworth T800", "Cabinas de Camión",
                           5200.00, 7600.00, 2, 1, 2,
                           [{"fecha": fecha_demo, "cantidad": 1, "ingreso_operacion": 7600.0, "ganancia_operacion": 2400.0}]),
            RepuestoPesado("ECU-8812", "Computadora ECM Detroit Diesel DDEC IV", "Computadoras Electrónicas",
                           950.00, 1550.00, 6, 4, 3,
                           [{"fecha": fecha_demo, "cantidad": 4, "ingreso_operacion": 6200.0, "ganancia_operacion": 2400.0}]),
            RepuestoPesado("TRA-3319", "Caja Eaton Fuller 18 Velocidades", "Transmisión Pesada",
                           3100.00, 4650.00, 4, 0, 2, [])
        ]
        for item in muestras:
            sistema_inventario.catalogo[item.codigo] = item