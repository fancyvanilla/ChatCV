import extra_streamlit_components as stx
import datetime
import jwt
import streamlit as st
from .jwt_types import JWTDATA,TokenInfos

class AuthTokenManager:
    def __init__(
        self,
        cookie_name:str,
        token_key:str,
        token_duration_days:int
    ):
        self.cookie_name = cookie_name
        self.token_key = token_key
        self.token_duration_days = token_duration_days
        self.cookie_manager = stx.CookieManager()
        self.token=None
    
    def set_token(self, oauth_id:str, name:str, email:str, tokens:TokenInfos):
        exp_date=(
            datetime.datetime.now()+
            datetime.timedelta(days=self.token_duration_days)
        )
        jwt_data=JWTDATA(
            oauth_id=oauth_id,
            name=name,
            email=email,
            tokens=tokens
        )
        self.token=self._encode_token(jwt_data)
        self.cookie_manager.set(
            self.cookie_name,
            self.token,
            expires_at=exp_date,
            secure=True, # sent only in https connections
            same_site="Lax", # adds csrf protection
            path="/" # cookie is available in all tabs
            )
    
    def get_token(self):
        self.token=self.cookie_manager.get(self.cookie_name)
        if self.token is None:
            return None
        self.token = self._decode_token()
        return self.token

    
    def delete_token(self):
        try:
          self.cookie_manager.delete(self.cookie_name)
        except KeyError:
          st.error("Token not found")

    def _encode_token(self,data:JWTDATA)->str:
        encoded=jwt.encode(data.model_dump(), self.token_key, algorithm="HS256")
        return encoded
    
    def _decode_token(self):
        try:
            decoded=jwt.decode(self.token,self.token_key,algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            self.delete_token()
            
