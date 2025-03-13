import streamlit as st
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from .token_manager import AuthTokenManager
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from .jwt_types import TokenInfos

class Authentificator:
    def __init__(
            self,
            secret_path:str,
            redirect_uri:str,
            token_key:str,
            cookie_name:str="auth_jwt",
            token_duration_days:int=30, 
    ):
        self.secret_path = secret_path
        self.redirect_uri = redirect_uri
        self.token_key = token_key
        st.session_state["connected"]=st.session_state.get("connected",False)
        self.token_duration_days = token_duration_days
        self.token_manager = AuthTokenManager(cookie_name,token_key,token_duration_days)

    
    def initialize_flow(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.secret_path,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/gmail.readonly",
            ],
        )
        flow.redirect_uri = self.redirect_uri
        return flow
    # Sets up the auth url redirection if the user is not logged in
    def login(self):
        if not st.session_state["connected"]:
            flow = self.initialize_flow()
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
            )
            st.link_button("login with google",auth_url)
    
    #completes the ouath flow or do nothing in case the user is connected or logged out
    def check_login(self):
        if st.session_state["connected"]:
            return
        if st.session_state.get("logout",False):
            st.toast(":red[You are disconnected!]")
            return
        token=self.token_manager.get_token()
        if token is not None:
            st.query_params.clear()
            st.session_state["connected"]=True
            st.session_state["user_infos"]={
                "oauth_id":token.get("oauth_id"),
                "email":token.get("email"),
                "name":token.get("name"),
                "tokens":token.get("tokens"),
            }
            st.rerun()
        time.sleep(1)
        auth_code=st.query_params.get("code")
        st.query_params.clear()
        if auth_code:
            flow = self.initialize_flow()
            access_token=flow.fetch_token(code=auth_code)
            try:
                tokens=TokenInfos(
                    access_token=access_token.get("access_token"),
                    refresh_token=access_token.get("refresh_token", None),
                    expires_at=access_token.get("expires_at")
                ).model_dump()
                
             # An exception is generated here because we only get the refresh token once so we need to store it in some persistent storage like a db
            except Exception as e:
                 st.write("Error: ",e)
                 st.write("Manually clean all the cache and try again")
                 st.stop()
            creds = flow.credentials
            oauth_service = build(serviceName="oauth2", version="v2", credentials=creds)
            user_info = oauth_service.userinfo().get().execute()
            self.token_manager.set_token(user_info.get("id"), user_info.get("name"), user_info.get("email"), tokens)
            st.session_state["connected"]=True
            st.session_state["user_infos"]={
                "name":user_info.get("name"),
                "email":user_info.get("email"),
                "oauth_id":user_info.get("id"),
                "tokens":tokens
            }
    
    def logout(self):
        self.token_manager.delete_token()
        st.session_state["connected"]=False
        st.session_state["user_infos"]=None
        st.session_state["logout"]=True
        st.rerun()
    
    def check_access_token(self):
        if st.session_state["connected"]:
            user_infos=st.session_state["user_infos"]
            token_infos=user_infos.get("tokens")
            if token_infos:
            # checks if token is valid
                if token_infos.get("expires_at") > time.time():
                    return 
                flow = self.initialize_flow()
                creds=Credentials(
                    token=token_infos.get("access_token"),
                    refresh_token=token_infos.get("refresh_token"),
                    token_uri=flow.client_config["token_uri"],
                    client_id=flow.client_config["client_id"],
                    client_secret=flow.client_config["client_secret"],
                    scopes=flow.oauth2session.scope
                )
                request = Request()
                creds.refresh(request)
                token_infos["access_token"]=creds.token
                token_infos["expires_at"]=creds.expiry.timestamp()
                token_infos["refresh_token"]=creds.refresh_token
                self.token_manager.set_token(user_infos.get("oauth_id"), user_infos.get("name"), user_infos.get("email"), token_infos)
                st.session_state["user_infos"]["tokens"]=token_infos
        