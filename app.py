import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime






multi = '''Suivi de la qualité des données du Dhis2. 
Deux dimensions sont utilisées, la recherche des valeurs atypiques par le Z-score et les règles de validation des programmes.
'''

st.header('La qualité des données avec Python')
st.markdown(multi)

def lien(page):
    return st.page_link(f"pages/{page}.py", label='Valider')


cible = st.selectbox(
    label="Règle de validation SRMNI",
    options=["Consultation prenatale", "Consultation postnatale"], index=None)

if cible=='Consultation postnatale':
    lien('3_Consultation_postnatale')


if cible=='Consultation prenatale':
    lien('2_Consultation_prenatale')







df = pd.read_excel("data/New_xls.xls", skiprows=1, engine="xlrd")

st.dataframe(df.head(5))

st.write(df.dtypes)


from datetime import datetime

# Excel string 'Mai 2024'
excel_string = 'Mai 2024'

# Convert 'Mai' to 'May' and parse the date
date = datetime.strptime(f"May {excel_string[4:]}", "%B %Y").date()

st.write(date) #2024-05-01 00:00:00