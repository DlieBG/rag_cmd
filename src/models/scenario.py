from src.models.schema import SchemaType
from src.models.chat import LLMType
from pydantic import BaseModel
from typing import Optional

class Scenario(BaseModel):
    questions: list[str]
    llm_type: LLMType
    override_schema: bool
    override_schema_type: Optional[SchemaType] = None
