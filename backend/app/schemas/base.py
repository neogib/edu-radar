from typing import ClassVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CustomBaseModel(BaseModel):
    """
    Custom model for use in API schemas.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        json_schema_serialization_defaults_required=True,  # to force Pydantic to include nullable fields with default values
    )
