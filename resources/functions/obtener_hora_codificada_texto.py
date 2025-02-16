from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt6.QtSpeech import QAudioInput, QAudioOutput
from speech_recognition import Recognizer, Microphone
import os
import datetime

class SpeechRecognition(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Obtener Hora Codificada")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #282a36; color: #ffffff; font-size: 16px;")

        # Creación del layout vertical
        layout = QVBoxLayout()
        
        # Creación del widget para la imagen de instrucciones
        self.image_label = QLabel(self)
        image = QPixmap("instrucciones.png")
        self.image_label.setPixmap(image.scaled(600, 350, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.image_label)

        # Creación del botón para iniciar el reconocimiento de voz
        self.start_button = QPushButton("Iniciar Reconocimiento")
        self.start_button.clicked.connect(self.start_recognition)
        layout.addWidget(self.start_button)

        # Creación del label para mostrar el resultado
        self.result_label = QLabel(self)
        self.result_label.setText("Resultado:")
        layout.addWidget(self.result_label)

        # Creación del temporizador para el reconocimiento de voz
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.stop_recognition)

        # Establecimiento del layout
        self.setLayout(layout)

    def start_recognition(self):
        # Deshabilitar el botón de inicio
        self.start_button.setEnabled(False)

        # Inicialización del reconocedor de voz
        recognizer = Recognizer()
        with Microphone() as source:
            # Ajustar el ruido ambiental
            recognizer.adjust_for_ambient_noise(source)
            
            # Iniciar el reconocimiento
            self.timer.start()
            audio = recognizer.listen(source)

        # Detener el temporizador
        self.timer.stop()

        # Intentar reconocer el habla
        try:
            text = recognizer.recognize_sphinx(audio)
            # Extraer la hora del texto
            hora = self.extract_time(text)
            # Mostrar el resultado
            self.result_label.setText(f"Hora codificada: {hora}")
        except Exception as e:
            # Mostrar mensaje de error
            QMessageBox.critical(self, "Error", str(e))

        # Habilitar el botón de inicio
        self.start_button.setEnabled(True)

    def stop_recognition(self):
        # Detener el reconocimiento de voz
        self.timer.stop()

    def extract_time(self, text):
        # Buscar patrones de hora en el texto
        hora = re.findall(r"((?:[0-9]|diez|once|doce)(?: y |:|: )[0-5][0-9])", text)
        if not hora:
            raise ValueError("No se encontró ninguna hora en el texto")
        hora = hora[0]
        # Convertir la hora a formato HH:MM
        hora = hora.replace(" y ", ":")
        hora = datetime.datetime.strptime(hora, "%H:%M").strftime("%H:%M")
        return hora

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SpeechRecognition()
    window.show()
    sys.exit(app.exec())