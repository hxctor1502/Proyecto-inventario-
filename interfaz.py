from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFrame, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class DialogoNotaEntrega(QDialog):
    def __init__(self, detalles_compra, total_pagado, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nota de Entrega - Venta Confirmada")
        self.resize(450, 400)
        
        layout = QVBoxLayout(self)
        
        # Encabezado del ticket
        lbl_titulo = QLabel("<h2 style='color: #4ADE80; text-align: center;'>¡COMPRA PROCESADA EXITOSAMENTE!</h2>")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        lbl_subtitulo = QLabel("<b>*** NOTA DE ENTREGA ***</b><br>HeavyParts Pro - Repuestos Pesados<br>")
        lbl_subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_subtitulo)
        
        # Tabla resumen de lo que se pagó
        self.tabla_ticket = QTableWidget()
        self.tabla_ticket.setColumnCount(4)
        self.tabla_ticket.setHorizontalHeaderLabels(["Código", "Repuesto", "Cant.", "Subtotal"])
        self.tabla_ticket.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_ticket.setRowCount(len(detalles_compra))
        
        for fila, detalle in enumerate(detalles_compra):
            self.tabla_ticket.setItem(fila, 0, QTableWidgetItem(detalle['codigo']))
            self.tabla_ticket.setItem(fila, 1, QTableWidgetItem(detalle['nombre']))
            self.tabla_ticket.setItem(fila, 2, QTableWidgetItem(str(detalle['cantidad'])))
            self.tabla_ticket.setItem(fila, 3, QTableWidgetItem(f"${detalle['subtotal']:,.2f}"))
            
        layout.addWidget(self.tabla_ticket)
        
        # Total Final
        lbl_total = QLabel(f"<h3 style='color: #F59E0B; text-align: right;'>TOTAL PAGADO: ${total_pagado:,.2f}</h3>")
        lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(lbl_total)
        
        btn_cerrar = QPushButton("Cerrar e Imprimir (Simulado)")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)


class DialogoCarrito(QDialog):
    def __init__(self, carrito, sistema, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carrito de Compras - Revisión antes de Pagar")
        self.resize(600, 400)
        self.carrito = carrito  # Diccionario {codigo: cantidad}
        self.sistema = sistema
        
        self.layout_principal = QVBoxLayout(self)
        
        # Título
        self.layout_principal.addWidget(QLabel("<h3 style='color: #38BDF8;'>Artículos en tu carrito:</h3>"))
        
        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(4)
        self.tabla_carrito.setHorizontalHeaderLabels(["Código", "Repuesto", "Cantidad", "Subtotal"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_carrito.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout_principal.addWidget(self.tabla_carrito)
        
        # Total
        self.lbl_total = QLabel()
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ADE80;")
        self.lbl_total.setAlignment(Qt.AlignRight)
        self.layout_principal.addWidget(self.lbl_total)
        
        # Botones de edición
        layout_edicion = QHBoxLayout()
        
        self.spin_nueva_cant = QSpinBox()
        self.spin_nueva_cant.setPrefix("Nueva Cantidad: ")
        self.spin_nueva_cant.setMinimum(1)
        self.spin_nueva_cant.setMaximum(500)
        
        btn_editar = QPushButton("Editar Cantidad")
        btn_editar.setStyleSheet("background-color: #3B82F6; color: white;")
        btn_editar.clicked.connect(self.modificar_cantidad)
        
        btn_eliminar = QPushButton("Borrar Artículo del Carrito")
        btn_eliminar.setStyleSheet("background-color: #EF4444; color: white;")
        btn_eliminar.clicked.connect(self.eliminar_del_carrito)
        
        layout_edicion.addWidget(self.spin_nueva_cant)
        layout_edicion.addWidget(btn_editar)
        layout_edicion.addWidget(btn_eliminar)
        self.layout_principal.addLayout(layout_edicion)
        
        # Botones finales
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("PROCESAR PAGO")
        botones.button(QDialogButtonBox.Cancel).setText("Seguir Comprando")
        botones.accepted.connect(self.verificar_y_pagar)
        botones.rejected.connect(self.reject)
        self.layout_principal.addWidget(botones)
        
        self.actualizar_tabla()

    def actualizar_tabla(self):
        self.tabla_carrito.setRowCount(0)
        total_pagar = 0.0
        
        for fila, (codigo, cantidad) in enumerate(list(self.carrito.items())):
            if codigo not in self.sistema.catalogo:
                continue
                
            repuesto = self.sistema.catalogo[codigo]
            subtotal = repuesto.precio_venta * cantidad
            total_pagar += subtotal
            
            self.tabla_carrito.insertRow(fila)
            self.tabla_carrito.setItem(fila, 0, QTableWidgetItem(codigo))
            self.tabla_carrito.setItem(fila, 1, QTableWidgetItem(repuesto.nombre))
            self.tabla_carrito.setItem(fila, 2, QTableWidgetItem(str(cantidad)))
            self.tabla_carrito.setItem(fila, 3, QTableWidgetItem(f"${subtotal:,.2f}"))
            
        self.lbl_total.setText(f"MONTO TOTAL A PAGAR: ${total_pagar:,.2f}")
        
    def _obtener_codigo_seleccionado(self):
        fila = self.tabla_carrito.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Selección", "Selecciona un repuesto de la lista.")
            return None
        return self.tabla_carrito.item(fila, 0).text()

    def modificar_cantidad(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo: return
        
        nueva_cantidad = self.spin_nueva_cant.value()
        stock_disp = self.sistema.catalogo[codigo].stock_actual
        
        if nueva_cantidad > stock_disp:
            QMessageBox.warning(self, "Sin Stock", f"Solo hay {stock_disp} unidades disponibles.")
            return
            
        self.carrito[codigo] = nueva_cantidad
        self.actualizar_tabla()

    def eliminar_del_carrito(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo: return
        
        del self.carrito[codigo]
        self.actualizar_tabla()
        
    def verificar_y_pagar(self):
        if not self.carrito:
            QMessageBox.warning(self, "Carrito Vacío", "No hay nada que pagar.")
            return
        self.accept()


class DialogoEditar(QDialog):
    def __init__(self, repuesto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Datos del Repuesto")
        self.resize(400, 300)
        
        layout = QFormLayout(self)
        
        self.input_nombre = QLineEdit(repuesto.nombre)
        
        self.spin_costo = QDoubleSpinBox()
        self.spin_costo.setPrefix("$")
        self.spin_costo.setMaximum(999999.99)
        self.spin_costo.setValue(repuesto.costo_inversion)
        
        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setPrefix("$")
        self.spin_precio.setMaximum(999999.99)
        self.spin_precio.setValue(repuesto.precio_venta)
        
        self.spin_stock = QSpinBox()
        self.spin_stock.setMaximum(5000)
        self.spin_stock.setValue(repuesto.stock_actual)
        
        self.spin_por_llegar = QSpinBox()
        self.spin_por_llegar.setMaximum(5000)
        self.spin_por_llegar.setValue(repuesto.por_llegar)
        
        layout.addRow("Nombre de la pieza:", self.input_nombre)
        layout.addRow("Costo de Inversión:", self.spin_costo)
        layout.addRow("Precio de Venta:", self.spin_precio)
        layout.addRow("Stock Físico Actual:", self.spin_stock)
        layout.addRow("Mercancía por Llegar:", self.spin_por_llegar)
        
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Guardar Cambios")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
        
    def obtener_datos(self):
        return (
            self.input_nombre.text(),
            self.spin_costo.value(),
            self.spin_precio.value(),
            self.spin_stock.value(),
            self.spin_por_llegar.value()
        )


class VentanaInventarioPesado(QMainWindow):
    def __init__(self, sistema, gestor_json):
        super().__init__()
        self.sistema = sistema
        self.gestor_json = gestor_json
        self.carrito = {} # Nuevo: Aquí guardamos lo que se va a vender temporalmente
        self.setWindowTitle("HeavyParts Pro - Control de Inventario y Finanzas para Vehículos Pesados")
        self.resize(1250, 720)
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
        self.input_nombre.setPlaceholderText("Nombre del repuesto (ej. Motor Mack MP8...)")

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

        # Barra de Operaciones Rápidas
        layout_acciones = QHBoxLayout()

        self.spin_cant_venta = QSpinBox()
        self.spin_cant_venta.setPrefix("Cant. a vender: ")
        self.spin_cant_venta.setMinimum(1)
        self.spin_cant_venta.setMaximum(500)

        btn_anadir_carrito = QPushButton("Añadir al Carrito")
        btn_anadir_carrito.setObjectName("BotonVenta")
        btn_anadir_carrito.clicked.connect(self.accion_anadir_carrito)
        
        self.btn_ver_carrito = QPushButton("🛒 Ver Carrito (0)")
        self.btn_ver_carrito.setStyleSheet("background-color: #8B5CF6; color: white; font-weight: bold;")
        self.btn_ver_carrito.clicked.connect(self.accion_ver_carrito)

        btn_recibir = QPushButton("Confirmar Llegada")
        btn_recibir.setObjectName("BotonLlegada")
        btn_recibir.clicked.connect(self.accion_recibir_pedido)

        btn_editar = QPushButton("Editar Artículo")
        btn_editar.setStyleSheet("background-color: #3B82F6; color: white; font-weight: bold;")
        btn_editar.clicked.connect(self.accion_editar)

        btn_eliminar = QPushButton("Eliminar Artículo")
        btn_eliminar.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        btn_eliminar.clicked.connect(self.accion_eliminar)

        layout_acciones.addWidget(self.spin_cant_venta)
        layout_acciones.addWidget(btn_anadir_carrito)
        layout_acciones.addWidget(self.btn_ver_carrito)
        layout_acciones.addWidget(btn_recibir)
        layout_acciones.addWidget(btn_editar)
        layout_acciones.addWidget(btn_eliminar)
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
        
    def actualizar_boton_carrito(self):
        cantidad_items = sum(self.carrito.values())
        self.btn_ver_carrito.setText(f"🛒 Ver Carrito ({cantidad_items})")

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

    def accion_anadir_carrito(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return
            
        repuesto = self.sistema.catalogo[codigo]
        cantidad_a_vender = self.spin_cant_venta.value()
        
        # Verificar stock antes de añadir
        cantidad_en_carrito = self.carrito.get(codigo, 0)
        if cantidad_en_carrito + cantidad_a_vender > repuesto.stock_actual:
            QMessageBox.warning(self, "Stock Insuficiente", f"No puedes añadir más. Tienes {repuesto.stock_actual} en stock físico y ya tienes {cantidad_en_carrito} de estos en el carrito.")
            return
            
        self.carrito[codigo] = cantidad_en_carrito + cantidad_a_vender
        self.actualizar_boton_carrito()
        QMessageBox.information(self, "Añadido", f"Se añadió {cantidad_a_vender}x {repuesto.nombre} al carrito.")
        
    def accion_ver_carrito(self):
        if not self.carrito:
            QMessageBox.information(self, "Carrito Vacío", "No has añadido nada al carrito aún.")
            return
            
        dialogo = DialogoCarrito(self.carrito, self.sistema, self)
        
        if dialogo.exec_() == QDialog.Accepted:
            # Procesar todos los pagos del carrito
            detalles_compra = []
            total_pagado = 0.0
            
            for cod, cant in self.carrito.items():
                rep = self.sistema.catalogo[cod]
                exito, _ = self.sistema.registrar_venta(cod, cant)
                if exito:
                    subtotal = rep.precio_venta * cant
                    total_pagado += subtotal
                    detalles_compra.append({
                        "codigo": cod,
                        "nombre": rep.nombre,
                        "cantidad": cant,
                        "subtotal": subtotal
                    })
            
            if detalles_compra:
                self.gestor_json.guardar_datos(self.sistema)
                self.carrito.clear() # Vaciamos el carrito tras pagar
                self.actualizar_boton_carrito()
                self.actualizar_vista()
                
                # Mostrar la nota de entrega
                nota = DialogoNotaEntrega(detalles_compra, total_pagado, self)
                nota.exec_()
        else:
            # Si el usuario cierra o cancela, actualizamos el botón por si eliminó cosas
            self.actualizar_boton_carrito()

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

    def accion_editar(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return
            
        repuesto = self.sistema.catalogo[codigo]
        dialogo = DialogoEditar(repuesto, self)
        
        if dialogo.exec_() == QDialog.Accepted:
            nuevo_nombre, nuevo_costo, nuevo_precio, nuevo_stock, nuevo_llegar = dialogo.obtener_datos()
            exito, mensaje = self.sistema.actualizar_datos_repuesto(
                codigo, nuevo_nombre, nuevo_costo, nuevo_precio, nuevo_stock, nuevo_llegar
            )
            if exito:
                self.gestor_json.guardar_datos(self.sistema)
                self.actualizar_vista()
                QMessageBox.information(self, "Actualizado Correctamente", mensaje)
            else:
                QMessageBox.warning(self, "Error al actualizar", mensaje)

    def accion_eliminar(self):
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return
            
        repuesto = self.sistema.catalogo[codigo]
        
        # Alerta para evitar que borres por accidente
        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Estás completamente seguro de que deseas eliminar '{repuesto.nombre}' ({codigo}) de tu inventario? Esta acción es irreversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacion == QMessageBox.Yes:
            exito, mensaje = self.sistema.eliminar_repuesto(codigo)
            if exito:
                # Si estaba en el carrito, lo sacamos por si acaso
                if codigo in self.carrito:
                    del self.carrito[codigo]
                    self.actualizar_boton_carrito()
                    
                self.gestor_json.guardar_datos(self.sistema)
                self.actualizar_vista()
                QMessageBox.information(self, "Artículo Eliminado", mensaje)
            else:
                QMessageBox.warning(self, "Error al eliminar", mensaje)