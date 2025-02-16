from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QPushButton, QLabel, QTextEdit, QComboBox, QWidget, QGroupBox, QTreeWidget, QTreeWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
import logging
from ...utils.logger import LuxLogger
from pathlib import Path

class ControlPanel(QDialog):
    def __init__(self, voice_manager, ai_manager, media_player, parent=None):
        super().__init__(parent)
        self.voice_manager = voice_manager
        self.ai_manager = ai_manager
        self.media_player = media_player
        
        self.setWindowTitle("Panel de Control")
        self.setMinimumSize(800, 600)
        
        # Configurar ventana no modal
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            Qt.WindowType.Window |  # Ventana independiente
            Qt.WindowType.WindowStaysOnTopHint |  # Siempre visible
            Qt.WindowType.WindowCloseButtonHint |  # Botón de cerrar
            Qt.WindowType.WindowMinimizeButtonHint  # Botón de minimizar
        )
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab de Logs
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)
        
        # Widget de logs
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        log_layout.addWidget(self.log_widget)
        
        # Configurar logger
        LuxLogger.setup(self.log_widget)
        
        # Botones de control de logs
        log_buttons = QHBoxLayout()
        
        clear_button = QPushButton("Limpiar Logs")
        clear_button.clicked.connect(self.log_widget.clear)
        log_buttons.addWidget(clear_button)
        
        log_level = QComboBox()
        log_level.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        log_level.setCurrentText('INFO')
        log_level.currentTextChanged.connect(self._change_log_level)
        log_buttons.addWidget(log_level)
        
        log_layout.addLayout(log_buttons)
        
        self.tabs.addTab(self.log_tab, "Logs")
        
        # Tab de Logs de Funciones
        self.function_log_tab = QWidget()
        function_log_layout = QVBoxLayout(self.function_log_tab)
        
        # Widget de logs de funciones
        self.function_log_widget = QTextEdit()
        self.function_log_widget.setReadOnly(True)
        self.function_log_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        function_log_layout.addWidget(self.function_log_widget)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        clear_button = QPushButton("Limpiar")
        clear_button.clicked.connect(self.function_log_widget.clear)
        buttons_layout.addWidget(clear_button)
        
        # Filtros de tipo de log
        filter_combo = QComboBox()
        filter_combo.addItems(["Todo", "Análisis", "Ejecución", "Errores"])
        filter_combo.currentTextChanged.connect(self._filter_function_logs)
        buttons_layout.addWidget(filter_combo)
        
        function_log_layout.addLayout(buttons_layout)
        
        self.tabs.addTab(self.function_log_tab, "Function Logs")
        
        # Tab de Voz
        voice_tab = self._setup_voice_tab()
        self.tabs.addTab(voice_tab, "Voz")
        
        # Tab de AI
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        
        # Estado de AI
        ai_status = QLabel(f"Modelo: {ai_manager.get_available_models()[0]}")
        ai_layout.addWidget(ai_status)
        
        # Pruebas de modelos
        models_group = QGroupBox("Pruebas de Modelos")
        models_layout = QVBoxLayout()
        
        # Gemini
        gemini_layout = QHBoxLayout()
        test_gemini = QPushButton("Probar Gemini")
        test_gemini.clicked.connect(self._test_gemini)
        gemini_layout.addWidget(test_gemini)
        
        self.gemini_status = QLabel("No probado")
        gemini_layout.addWidget(self.gemini_status)
        models_layout.addLayout(gemini_layout)
        
        # OpenRouter (Deepseek)
        if "deepseek" in ai_manager.get_available_models():
            deepseek_layout = QHBoxLayout()
            test_deepseek = QPushButton("Probar Deepseek")
            test_deepseek.clicked.connect(self._test_deepseek)
            deepseek_layout.addWidget(test_deepseek)
            
            self.deepseek_status = QLabel("No probado")
            deepseek_layout.addWidget(self.deepseek_status)
            models_layout.addLayout(deepseek_layout)
        
        models_group.setLayout(models_layout)
        ai_layout.addWidget(models_group)
        
        # Resultado de pruebas
        self.ai_result = QTextEdit()
        self.ai_result.setReadOnly(True)
        self.ai_result.setMaximumHeight(100)
        ai_layout.addWidget(self.ai_result)
        
        ai_layout.addStretch()
        self.tabs.addTab(ai_tab, "AI")
        
        # Agregar tab de Funciones
        functions_tab = self._setup_functions_tab()
        self.tabs.addTab(functions_tab, "Funciones")
        
        # Botón de cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        # Estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #3E3E3E;
                background-color: #2D2D2D;
            }
            QTabBar::tab {
                background-color: #2D2D2D;
                color: #FFFFFF;
                padding: 8px 16px;
                border: 1px solid #3E3E3E;
            }
            QTabBar::tab:selected {
                background-color: #3D3D3D;
            }
            QTextEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                padding: 4px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
        """)
        
        # Inicializar logs
        logging.info("Panel de control abierto")
        
        # Configurar handler especial para logs de funciones
        self._setup_function_logger()
    
    def _change_log_level(self, level):
        """Cambia el nivel de log y filtra los mensajes existentes"""
        try:
            # Cambiar nivel de log
            numeric_level = getattr(logging, level)
            logging.getLogger('lux').setLevel(numeric_level)
            
            # Obtener todos los logs actuales
            current_logs = self.log_widget.toPlainText().split('\n')
            
            # Filtrar logs según el nivel seleccionado
            filtered_logs = []
            levels = {
                'DEBUG': 0,
                'INFO': 1,
                'WARNING': 2,
                'ERROR': 3
            }
            selected_level = levels[level]
            
            for log in current_logs:
                if any(lvl in log for lvl in list(levels.keys())[selected_level:]):
                    filtered_logs.append(log)
            
            # Actualizar widget
            self.log_widget.setPlainText('\n'.join(filtered_logs))
            
        except Exception as e:
            logging.error(f"Error al cambiar nivel de log: {e}")
    
    def _setup_voice_tab(self):
        """Configura la pestaña de voz"""
        voice_tab = QWidget()
        voice_layout = QVBoxLayout(voice_tab)
        
        # Selección de servicios
        services_group = QGroupBox("Servicios de Voz")
        services_layout = QVBoxLayout()
        
        # TTS Service
        tts_layout = QHBoxLayout()
        tts_layout.addWidget(QLabel("Servicio TTS:"))
        
        self.tts_combo = QComboBox()
        self.tts_combo.addItems(['simple', 'deepgram', 'elevenlabs'])
        self.tts_combo.setCurrentText(self.voice_manager.current_tts)
        self.tts_combo.currentTextChanged.connect(self._change_tts_service)
        tts_layout.addWidget(self.tts_combo)
        
        # Si es elevenlabs, mostrar selector de voces
        self.voice_combo = QComboBox()
        self.voice_combo.setVisible(False)
        tts_layout.addWidget(self.voice_combo)
        
        services_layout.addLayout(tts_layout)
        
        # STT Service
        stt_layout = QHBoxLayout()
        stt_layout.addWidget(QLabel("Servicio STT:"))
        
        self.stt_combo = QComboBox()
        self.stt_combo.addItems(['simple', 'web'])
        self.stt_combo.setCurrentText(self.voice_manager.current_stt)
        self.stt_combo.currentTextChanged.connect(self._change_stt_service)
        stt_layout.addWidget(self.stt_combo)
        
        services_layout.addLayout(stt_layout)
        services_group.setLayout(services_layout)
        voice_layout.addWidget(services_group)
        
        # Estado y pruebas
        status_layout = QHBoxLayout()
        self.voice_status = QLabel(f"Estado: {'Escuchando' if self.voice_manager.is_listening else 'Pausado'}")
        status_layout.addWidget(self.voice_status)
        voice_layout.addLayout(status_layout)
        
        # Botones de prueba
        test_layout = QVBoxLayout()
        
        test_tts = QPushButton("Probar TTS")
        test_tts.clicked.connect(self._test_tts)
        test_layout.addWidget(test_tts)
        
        test_stt = QPushButton("Probar STT")
        test_stt.clicked.connect(self._test_stt)
        test_layout.addWidget(test_stt)
        
        # Botón actualizar proxies
        update_proxies = QPushButton("Actualizar Proxies")
        update_proxies.clicked.connect(self._update_proxies)
        test_layout.addWidget(update_proxies)
        
        voice_layout.addLayout(test_layout)
        voice_layout.addStretch()
        
        return voice_tab
    
    def _change_tts_service(self, service):
        """Cambia el servicio TTS"""
        try:
            self.voice_manager.set_tts_service(service)
            logging.info(f"Servicio TTS cambiado a: {service}")
            
            # Actualizar selector de voces si es ElevenLabs
            if service == 'elevenlabs':
                self.voice_combo.clear()
                self.voice_combo.addItems([
                    'daniel', 'emily', 'dave', 'charlie', 'callum',
                    'clyde', 'fin', 'freya', 'gigi', 'giovanni'
                ])
                self.voice_combo.setVisible(True)
                # Conectar cambio de voz
                self.voice_combo.currentTextChanged.connect(self._change_elevenlabs_voice)
            else:
                self.voice_combo.setVisible(False)
                
        except Exception as e:
            logging.error(f"Error al cambiar servicio TTS: {e}")
    
    def _change_elevenlabs_voice(self, voice_name):
        """Cambia la voz de ElevenLabs"""
        try:
            service = self.voice_manager.tts_services['elevenlabs']
            service.current_voice = voice_name
            logging.info(f"Voz de ElevenLabs cambiada a: {voice_name}")
        except Exception as e:
            logging.error(f"Error al cambiar voz de ElevenLabs: {e}")
    
    def _change_stt_service(self, service):
        """Cambia el servicio STT"""
        try:
            self.voice_manager.set_stt_service(service)
            logging.info(f"Servicio STT cambiado a: {service}")
            self.voice_status.setText(f"Estado: {'Escuchando' if self.voice_manager.is_listening else 'Pausado'}")
        except Exception as e:
            logging.error(f"Error al cambiar servicio STT: {e}")
    
    def _test_tts(self):
        """Prueba el sistema TTS"""
        try:
            test_text = "Hola, soy Luxion. Esta es una prueba del sistema de voz."
            logging.info("Probando TTS...")
            self.voice_manager.speak(test_text)
            logging.info("Prueba TTS completada")
        except Exception as e:
            logging.error(f"Error en prueba TTS: {e}")
    
    def _test_stt(self):
        """Prueba el sistema STT"""
        try:
            logging.info("Iniciando prueba STT (habla algo)...")
            # Aquí podríamos implementar una prueba específica de STT
        except Exception as e:
            logging.error(f"Error en prueba STT: {e}")
    
    def _test_gemini(self):
        """Prueba el modelo Gemini"""
        try:
            self.gemini_status.setText("Probando...")
            test_prompt = "¿Cuál es tu nombre y qué puedes hacer?"
            logging.info(f"Probando Gemini con prompt: {test_prompt}")
            response = self.ai_manager.chat(test_prompt)
            logging.info(f"Respuesta Gemini: {response}")
            self.ai_result.setText(f"Gemini: {response}")
            self.gemini_status.setText("OK")
            self.voice_manager.speak(response)
        except Exception as e:
            self.gemini_status.setText("Error")
            logging.error(f"Error en prueba Gemini: {e}")
    
    def _test_deepseek(self):
        """Prueba el modelo Deepseek"""
        try:
            self.deepseek_status.setText("Probando...")
            test_prompt = "¿Cuál es tu nombre y qué puedes hacer?"
            logging.info(f"Probando Deepseek con prompt: {test_prompt}")
            # TODO: Implementar llamada a Deepseek
            response = "Hola, soy Deepseek. Esta es una prueba."
            logging.info(f"Respuesta Deepseek: {response}")
            self.ai_result.setText(f"Deepseek: {response}")
            self.deepseek_status.setText("OK")
            self.voice_manager.speak(response)
        except Exception as e:
            self.deepseek_status.setText("Error")
            logging.error(f"Error en prueba Deepseek: {e}")
    
    def _update_proxies(self):
        """Actualiza la lista de proxies"""
        try:
            service = self.voice_manager.tts_services['elevenlabs']
            service.proxy_service.update_proxies()
            logging.info("Proxies actualizados correctamente")
        except Exception as e:
            logging.error(f"Error actualizando proxies: {e}")
    
    def _setup_function_logger(self):
        """Configura el logger específico para funciones"""
        class FunctionLogHandler(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
                self.setFormatter(logging.Formatter(
                    '%(asctime)s - %(levelname)s\n%(message)s\n',
                    datefmt='%H:%M:%S'
                ))
            
            def emit(self, record):
                # Solo procesar logs del logger 'lux.functions'
                if record.name != 'lux.functions':
                    return
                
                msg = self.format(record)
                # Dar color según el tipo de mensaje
                color = {
                    'DEBUG': '#808080',
                    'INFO': '#4CAF50',
                    'WARNING': '#FFC107',
                    'ERROR': '#F44336'
                }.get(record.levelname, '#FFFFFF')
                
                # Formatear mensaje
                formatted_msg = f'<div style="color: {color}; margin: 2px 0;">{msg}</div>'
                
                # Agregar separadores visuales
                if "ANÁLISIS DE SOLICITUD" in record.message:
                    self.widget.append('<div style="border-top: 1px solid #666; margin: 10px 0;"></div>')
                    formatted_msg = f'<div style="color: #42A5F5; font-weight: bold;">{msg}</div>'
                elif "CREACIÓN DE NUEVA FUNCIÓN" in record.message:
                    formatted_msg = f'<div style="color: #66BB6A; font-weight: bold;">{msg}</div>'
                
                self.widget.append(formatted_msg)
                self.widget.verticalScrollBar().setValue(
                    self.widget.verticalScrollBar().maximum()
                )
        
        # Configurar logger
        function_logger = logging.getLogger('lux.functions')
        function_logger.setLevel(logging.DEBUG)
        function_logger.propagate = False  # No propagar logs al logger padre
        
        # Limpiar handlers existentes
        for handler in function_logger.handlers[:]:
            function_logger.removeHandler(handler)
        
        # Agregar nuevo handler
        handler = FunctionLogHandler(self.function_log_widget)
        function_logger.addHandler(handler)
    
    def _filter_function_logs(self, filter_type: str):
        """Filtra los logs según el tipo seleccionado"""
        current_text = self.function_log_widget.toPlainText()
        filtered_lines = []
        
        for line in current_text.split('\n'):
            if filter_type == "Todo":
                filtered_lines.append(line)
            elif filter_type == "Análisis" and "ANÁLISIS DE SOLICITUD" in line:
                filtered_lines.append(line)
            elif filter_type == "Ejecución" and "Iniciando ejecución" in line:
                filtered_lines.append(line)
            elif filter_type == "Errores" and "ERROR" in line:
                filtered_lines.append(line)
        
        self.function_log_widget.setPlainText('\n'.join(filtered_lines))
    
    def _setup_functions_tab(self):
        """Configura la pestaña de funciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de funciones
        self.functions_list = QTreeWidget()
        self.functions_list.setHeaderLabels(["Función", "Descripción"])
        self.functions_list.setColumnWidth(0, 200)
        self.functions_list.setAlternatingRowColors(True)
        layout.addWidget(self.functions_list)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Actualizar Lista")
        refresh_btn.clicked.connect(self._refresh_functions_list)
        buttons_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("Eliminar Función")
        delete_btn.clicked.connect(self._delete_selected_function)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        # Estilo
        self.functions_list.setStyleSheet("""
            QTreeWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                font-family: 'Consolas', monospace;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #3D3D3D;
            }
        """)
        
        # Cargar funciones iniciales
        self._refresh_functions_list()
        
        return tab
    
    def _refresh_functions_list(self):
        """Actualiza la lista de funciones disponibles"""
        try:
            self.functions_list.clear()
            
            if not self.ai_manager.function_manager:
                return
            
            functions = self.ai_manager.function_manager.get_available_functions()
            for name, doc in functions.items():
                item = QTreeWidgetItem([name, doc or "Sin descripción"])
                self.functions_list.addTopLevelItem(item)
            
        except Exception as e:
            logging.error(f"Error actualizando lista de funciones: {e}")
    
    def _delete_selected_function(self):
        """Elimina la función seleccionada"""
        try:
            item = self.functions_list.currentItem()
            if not item:
                return
            
            function_name = item.text(0)
            
            # Confirmar eliminación
            reply = QMessageBox.question(
                self,
                'Confirmar Eliminación',
                f'¿Estás seguro de que quieres eliminar la función "{function_name}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Eliminar archivo
                function_path = Path("resources/functions") / f"{function_name}.py"
                if function_path.exists():
                    function_path.unlink()
                
                # Eliminar del registro
                if function_name in self.ai_manager.function_manager.functions:
                    del self.ai_manager.function_manager.functions[function_name]
                
                # Actualizar lista
                self._refresh_functions_list()
                logging.info(f"Función eliminada: {function_name}")
            
        except Exception as e:
            logging.error(f"Error eliminando función: {e}")
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        self.hide()  # Solo ocultar en lugar de cerrar
        event.ignore() 