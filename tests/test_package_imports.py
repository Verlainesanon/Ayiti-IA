"""
Test d'importation du nouveau package ayiti_ai.
Ce test vérifie que tous les sous-modules du package sont importables.
"""
import pytest


def test_imports_ayiti_ai():
    """Vérifie que le package principal est importable."""
    try:
        import ayiti_ai  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import du package principal a échoué : {e}")


def test_imports_ayiti_ai_data():
    """Vérifie que le sous-module data est importable."""
    try:
        from ayiti_ai import data  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.data a échoué : {e}")


def test_imports_ayiti_ai_models():
    """Vérifie que le sous-module models est importable."""
    try:
        from ayiti_ai import models  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.models a échoué : {e}")


def test_imports_ayiti_ai_training():
    """Vérifie que le sous-module training est importable."""
    try:
        from ayiti_ai import training  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.training a échoué : {e}")


def test_imports_ayiti_ai_evaluation():
    """Vérifie que le sous-module evaluation est importable."""
    try:
        from ayiti_ai import evaluation  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.evaluation a échoué : {e}")


def test_imports_ayiti_ai_inference():
    """Vérifie que le sous-module inference est importable."""
    try:
        from ayiti_ai import inference  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.inference a échoué : {e}")


def test_imports_ayiti_ai_guardrails():
    """Vérifie que le sous-module guardrails est importable."""
    try:
        from ayiti_ai import guardrails  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.guardrails a échoué : {e}")


def test_imports_ayiti_ai_rag():
    """Vérifie que le sous-module rag est importable."""
    try:
        from ayiti_ai import rag  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.rag a échoué : {e}")


def test_imports_ayiti_ai_utils():
    """Vérifie que le sous-module utils est importable."""
    try:
        from ayiti_ai import utils  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Import de ayiti_ai.utils a échoué : {e}")


def test_package_version():
    """Vérifie que la version du package est définie."""
    import ayiti_ai
    assert hasattr(ayiti_ai, "__version__"), "Le package doit avoir un attribut __version__"
    assert isinstance(ayiti_ai.__version__, str), "__version__ doit être une chaîne"
    assert ayiti_ai.__version__ == "0.1.0"
