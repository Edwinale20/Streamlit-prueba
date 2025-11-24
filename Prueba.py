import streamlit as st
import msal
import requests
import pandas as pd
import io

st.title("Conexión OneDrive Empresarial vía Microsoft Graph (Delegated OAuth)")

TENANT_ID = st.secrets["azure"]["tenant_id"]
CLIENT_ID = st.secrets["azure"]["client_id"]
CLIENT_SECRET = st.secrets["azure"]["client_secret"]
REDIRECT_URI = st.secrets["azure"]["redirect_uri"]

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Permisos delegados (NO requieren admin consent)
SCOPES = ["User.Read", "Files.Read"]

# Inicializar estado
if "token" not in st.session_state:
    st.session_state["token"] = None

# Crear la URL de autenticación
def get_auth_url():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    return app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)

# Intercambiar código por token
def exchange_code_for_token(code):
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    return app.acquire_token_by_authorization_code(
        code,
        SCOPES,
        redirect_uri=REDIRECT_URI
    )

# Obtener parámetros de la URL
params = st.experimental_get_query_params()

# Si viene code, intercambiar por token
if "code" in params and st.session_state["token"] is None:
    code = params["code"][0]
    token_data = exchange_code_for_token(code)
    st.session_state["token"] = token_data

# Si no hay token → mostrar botón de inicio de sesión
if st.session_state["token"] is None:
    auth_url = get_auth_url()
    st.markdown(f"[Iniciar sesión con Microsoft]({auth_url})")
else:
    st.success("Autenticado con Microsoft Graph correctamente.")
    access_token = st.session_state["token"]["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # Cambia esto por el archivo que quieras leer
    file_path = "/PruebasStreamlit/datos_prueba.xlsx"

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:{file_path}:/content"

    st.write("Obteniendo archivo desde OneDrive de empresa...")

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        df = pd.read_excel(io.BytesIO(r.content))
        st.dataframe(df)
    else:
        st.error(f"Error {r.status_code}: {r.text}")
