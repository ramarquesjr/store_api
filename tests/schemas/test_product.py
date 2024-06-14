from pydantic import ValidationError
from store.schemas.product import ProductIn
from tests.factories import product_data
from uuid import UUID
import pytest


def test_schemas_validated_success():
    data = product_data()

    product = ProductIn.model_validate(data)
    assert product.name == "Iphone 14 Pro"
    assert isinstance(product.id, UUID)


def test_schemas_return_raise():
    data = product_data()
    del data["status"]

    with pytest.raises(ValidationError) as err:
        ProductIn.model_validate(data)

    assert err.value.errors()[0] == {
        "type": "missing",
        "loc": ("status",),
        "msg": "Field required",
        "input": {"name": "Iphone 14 Pro", "quantity": 10, "price": 8.5},
        "url": "https://errors.pydantic.dev/2.7/v/missing",
    }
