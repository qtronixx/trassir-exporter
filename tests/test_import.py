# tests/test_import.py
def test_import():
    """Проверяет, что модуль импортируется без ошибок"""
    try:
        import trassir_exporter
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"
