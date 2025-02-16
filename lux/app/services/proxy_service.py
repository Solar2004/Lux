import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger('lux')

class ProxyService:
    def __init__(self):
        self.proxy_file = Path("resources/proxies/working_proxies.txt")
        self.proxy_file.parent.mkdir(parents=True, exist_ok=True)
        self.working_proxies: List[str] = []
        self._load_proxies()
    
    def _load_proxies(self):
        """Carga proxies desde el archivo"""
        try:
            if self.proxy_file.exists():
                with open(self.proxy_file, 'r') as f:
                    self.working_proxies = [line.strip() for line in f if line.strip()]
                logger.info(f"Cargados {len(self.working_proxies)} proxies")
            else:
                self.update_proxies()
        except Exception as e:
            logger.error(f"Error cargando proxies: {e}")
    
    def _check_proxy(self, proxy: str, timeout: int = 2) -> Optional[Tuple[str, float]]:
        """Verifica si un proxy funciona"""
        start_time = time.perf_counter()
        try:
            with requests.Session() as session:
                response = session.head(
                    "https://www.google.com/",
                    proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
                    timeout=timeout
                )
                elapsed_time = time.perf_counter() - start_time
                if response.status_code == 200 and elapsed_time <= timeout:
                    logger.debug(f"Proxy válido: {proxy} ({elapsed_time:.2f}s)")
                    return proxy, elapsed_time
        except Exception as e:
            logger.debug(f"Proxy inválido {proxy}: {e}")
        return None
    
    def update_proxies(self, number_of_proxies: int = 100, timeout: int = 2):
        """Actualiza la lista de proxies"""
        try:
            logger.info("Actualizando lista de proxies...")
            resp = requests.get(
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            )
            proxies = [p.strip() for p in resp.text.strip().split("\n")[:number_of_proxies] if p.strip()]
            
            working_proxies = []
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {
                    executor.submit(self._check_proxy, proxy, timeout): proxy 
                    for proxy in proxies
                }
                
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        working_proxies.append(result[0])
            
            # Guardar proxies funcionando
            with open(self.proxy_file, 'w') as f:
                f.write('\n'.join(working_proxies))
            
            self.working_proxies = working_proxies
            logger.info(f"Encontrados {len(working_proxies)} proxies funcionando")
            
        except Exception as e:
            logger.error(f"Error actualizando proxies: {e}")
    
    def get_proxy(self) -> Optional[str]:
        """Obtiene un proxy aleatorio de la lista"""
        import random
        if not self.working_proxies:
            self.update_proxies()
        return random.choice(self.working_proxies) if self.working_proxies else None
    
    def get_all_proxies(self) -> List[str]:
        """Retorna todos los proxies disponibles"""
        if not self.working_proxies:
            self.update_proxies()
        return self.working_proxies.copy() 