import streamlit as st
import pandas as pd

st.title("Dashboard conectado a OneDrive 🔥")

url = "https://7eleven-my.sharepoint.com/:f:/g/personal/edwing_cardenas_7-eleven_com_mx/ElsK3j-g6u5Gly9lUEeKMEMBELmofLCv22h-GNeKCaq0LA?e=kPoOQ7"

st.write("Leyendo archivo desde OneDrive empresarial...")

df = pd.read_excel(url)

st.dataframe(df)

