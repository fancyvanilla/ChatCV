from pydantic import BaseModel

class TokenInfos(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: float

class JWTDATA(BaseModel):
    oauth_id: str
    name: str
    email: str
    tokens:TokenInfos 


