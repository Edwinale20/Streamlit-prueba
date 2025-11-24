import streamlit as st
import requests
import io
import pandas as pd

# ---------- Config desde secrets ----------

TENANT_ID = st.secrets["azure"]["tenant_id"]
CLIENT_ID = st.secrets["azure"]["client_id"]
CLIENT_SECRET = st.secrets["azure"]["client_secret"]

USER_ID = st.secrets["onedrive"]["user_id"]
CARPETA = st.secrets["onedrive"]["carpeta"]
ARCHIVO = st.secrets["onedrive"]["archivo"]

# ---------- Función para obtener token (client_credentials) ----------

def get_access_token():
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default",  # usa los permisos que ya aprobó el admin
    }

    resp = requests.post(token_url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

# ---------- Función para descargar el archivo de OneDrive ----------

def leer_excel_onedrive():
    access_token = get_access_token()

    # Ruta al archivo en OneDrive del usuario (business)
    # Graph: /users/{user-id}/drive/root:/Carpeta/archivo:/content  :contentReference[oaicite:7]{index=7}
    file_path = f"/{CARPETA}/{ARCHIVO}"
    graph_url = (
        f"https://graph.microsoft.com/v1.0/users/{USER_ID}"
        f"/drive/root:{file_path}:/content"
    )

    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(graph_url, headers=headers)
    resp.raise_for_status()

    return pd.read_excel(io.BytesIO(resp.content))

# ---------- Streamlit UI ----------

st.title("Prueba OneDrive 365 + Streamlit")

st.write("Leyendo archivo desde OneDrive for Business…")

try:
    df = leer_excel_onedrive()
    st.success("Archivo leído correctamente desde OneDrive ✅")
    st.dataframe(df)
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
