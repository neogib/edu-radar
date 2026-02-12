from pydantic import ConfigDict
from sqlmodel import SQLModel


class APIResponseConfig(SQLModel):
    """
    Mixin to force Pydantic to include nullable fields with default values
    in the generated OpenAPI schema (required keys, nullable values).
    """

    model_config: ConfigDict = ConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        json_schema_serialization_defaults_required=True
    )
