import re
from pydantic import BaseModel, Field, field_validator

_HOST_LABEL = re.compile(r"^(?=.{1,63}$)[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$")

def normalize_hostname(value: str) -> str:
    value = value.strip().rstrip(".").lower()
    if not value or len(value) > 253 or "/" in value or ":" in value or "@" in value:
        raise ValueError("Provide a DNS hostname only; URLs, ports and IP literals are not accepted.")
    labels = value.split(".")
    if len(labels) < 2 or any(not _HOST_LABEL.fullmatch(label) for label in labels):
        raise ValueError("Enter a valid fully-qualified DNS hostname, such as example.com.")
    if all(label.isdigit() for label in labels):
        raise ValueError("IP addresses are not accepted by this hostname-only assessment profile.")
    return value

class AssetCreate(BaseModel):
    hostname: str = Field(min_length=3, max_length=253)
    display_name: str = Field(default="", max_length=120)
    authorized: bool = False
    authorization_note: str = Field(default="", max_length=2000)

    @field_validator("hostname")
    @classmethod
    def valid_hostname(cls, value):
        return normalize_hostname(value)

    @field_validator("authorized")
    @classmethod
    def require_authorization_note(cls, value, info):
        # Cross-field validation is enforced in the route for a clear error message.
        return value

class AssetOut(BaseModel):
    id: int
    hostname: str
    display_name: str
    authorized: bool
    authorization_note: str
    model_config = {"from_attributes": True}

class JobOut(BaseModel):
    id: int
    asset_id: int
    profile: str
    status: str
    findings: list
    error: str
    model_config = {"from_attributes": True}
