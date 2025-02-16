import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .. import config
from .models import Base
from pathlib import Path
import os

logger = logging.getLogger('lux')

def init_db(force_reset: bool = False):
    """
    Inicializa la base de datos
    Args:
        force_reset: Si es True, borra la base de datos existente
    Returns:
        Session: Sesión de SQLAlchemy
    """
    try:
        # Crear directorio si no existe
        db_dir = Path("resources/database")
        db_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = db_dir / "lux.db"
        
        # Si force_reset, borrar DB existente
        if force_reset and db_path.exists():
            try:
                os.remove(db_path)
                logger.info("Base de datos existente eliminada")
            except Exception as e:
                logger.error(f"Error al eliminar base de datos: {e}")
        
        # Crear engine y tablas
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        
        # Crear sesión
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Base de datos inicializada correctamente")
        return session
        
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        raise

def get_session():
    """
    Obtiene una nueva sesión de base de datos.
    Útil cuando necesitamos una sesión fuera del contexto principal.
    """
    try:
        engine = create_engine(config.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        logger.error(f"Error al obtener sesión de base de datos: {str(e)}")
        raise
