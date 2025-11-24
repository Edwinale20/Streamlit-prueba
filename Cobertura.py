import streamlit as st
import requests
import pandas as pd
import urllib.parse

st.set_page_config(page_title="OneDrive Personal", layout="centered")

# ------------------------
# CONFIG
# ------------------------
CLIENT_ID = st.secrets["onedrive"]["client_id"]
CLIENT_SECRET = st.secrets["onedrive"]["client_secret"]
REDIRECT_URI = st.secrets["onedrive"]["redirect_uri"]
TENANT_ID = "consumers"

AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"


# ------------------------
# LOGIN URL
# ------------------------
def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": "offline_access Files.Read Files.ReadWrite Files.Read.All User.Read",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


# ------------------------
# REFRESH TOKEN
# ------------------------
def refresh_token():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": st.session_state["refresh_token"],
        "redirect_uri": REDIRECT_URI,
    }
    r = requests.post(TOKEN_URL, data=data).json()
    st.session_state["access_token"] = r["access_token"]
    st.session_state["refresh_token"] = r["refresh_token"]


# ------------------------
# LISTAR ARCHIVOS
# ------------------------
def listar_archivos_carpeta(nombre_carpeta):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{nombre_carpeta}:/children"

    r = requests.get(url, headers=headers)

    # Si token expiró → refrescarlo
    if r.status_code == 401:
        refresh_token()
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        r = requests.get(url, headers=headers)

    return r.json()


# ------------------------
# UI
# ------------------------
st.title("📂 Conexión OneDrive Personal (MSA)")
st.write("Inicia sesión con tu cuenta personal:")

st.markdown(f"[Iniciar sesión con Microsoft]({get_auth_url()})")

# Captura del código al volver del login
params = st.experimental_get_query_params()
if "code" in params and "access_token" not in st.session_state:
    code = params["code"][0]

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    r = requests.post(TOKEN_URL, data=data).json()
    st.session_state["access_token"] = r["access_token"]
    st.session_state["refresh_token"] = r["refresh_token"]

    st.success("🔥 LOGIN EXITOSO 🔥")


# ------------------------
# MOSTRAR ARCHIVOS DE COBERTURA
# ------------------------
if "access_token" in st.session_state:
    st.subheader("📁 Archivos dentro de la carpeta 'cobertura'")

    data = listar_archivos_carpeta("cobertura")

    if "value" in data:
        for item in data["value"]:
            st.write("📄", item["name"])
    else:
        st.write("No se encontró la carpeta o está vacía.")
