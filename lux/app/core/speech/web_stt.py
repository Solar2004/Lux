from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging
import time

logger = logging.getLogger('lux')

class WebSTTService:
    """Servicio de reconocimiento de voz basado en web"""
    
    def __init__(self, language: str = "es-ES"):
        self.language = language
        self.chrome_options = Options()
        self.chrome_options.add_argument("--use-fake-ui-for-media-stream")
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--log-level=3")  # Minimizar logs de Chrome
        self.driver = None
        self.wait = None
        self.is_initialized = False
        self.callback = None
        self.is_listening = False
        self.error_count = 0
        self.MAX_ERRORS = 3
        
    def initialize(self):
        """Inicializa el servicio web"""
        try:
            if self.is_initialized:
                return
                
            logger.info("Iniciando WebSTT...")
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            self.driver.get("https://realtime-stt-devs-do-code.netlify.app/")
            
            # Esperar elementos críticos
            self.wait.until(EC.presence_of_element_located((By.ID, "language_select")))
            self.wait.until(EC.presence_of_element_located((By.ID, "click_to_record")))
            
            self._select_language()
            self.driver.find_element(By.ID, "click_to_record").click()
            
            self.is_initialized = True
            self.error_count = 0
            logger.info("WebSTT inicializado correctamente")
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error al inicializar WebSTT ({self.error_count}/{self.MAX_ERRORS}): {e}")
            self.cleanup()
            
            if self.error_count >= self.MAX_ERRORS:
                logger.error("Demasiados errores en WebSTT, deteniendo servicio")
                raise RuntimeError("WebSTT service failed to initialize")
            
            time.sleep(2)  # Esperar antes de reintentar
            self.initialize()  # Reintentar inicialización
    
    def _select_language(self):
        """Selecciona el idioma"""
        self.driver.execute_script(
            f"""
            var select = document.getElementById('language_select');
            select.value = '{self.language}';
            select.dispatchEvent(new Event('change'));
            """
        )
    
    def start_listening(self, callback):
        """Inicia la escucha continua"""
        self.callback = callback
        self.is_listening = True
        self.initialize()
        logger.info("WebSTT iniciado")
    
    def stop_listening(self):
        """Detiene la escucha"""
        self.is_listening = False
        self.cleanup()
        logger.info("WebSTT detenido")
    
    def get_text(self) -> str:
        """Obtiene el texto reconocido"""
        try:
            if not self.is_initialized:
                self.initialize()
                
            text = self.driver.find_element(By.ID, "convert_text").text
            if text:
                logger.debug(f"Texto reconocido: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error al obtener texto: {e}")
            self.error_count += 1
            
            if self.error_count >= self.MAX_ERRORS:
                logger.error("Demasiados errores en reconocimiento, reiniciando servicio")
                self.cleanup()
                self.initialize()
                
            return ""
    
    def is_recording(self) -> bool:
        """Verifica si está grabando"""
        element = self.driver.find_element(By.ID, "is_recording")
        return element.text.startswith("Recording: True")
    
    def cleanup(self):
        """Limpia recursos"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_initialized = False 