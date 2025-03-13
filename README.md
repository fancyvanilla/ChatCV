# ChatCV  

ChatCV is a Streamlit app that allows recruiters to parse and interact with resumes using an AI-powered chat interface.  

## Setup Instructions  

### 1. Get Google OAuth Credentials  
To use this app, you need to obtain Google OAuth credentials. Follow these steps:  
- Create a Google OAuth application and grant it the following scopes:  
  - `openid`  
  - `https://www.googleapis.com/auth/userinfo.profile`  
  - `https://www.googleapis.com/auth/userinfo.email`  
  - `https://www.googleapis.com/auth/gmail.readonly`  
- Download the generated JSON credentials file.  
- Store the absolute path of this file in an `.env` file.  

### 2. Set Up a Virtual Env and Environment Variables  
### 3. Run the App via the Command:  
```bash
streamlit run app.py
```
## Highlights
- Authentication Security: Currently, the refresh token is stored in a cookie. A more secure storage method should be implemented.
- Retrieval-Augmented Generation (RAG): The system refines responses using two rounds of LLM processing and stores each CV as a structured document.
- File Handling: For testing purposes, PDFs are stored locally before being parsed.

Feel free to contribute or suggest improvements! 🚀


