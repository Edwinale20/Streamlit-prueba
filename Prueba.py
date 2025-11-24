import streamlit as st
import pandas as pd

st.title("Dashboard conectado a OneDrive 🔥")

st.write("Leyendo archivo desde OneDrive empresarial...")

df = pd.read_excel(url)

st.dataframe(df)

