from pydantic import BaseModel

class RunRequest(BaseModel):
    prompt: str