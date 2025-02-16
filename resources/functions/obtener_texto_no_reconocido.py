from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
import sys

def obtener_texto_no_reconocido() -> str:
    '''
    función para extraer texto no reconocido en un mensaje de entrada y almacenarlo o procesarlo
    Returns:
        str: Mensaje con el resultado
    '''
    try:
        class MainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("obtener_texto_no_reconocido")
                self.setGeometry(100, 100, 400, 300)
                
                # Crear widget central y layout
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)
                
                # Agregar widgets
                self.txt_input = QPushButton("Seleccionar archivo de texto")
                self.txt_input.clicked.connect(self.seleccionar_archivo)
                                    
                self.lbl_status = QLabel("Esperando archivo de texto...")
                
                layout.addWidget(self.txt_input)
                layout.addWidget(self.lbl_status)
                
                self.show()
                    
                # Cerrar ventana al cerrar la aplicación
                QTimer.singleShot(100, self.close)
                
            def seleccionar_archivo(self):
                try:
                    # Abrir diálogo de selección de archivo
                    filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de texto", "", "Archivos de texto (*.txt)")
                    if filename:
                        # Obtener texto del archivo
                        with open(filename, "r") as f:
                            texto = f.read()
                                                    
                        # Verificar texto no reconocido
                        texto_no_reconocido = ""
                        for palabra in texto.split():
                            if palabra not in ["la", "el", "los", "las", "un", "una", "unos", "unas"]:
                                texto_no_reconocido += palabra + " "
                                                     
                        if texto_no_reconocido:
                            # Mostrar texto no reconocido
                            self.lbl_status.setText(f"Texto no reconocido:\n{texto_no_reconocido}")
                        else:
                            self.lbl_status.setText("No se encontró texto no reconocido")
                except Exception as e:
                    self.lbl_status.setText(f"Error: {e}")
                    
        # Crear aplicación
        app = QApplication(sys.argv)
        window = MainWindow()
        app.exec()
        
        return "Operación completada exitosamente"
    except Exception as e:
        return f"Error: {e}"