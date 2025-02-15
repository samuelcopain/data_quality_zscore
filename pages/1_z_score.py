import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from random import randint
from openpyxl.workbook import Workbook
from st_aggrid import JsCode,AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import scipy.stats as stats
from plotnine import *
import datetime
from docxtpl import DocxTemplate, InlineImage

#from docxtpl import DocxTemplate
plt.style.use('ggplot')




st.header('Les valeur aberrantes par la méthode du z-score')

#@st.cache_data
def data_upload():
    #df = pd.read_csv("data\SR_zscore.csv", encoding='latin-1')
    #df = pd.read_excel("data/data_new.xls", skiprows=1, engine="xlrd")
    df = pd.read_excel("data/RMA_II_2_1_Centre_z_score.xls", skiprows=1, engine="xlrd")
    #df = pd.read_excel("data/Zscore_ExpandPF_centre.xls", skiprows=1, engine="xlrd")

    df.fillna(0, inplace = True)
    #df['Periode'] = pd.to_datetime(df['Periode'])
    return df

df = data_upload()
#df["Periode"]=pd.to_datetime(df["Periode"])
#df["Periode"] = pd.to_datetime(df["Periode"]).dt.strftime("%d-%b-%y")
st.dataframe(df.head(5))
st.write(df.shape)
st.write(df.dtypes)

with st.form(key="form1"):
    z = st.selectbox('valeur du zscore :',(3,2.5,2,1.5))
    submit = st.form_submit_button(label="Valeurs atypiques")

my_list = df._get_numeric_data().columns.values.tolist()
list_fosa = df["FOSA"].unique()


for col in my_list:
    df['zscore_'+col] = stats.zscore(df[col])
    

selected_columns = [column for column in df.columns if column.startswith('zscore_')] #sélectionner les colonne qui commencent par zscore_

fusion2 = []

######
for col in selected_columns :
    #selected_columns_new = selected_columns.remove(col)
    df_zscore = df[(df[col]  > z)|(df[col] < -z)]
    df_zscore['Variable'] = col
    df_zscore.rename(columns = { col:'zscore'}, inplace = True)
   
    #df_zscore = df_zscore.drop(selected_columns_new, axis=1)
    selections= ['Region','District','Aire','FOSA','Periode', 'Variable','zscore']
    df_zscore = df_zscore.loc[:, ~df_zscore.columns.str.startswith('zscore_')] # supprimer les colonne commençant par zscore_
    df_zscore['Variable'] = df_zscore['Variable'].str.replace('zscore_','')

    names = ['Region','District','Aire','FOSA','Periode','Variable','zscore']
    #df_zscore = df_zscore[df_zscore.columns.difference(names)].add_prefix("zscore_")

    #df_zscore.columns = ['{}{}'.format(c, '' if c in names else 'zscore_') for c in df_zscore.columns]

    df_zscore.columns=df_zscore.columns.map(lambda x : 'zscore_'+x if x !='Region' and x!='District' and x!='Aire' and x!='FOSA' and x!='Periode' and x!='zscore' and x!='Variable' else x)
    df_zscore.rename(columns = { col:'Valeur'}, inplace = True)
    df_zscore = df_zscore.loc[:, ~df_zscore.columns.str.startswith('zscore_')] # voir si on n'aurait du supprimer en haut
    names = ['Region','District','Aire','FOSA','Periode','zscore','Variable','Valeur']
    df_zscore = df_zscore[names]
    #df_zscore=df_zscore[selection]
    #df_zscore['Variable'] = col
    
    ##df_zscore=df_zscore[selections]
    #st.dataframe(df_zscore)
    #df_ola.reset_index(inplace = True)
    #df_ola=df_ola['FOSA','Periode', 'Variable'] 
    if not df_zscore.empty:
        fusion2.append(df_zscore)
        dfX = pd.concat(fusion2, axis=0, ignore_index=True)
        dfX.sort_values(by='zscore', ascending=False, inplace=True)
st.write("total valeurs atypiques : ", len(dfX))
st.dataframe(dfX)


# Ag grid

gd = GridOptionsBuilder.from_dataframe(dfX)

gd.configure_pagination(enabled=True)
gd.configure_selection(use_checkbox=True)
gridoptions= gd.build()
with st.form("quality") as f:
    grid_table=AgGrid(dfX,
                    gridOptions=gridoptions,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    allow_unsafe_jscode=True)
    sel_row= grid_table["selected_rows"]
    df_row = pd.DataFrame(sel_row)
    st.form_submit_button("Analyser")

if df_row.size != 0:
    nom_fosa=st.write(df_row.iat[0,3])
    st.write(sel_row)

    selections2= ['Region','District','Aire','FOSA','Periode',df_row.iat[0,6]]

    if not dfX.empty:
        #st.table(df2)
    # title = st.text_input('Vérifier la plage de données', '')
        #st.write('Plage de données :', df_row.iat[0,3])
        df4 = df[(df["FOSA"] == df_row.iat[0,3])][selections2]
        df4.rename(columns = { df_row.iat[0,6]:'Variable'}, inplace = True)
        st.dataframe(df4)

        if not df4.empty:
            #fig2, ax = plt.subplots()
            #ax.bar(df4['Periode'], df4['Variable'])
            #st.pyplot(fig2)
            level_order = ['Janvier 2024', 'Février 2024', 'Mars 2024','Avril 2024', 'Mai 2024', 'Juin 2024','Juillet 2024', 'Août 2024', 'Septembre 2024','Octobre 2024', 'Novembre 2024', 'Décembre 2024']
            p = ggplot(df4, aes(x='Periode', y='Variable'  )) + scale_x_discrete(limits = level_order)+geom_bar(stat="identity",fill="steelblue",width=0.6)+ theme(axis_text_x  = element_text(angle = 40, hjust = 1)) + geom_text(aes(label = 'Variable'))
            # When using ggplot for python, replace "axis.text.x" with "axis_text_x"
            st.pyplot(ggplot.draw(p))

# Partie rapport DOCX
st.write('Reportings')

bouton_regle = st.button("Rapport données atypiques")
if bouton_regle:
    doc = DocxTemplate("templateRapport/zscoreTplate.docx")


    

    z_score = []
    for ind in dfX.index:
        z_score.append({"Region":dfX['Region'][ind], "District":dfX['District'][ind], "Aire":dfX['Aire'][ind],"FOSA":dfX['FOSA'][ind],"Periode":dfX['Periode'][ind],"zscore":dfX['zscore'][ind],"Variable":dfX['Variable'][ind],"Valeur":dfX['Valeur'][ind]})
            
        


    context = {

    "z_score":z_score
        }

    doc.render(context)
    doc.save("rapport/rapport_zscore.docx")

# télécharger le fichier
dfX_csv=dfX.to_csv()
st.download_button("Télécharger",
data=dfX_csv,
file_name="z_score.csv",
mime="text/csv"

)


