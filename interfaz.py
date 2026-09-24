from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFrame, QHeaderView
)
from PyQt5.QtCore import Qt


class VentanaInventarioPesado(QMainWindow):
    def __init__(self, sistema, gestor_json):
        super().__init__()
        self.sistema = sistema
        self.gestor_json = gestor_json
        self.setWindowTitle("HeavyParts Pro - Control de Inventario y Finanzas para Vehículos Pesados")
        self.resize(1220, 680)
        self._construir_interfaz()
        self.actualizar_vista()

    def _construir_interfaz(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)
        layout_principal = QVBoxLayout(contenedor)

        # Título superior
        titulo = QLabel("SISTEMA DE INVENTARIO Y RENTABILIDAD - REPUESTOS DE VEHÍCULOS PESADOS")
        titulo.setObjectName("TituloPrincipal")
        layout_principal.addWidget(titulo)

        # Panel de Tarjetas Financieras
        layout_finanzas = QHBoxLayout()
        self.lbl_invertido = self._crear_tarjeta(layout_finanzas, "CAPITAL TOTAL INVERTIDO", "$0.00", "ValorFinanciero")
        self.lbl_ingresos = self._crear_tarjeta(layout_finanzas, "INGRESO BRUTO OBTENIDO (VENTAS)", "$0.00", "ValorFinanciero")
        self.lbl_ganancia_empresa = self._crear_tarjeta(layout_finanzas, "GANANCIA NETA GENERADA", "$0.00", "ValorGanancia")
        layout_principal.addLayout(layout_finanzas)

        # Formulario para agregar nuevos repuestos
        layout_form = QHBoxLayout()

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del repuesto (ej. Motor Mack MP8, Cabina Cascadia...)")

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "Motores", "Cabinas de Camión", "Computadoras Electrónicas",
            "Transmisión Pesada", "Sistemas de Inyección y Turbo"
        ])

        self.spin_costo = QDoubleSpinBox()
        self.spin_costo.setPrefix("Costo Inv: $")
        self.spin_costo.setMaximum(999999.99)
        self.spin_costo.setValue(1200.00)

        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setPrefix("Precio Venta: $")
        self.spin_precio.setMaximum(999999.99)
        self.spin_precio.setValue(1850.00)

        self.spin_stock = QSpinBox()
        self.spin_stock.setPrefix("Stock: ")
        self.spin_stock.setMaximum(5000)
        self.spin_stock.setValue(3)

        self.spin_por_llegar = QSpinBox()
        self.spin_por_llegar.setPrefix("Por Llegar: ")
        self.spin_por_llegar.setMaximum(5000)
        self.spin_por_llegar.setValue(1)

        btn_agregar = QPushButton("Registrar Repuesto")
        btn_agregar.clicked.connect(self.accion_agregar_repuesto)

        for widget in [self.input_nombre, self.combo_categoria, self.spin_costo,
                       self.spin_precio, self.spin_stock, self.spin_por_llegar, btn_agregar]:
            layout_form.addWidget(widget)

        layout_principal.addLayout(layout_form)

        # Tabla de Inventario
        self.tabla = QTableWidget()
        columnas = [
            "Código", "Repuesto", "Categoría", "Stock Actual", "Vendidos",
            "Última Venta (Fecha)", "Por Llegar", "Costo Inversión",
            "Precio Venta (Tuyo)", "Ganancia Unitaria ($ / %)"
        ]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        layout_principal.addWidget(self.tabla)

        # Barra de Operaciones Rápidas sobre el repuesto seleccionado
        layout_acciones = QHBoxLayout()

        self.spin_cant_venta = QSpinBox()
        self.spin_cant_venta.setPrefix("Cant. a vender: ")
        self.spin_cant_venta.setMinimum(1)
        self.spin_cant_venta.setMaximum(500)

        btn_vender = QPushButton("Registrar Venta de Repuesto Seleccionado")
        btn_vender.setObjectName("BotonVenta")
        btn_vender.clicked.connect(self.accion_vender)

        btn_recibir = QPushButton("Confirmar Llegada de Mercancía en Tránsito")
        btn_recibir.setObjectName("BotonLlegada")
        btn_recibir.clicked.connect(self.accion_recibir_pedido)

        layout_acciones.addWidget(self.spin_cant_venta)
        layout_acciones.addWidget(btn_vender)
        layout_acciones.addWidget(btn_recibir)
        layout_principal.addLayout(layout_acciones)

    def _crear_tarjeta(self, layout_padre, titulo_texto, valor_inicial, nombre_estilo_valor):
        tarjeta = QFrame()
        tarjeta.setObjectName("TarjetaFinanciera")
        layout_interno = QVBoxLayout(tarjeta)
        lbl_titulo = QLabel(titulo_texto)
        lbl_valor = QLabel(valor_inicial)
        lbl_valor.setObjectName(nombre_estilo_valor)
        layout_interno.addWidget(lbl_titulo)
        layout_interno.addWidget(lbl_valor)
        layout_padre.addWidget(tarjeta)
        return lbl_valor

    def actualizar_vista(self):
        self.tabla.setRowCount(0)
        for fila, (codigo, rep) in enumerate(self.sistema.catalogo.items()):
            self.tabla.insertRow(fila)
            ganancia_u = rep.calcular_ganancia_unitaria()
            margen = rep.calcular_margen_porcentaje()

            datos_fila = [
                rep.codigo,
                rep.nombre,
                rep.categoria,
                str(rep.stock_actual),
                str(rep.vendidos),
                rep.obtener_ultima_venta(),
                str(rep.por_llegar),
                f"${rep.costo_inversion:,.2f}",
                f"${rep.precio_venta:,.2f}",
                f"+${ganancia_u:,.2f} ({margen}%)"
            ]

            for col, texto in enumerate(datos_fila):
                celda = QTableWidgetItem(texto)
                celda.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, col, celda)

        resumen = self.sistema.obtener_resumen_financiero()
        self.lbl_invertido.setText(f"${resumen['total_invertido']:,.2f}")
        self.lbl_ingresos.setText(f"${resumen['ingreso_obtenido']:,.2f}")
        self.lbl_ganancia_empresa.setText(f"+${resumen['ganancia_generada']:,.2f}")

    def accion_agregar_repuesto(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo vacío", "Ingresa el nombre del motor, cabina o módulo electrónico.")
            return

        costo = self.spin_costo.value()
        precio = self.spin_precio.value()
        if precio <= costo:
            respuesta = QMessageBox.question(
                self, "Advertencia de Margen",
                "El precio de venta no supera el costo de inversión. ¿Deseas registrarlo igualmente?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.No:
                return

        self.sistema.agregar_o_actualizar_repuesto(
            nombre=nombre,
            categoria=self.combo_categoria.currentText(),
            costo=costo,
            precio=precio,
            stock=self.spin_stock.value(),
            por_llegar=self.spin_por_llegar.value()
        )
        self.gestor_json.guardar_datos(self.sistema)
        self.input_nombre.clear()
        self.actualizar_vista()

    def _obtener_codigo_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Selección requerida", "Haz clic primero sobre un repuesto de la tabla.")
            return None
        return self.tabla.item(fila, 0).text()

    def accion_vender(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return
        exito, mensaje = self.sistema.registrar_venta(codigo, self.spin_cant_venta.value())
        if exito:
            self.gestor_json.guardar_datos(self.sistema)
            self.actualizar_vista()
            QMessageBox.information(self, "Venta Completada", mensaje)
        else:
            QMessageBox.warning(self, "No se pudo vender", mensaje)

    def accion_recibir_pedido(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return
        exito, mensaje = self.sistema.recibir_mercancia(codigo)
        if exito:
            self.gestor_json.guardar_datos(self.sistema)
            self.actualizar_vista()
            QMessageBox.information(self, "Recepción Exitosa", mensaje)
        else:
            QMessageBox.warning(self, "Sin pedidos en tránsito", mensaje)