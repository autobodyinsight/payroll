from pydantic import BaseModel

class ParsedItem(BaseModel):
    operation: str
    labor_time: float
    category: str