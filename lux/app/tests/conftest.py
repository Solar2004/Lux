import pytest
import os
from pathlib import Path
from ..database.database import init_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_db():
    """Crea una base de datos temporal para pruebas"""
    db_path = Path("test.db")
    if db_path.exists():
        db_path.unlink()
    
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    if db_path.exists():
        db_path.unlink()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configura variables de entorno para pruebas"""
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'
    yield
    os.environ.pop('TESTING', None)
    os.environ.pop('DATABASE_URL', None) 