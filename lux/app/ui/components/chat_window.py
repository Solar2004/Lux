from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QDialog, QLabel, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
import json
from pathlib import Path
from datetime import datetime
import logging
from ...services.ai_service import AIService

logger = logging.getLogger('lux')

class ChatWindow(QDialog):
    """Ventana de chat con IA"""
    
    def __init__(self, ai_service: AIService, parent=None):
        super().__init__(parent)
        self.ai_service = ai_service
        self.chat_history = []
        self.current_model = "gemini"  # Modelo por defecto
        
        self._setup_ui()
        self._load_chat_history()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Chat con IA")
        self.setMinimumSize(600, 800)
        
        layout = QVBoxLayout(self)
        
        # Selector de modelo
        model_layout = QHBoxLayout()
        model_label = QLabel("Modelo:")
        self.model_selector = QComboBox()
        self.model_selector.addItems(self.ai_service.get_available_models())
        self.model_selector.currentTextChanged.connect(self._on_model_changed)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()
        layout.addLayout(model_layout)
        
        # Área de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        
        # Área de entrada
        input_layout = QHBoxLayout()
        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(100)
        self.input_area.textChanged.connect(self._on_input_changed)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setEnabled(False)
        
        input_layout.addWidget(self.input_area)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        # Estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QTextEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #404040;
                color: #FFFFFF;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #2D2D2D;
                color: #808080;
            }
            QLabel {
                color: #FFFFFF;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 5px;
                padding: 5px;
            }
        """)
    
    def _on_input_changed(self):
        """Habilita/deshabilita el botón de enviar según el contenido"""
        self.send_button.setEnabled(bool(self.input_area.toPlainText().strip()))
    
    def _on_model_changed(self, model):
        """Maneja el cambio de modelo de IA"""
        self.current_model = model
        self._append_system_message(f"Cambiado a modelo: {model}")
    
    def _send_message(self):
        """Envía el mensaje al modelo de IA"""
        message = self.input_area.toPlainText().strip()
        if not message:
            return
        
        # Mostrar mensaje del usuario
        self._append_user_message(message)
        self.input_area.clear()
        
        # Obtener respuesta según el modelo
        response = self.ai_service.chat_with_model(message, self.current_model)
        
        # Mostrar respuesta
        if response:
            self._append_ai_message(response)
        else:
            self._append_system_message("Error al obtener respuesta")
        
        # Guardar historial
        self._save_chat_history()
    
    def _append_user_message(self, message):
        """Añade mensaje del usuario al chat"""
        self.chat_area.append(f"\n<b>Tú:</b> {message}\n")
        self.chat_history.append({"role": "user", "content": message})
    
    def _append_ai_message(self, message):
        """Añade mensaje de la IA al chat"""
        self.chat_area.append(f"\n<b>IA:</b> {message}\n")
        self.chat_history.append({"role": "assistant", "content": message})
    
    def _append_system_message(self, message):
        """Añade mensaje del sistema al chat"""
        self.chat_area.append(f"\n<i>Sistema: {message}</i>\n")
    
    def _save_chat_history(self):
        """Guarda el historial de chat"""
        try:
            history_file = Path("resources/chat_history.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Mantener solo las últimas 100 interacciones
            if len(self.chat_history) > 100:
                self.chat_history = self.chat_history[-100:]
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "model": self.current_model,
                "messages": self.chat_history
            }
            
            with history_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error al guardar historial: {e}")
    
    def _load_chat_history(self):
        """Carga el historial de chat"""
        try:
            history_file = Path("resources/chat_history.json")
            if history_file.exists():
                with history_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chat_history = data.get("messages", [])
                    
                    # Mostrar historial en el chat
                    for msg in self.chat_history:
                        if msg["role"] == "user":
                            self._append_user_message(msg["content"])
                        elif msg["role"] == "assistant":
                            self._append_ai_message(msg["content"])
                    
                    # Seleccionar el modelo guardado
                    saved_model = data.get("model", "gemini")
                    index = self.model_selector.findText(saved_model)
                    if index >= 0:
                        self.model_selector.setCurrentIndex(index)
                    
        except Exception as e:
            logger.error(f"Error al cargar historial: {e}") 