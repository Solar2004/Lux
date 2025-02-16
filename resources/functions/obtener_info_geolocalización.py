from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtLocation import QGeoLocation
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys

def obtener_info_geolocalización() -> str:
    '''
    función para obtener información geográfica (como país) sobre la ubicación actual
    Returns:
        str: Mensaje con el resultado
    '''
    try:
        class MainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Obtener Información Geográfica")
                self.setGeometry(100, 100, 400, 300)

                # Crear widget central y layout
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                # Crear botón y conectar con el slot
                self.btn_geolocalización = QPushButton("Obtener Geolocalización")
                self.btn_geolocalización.clicked.connect(self.obtener_geolocalización)
                layout.addWidget(self.btn_geolocalización)

                # Crear etiqueta para mostrar el resultado
                self.label_resultado = QLabel()
                layout.addWidget(self.label_resultado)

                # Crear objeto de geolocalización
                self.geolocator = QGeoLocation()
                if not self.geolocator.isValid():
                    raise Exception("No se pudo obtener la geolocalización")

                self.show()

            def obtener_geolocalización(self):
                # Iniciar la geolocalización
                self.geolocator.start()
                # Conectar con la señal de nueva posición
                self.geolocator.positionUpdated.connect(self.actualizar_posicion)

            def actualizar_posicion(self, pos):
                self.geolocator.disconnect()  # Desconectar la señal
                lat = pos.coordinate().latitude()
                lon = pos.coordinate().longitude()
                # Obtener la URL de la API de OpenStreetMaps
                url = QUrl(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1")
                # Crear vista web y cargar la URL
                view = QWebEngineView(self)
                view.load(url)
                # Conectar con la señal de carga completada
                view.loadFinished.connect(self.mostrar_resultado)

            def mostrar_resultado(self):
                html = self.view.page().mainFrame().toHtml()
                # Analizar el HTML para obtener el país
                # (suponiendo que el HTML esté en el formato correcto)
                resultado = html[html.find('address country_name")">') + 23:]
                resultado = resultado[:resultado.find('<')]
                # Mostrar el resultado
                self.label_resultado.setText(resultado)

        # Crear aplicación
        app = QApplication(sys.argv)
        window = MainWindow()

        # Manejar el cierre de la ventana
        window.closeEvent = lambda event: app.quit()

        app.exec()

        return "Operación completada exitosamente"

    except Exception as e:
        return f"Error: {e}"