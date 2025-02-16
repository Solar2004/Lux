def test_verify_function_request(ai_manager):
    # Test función existente
    result = ai_manager.verify_function_request("crea una tarea para comprar leche")
    assert result["type"] == "YES"
    assert result["function_name"] == "crear_tarea"
    assert "leche" in result["extra_info"]
    
    # Test función nueva
    result = ai_manager.verify_function_request("necesito una función para enviar emails")
    assert result["type"] == "NEW"
    assert "email" in result["function_name"]
    assert result["description"]
    
    # Test no función
    result = ai_manager.verify_function_request("hola, ¿cómo estás?")
    assert result["type"] == "NO" 