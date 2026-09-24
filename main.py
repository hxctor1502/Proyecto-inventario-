import sys
from PyQt5.QtWidgets import QApplication
from modelos import SistemaInventario
from gestor_datos import GestorJSON
from interfaz import VentanaInventarioPesado


def cargar_estilos_qss(app, ruta_qss="estilos.qss"):
    try:
        with open(ruta_qss, "r", encoding="utf-8") as archivo_estilo:
            app.setStyleSheet(archivo_estilo.read())
    except FileNotFoundError:
        print("Aviso: No se encontró estilos.qss, ejecutando con estilo por defecto.")


def iniciar_aplicacion():
    app = QApplication(sys.argv)
    cargar_estilos_qss(app)

    sistema = SistemaInventario()
    gestor_json = GestorJSON("inventario_pesado.json")
    gestor_json.cargar_datos(sistema)

    ventana = VentanaInventarioPesado(sistema, gestor_json)
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    iniciar_aplicacion()