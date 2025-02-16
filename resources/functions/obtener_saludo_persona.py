import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton

def obtener_saludo_persona() -> str:
    '''
    función para obtener un saludo genérico para una persona
    Returns:
        str: Mensaje con el resultado
    '''
    try:
        class MainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("obtener_saludo_persona")
                self.setGeometry(100, 100, 400, 300)
                
                # Crear widget central y layout
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)
                
                # Crear widgets
                label = QLabel("Hola, mundo!")
                button = QPushButton("Cerrar")
                
                # Agregar widgets al layout
                layout.addWidget(label)
                layout.addWidget(button)
                
                # Conectar el botón al evento de cierre
                button.clicked.connect(self.close)
                
                self.show()
                
            def closeEvent(self, event):
                event.accept()
                return super().closeEvent(event)
        
        # Crear aplicación
        app = QApplication(sys.argv)
        window = MainWindow()
        app.exec()
        
        return "Saludos generados exitosamente"
        
    except Exception as e:
        return f"Error: {e}"