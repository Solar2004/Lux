from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox
import sys

def obtener_hora_ubicacion_especifica() -> str:
    '''
    función para consultar la hora actual en una ubicación específica
    Returns:
        str: Mensaje con el resultado
    '''
    try:
        class MainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Obtener Hora Específica")
                self.setGeometry(100, 100, 400, 300)

                # Crear widget central y layout
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)
                
                # Crear grid layout para los widgets
                grid_layout = QGridLayout()
                layout.addLayout(grid_layout)

                # Agregar etiqueta y campo de entrada para la ciudad
                label_ciudad = QLabel("Ciudad:")
                grid_layout.addWidget(label_ciudad, 0, 0)
                self.input_ciudad = QLineEdit()
                grid_layout.addWidget(self.input_ciudad, 0, 1)

                # Agregar etiqueta y campo de entrada para el país
                label_pais = QLabel("País:")
                grid_layout.addWidget(label_pais, 1, 0)
                self.input_pais = QLineEdit()
                grid_layout.addWidget(self.input_pais, 1, 1)

                # Agregar botón para obtener la hora
                self.btn_obtener = QPushButton("Obtener Hora")
                grid_layout.addWidget(self.btn_obtener, 2, 1)

                # Agregar etiqueta para mostrar el resultado
                self.label_resultado = QLabel()
                grid_layout.addWidget(self.label_resultado, 3, 0, 1, 2)

                # Conectar el botón con el evento correspondiente
                self.btn_obtener.clicked.connect(self.obtener_hora)

            def obtener_hora(self):
                try:
                    import datetime
                    from pytz import timezone

                    # Obtener la ciudad y el país del usuario
                    ciudad = self.input_ciudad.text()
                    pais = self.input_pais.text()

                    # Crear un timezone para la ubicación específica
                    ubicacion = f"{ciudad}, {pais}"
                    tz = timezone(ubicacion)

                    # Obtener la fecha y hora actuales
                    ahora = datetime.datetime.now(tz=tz)

                    # Mostrar el resultado
                    self.label_resultado.setText(f"Hora actual en {ubicacion}: {ahora.strftime('%H:%M:%S %Z')}")
                except Exception as e:
                    self.label_resultado.setText(f"Error: {e}")
        
        # Crear aplicación
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        app.exec()
        
        return "Operación completada exitosamente"
                    
    except Exception as e:
        return f"Error: {e}"