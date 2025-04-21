from pydantic import BaseModel

class SampleCommand(BaseModel):
    id: str
    cypher: str
    tags: list[str]
    description: str

class SampleCommandCreate(BaseModel):
    cypher: str
    tags: list[str]
    description: str

class SampleCommandId(BaseModel):
    id: str
