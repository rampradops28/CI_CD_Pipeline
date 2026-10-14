import pytest
from pydantic import ValidationError

from app.config import Settings
from app.main import ItemCreate
from app.models.item import Item


@pytest.mark.unit
def test_settings_defaults():
    """Test configuration settings have safe defaults."""
    s = Settings()
    assert s.app_port == 8000
    assert "test_db" in s.database_url or "postgresql" in s.database_url


@pytest.mark.unit
def test_item_create_schema_valid():
    """Test ItemCreate accepts valid payload."""
    payload = ItemCreate(name="Kubernetes Book", description="Comprehensive Guide")
    assert payload.name == "Kubernetes Book"
    assert payload.description == "Comprehensive Guide"


@pytest.mark.unit
def test_item_create_schema_requires_name():
    """Test ItemCreate rejects payload without name."""
    with pytest.raises(ValidationError):
        ItemCreate.model_validate({})


@pytest.mark.unit
def test_item_orm_model_instantiation():
    """Test Item SQLAlchemy model instantiation."""
    item = Item(name="Docker Container", description="Lightweight OCI")
    assert item.name == "Docker Container"
    assert item.description == "Lightweight OCI"
