import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

def test_chat_with_gemini(ai_service):
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = "Respuesta de prueba"
        mock_generate.return_value = mock_response
        
        response = ai_service.chat_with_gemini("Hola")
        assert response == "Respuesta de prueba"

def test_code_assistance(ai_service):
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "```python\ndef test():\n    pass\n```\nExplicación del código"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        result = ai_service.code_assistance("Escribe una función de prueba")
        assert "code" in result
        assert "explanation" in result

def test_analyze_task(ai_service):
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = "Análisis de prueba"
        mock_generate.return_value = mock_response
        
        result = ai_service.analyze_task("Crear presentación para mañana")
        assert isinstance(result, dict)
        assert "priority" in result
        assert "category" in result

def test_generate_task_suggestions(ai_service):
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = "Tarea 1\nTarea 2\nTarea 3"
        mock_generate.return_value = mock_response
        
        tasks = [
            {"title": "Tarea anterior", "category": "trabajo"}
        ]
        
        suggestions = ai_service.generate_task_suggestions(tasks)
        assert len(suggestions) > 0
        assert isinstance(suggestions, list)

def test_rate_limit_check(ai_service):
    assert ai_service.rate_limit_check() == True 