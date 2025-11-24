import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="Login OneDrive", layout="centered")

CLIENT_ID = st.secrets["onedrive"]["client_id"]
CLIENT_SECRET = st.secrets["onedrive"]["client_secret"]
REDIRECT_URI = st.secrets["onedrive"]["redirect_uri"]
TENANT_ID = st.secrets["onedrive"]["tenant_id"]

AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": "offline_access Files.Read Files.ReadWrite Files.Read.All User.Read",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)

st.title("Conexión OneDrive Personal (MSA)")
st.write("Haz clic para iniciar sesión con tu cuenta PERSONAL:")

st.markdown(f"[**Iniciar sesión con Microsoft**]({get_auth_url()})")

# Captura 'code' al regresar del login
query_params = st.experimental_get_query_params()
if "code" in query_params:
    code = query_params["code"][0]

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    token_res = requests.post(TOKEN_URL, data=data)
    token_json = token_res.json()

    if "access_token" not in token_json:
        st.error("Error obteniendo token. Revisa los secrets.")
        st.write(token_json)
    else:
        st.success("🔥 LOGIN EXITOSO 🔥")
        st.json(token_json)

