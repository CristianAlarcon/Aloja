import streamlit as st
import joblib
import pandas as pd
import datetime
import plotly.express as px
import numpy as np

data = pd.read_csv('dades_prediccio_bernat.csv', delimiter=',', quotechar='"', low_memory=False)

###############################################################################


st.set_page_config(layout="wide")
st.write("""

# ANÁLISI EXPLORATORI

""")

#####################  PREPARACIÓ FILTRES  ####################################


st.sidebar.header('FILTRES')
data['createdAt'] = pd.to_datetime(data['createdAt'], format='%Y-%m-%d %H:%M:%S')
booking_date = datetime.datetime(2021, 1, 1)
first_date = datetime.datetime(2021, 1, 1)
last_date = datetime.datetime(2021, 12, 31)
data_reserva = st.sidebar.date_input("DATA DE RESERVA", booking_date)
data_inici = st.sidebar.date_input("DATA D'INICI", first_date)
data_fi = st.sidebar.date_input("DATA DE FI", last_date)



data['createdAt'] = pd.to_datetime(data['createdAt'], format='%Y-%m-%d %H:%M:%S')
data['from'] = pd.to_datetime(data['from'], format='%Y-%m-%d %H:%M:%S')
data['to'] = pd.to_datetime(data['to'], format='%Y-%m-%d %H:%M:%S')

data_reserva = pd.to_datetime(data_reserva)
data_inici = pd.to_datetime(data_inici)
data_fi = pd.to_datetime(data_fi)
data = data[data['createdAt'] >= data_reserva]
data = data[((data['from'] >= data_inici) & (data['to'] <= data_fi))]


###############################################################################


fig_title = "### TOTAL DE RESERVES CONFIRMADES I CANCEL·LADES"
temp = data.groupby(['status', 'substatus']).size().reset_index(name='total')
temp = temp.sort_values('status')
temp.columns = ['status', 'substatus', 'total']
temp['total'] = temp['total'].astype(int)
styler = temp.style.hide_index()
st.write(fig_title)
st.write(styler.to_html(), unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')


###############################################################################


fig_title = "### RESERVES PER NOMBRE D'HABITACIONS RESERVADES"
temp = data['rooms'].value_counts().reset_index()
temp.columns = ['nombre habitacions', 'total']
##temp['total'] = temp['total'].astype(int)
st.write(fig_title)
styler = temp.style.hide_index()
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')

###############################################################################


fig_title = "PERCENTATGE DE RESERVES PER ESTAT"
temp = data.groupby(['status']).size().reset_index(name='total')
temp = temp.sort_values('status')
fig = px.pie(temp, names='status', values='total')
fig.update_traces(textposition='inside', textinfo='percent+label',
                      textfont_size=20, marker=dict(line=dict(color='#000000',
                                                              width=2)))
fig.update_layout(title=dict(text=fig_title, font=dict(family='Arial', size=30,
                             color='#000000')),
                  yaxis_zeroline=False, xaxis_zeroline=False)
fig.update_layout(
    autosize=False,
    width=1350,
    height=700)

st.write(fig)


###############################################################################


fig_title = "RESERVES AMB O SENSE FILLS"
# Crear un filtre per a les files amb algun fill
filtre_fills = (data['num_childs'] > 0) | (data['num_children'] > 0)

# Aplicar el filtre i comptar les files amb algun fill
files_amb_fills = data[filtre_fills]
compte_amb_fills = len(files_amb_fills)

# Comptar les files sense fills (negant el filtre)
files_sense_fills = data[~filtre_fills]
compte_sense_fills = len(files_sense_fills)

# Crear un DataFrame amb els comptes
df_comptes = pd.DataFrame({'Categoria': ['Amb fills', 'Sense fills'],
                           'Compte': [compte_amb_fills, compte_sense_fills]})

# Crear un gràfic de sectors amb Plotly Express
fig = px.pie(df_comptes, names='Categoria', values='Compte')
fig.update_traces(textposition='inside', textinfo='percent+label',
                               textfont_size=20,
                               marker=dict(line=dict(color='#000000',
                                                     width=2)))
fig.update_layout(title=dict(text=fig_title, font=dict(family='Arial', size=30,
                                                       color='#000000')),
                  yaxis_zeroline=False, xaxis_zeroline=False)
fig.update_layout(
    autosize=False,
    width=1350,
    height=700)

st.write(fig)


###############################################################################

fig_title = "### RESERVES PER MES"
data['Month'] = data['from'].dt.month

# Calcular el recuento de reservas por mes
room_counts = data.groupby('Month').size().reset_index()
room_counts.columns = ['Mes', 'Recuento']

# Mapear los nombres de los meses
noms_mesos_cat = [
    'gener', 'febrer', 'març', 'abril', 'maig', 'juny',
    'juliol', 'agost', 'setembre', 'octubre', 'novembre', 'desembre'
]
room_counts['Mes'] = room_counts['Mes'].map(lambda x: noms_mesos_cat[x - 1])
styler = room_counts.style.hide_index()
st.write(fig_title)
st.write(styler.to_html(), unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')


###############################################################################


fig_title = "### RESERVES PER CORREU"
temp = data.copy()


def agrupa_correus(email):
    if pd.isna(email) or ('@' not in email):
        return 'sense email'
    elif email.endswith('@guest.booking.com'):
        return 'guest booking'
    else:
        return email

temp= temp['customer.email'].apply(agrupa_correus)
temp = pd.DataFrame({'customer.email': temp})
result = temp['customer.email'].value_counts().reset_index()
result.columns = ['email', 'total']
result = result.sort_values('total', ascending= False)
styler = result.style.hide_index()
st.write(fig_title)
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')


###############################################################################


fig_title = "### RESERVES PER TIPUS DE PENSIÓ"
confirmats = data[data['status'] == 'co']
temp = confirmats.agg({'count_PC': 'sum',
                            'count_MP': 'sum',
                            'count_HA': 'sum',
                            'count_HD': 'sum',
                            'count_PCB': 'sum'}).reset_index()

# Suma total de cada fila
temp['index'] = ['pensio completa',
                 'mitja pensio',
                 'Nomes habitacio',
                 'Habitacio i esmorzar',
                 'PCB']

# Renomena les columnes per clarificar-les
temp.columns = ['index','total']
styler = temp.style.hide_index()
st.write(fig_title)
st.write(styler.to_html(), unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')

###############################################################################


fig_title = "### RESERVES PER DIES D'ANTELACIÓ"
temp = confirmats['dies_antelacio_reserva'].value_counts().reset_index()
temp.columns = ['dies antelacio', 'total']
temp['dies antelacio'] = temp['dies antelacio'] + 1
temp = temp[0:50].sort_values('dies antelacio', ascending= True)
styler = temp.style.hide_index()
st.write(fig_title)
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write("")
st.write("")
st.write("")

###############################################################################


fig_title = "### PERCENTATGES DE NULS PRESENTS A COLUMNES DE DETAILS"
print(data.columns)
columnes = ['customer.email', 'Birthday', 'customer.lastname', 'customer.city',
            'customer.province', 'customer.telephone', 'customer.zip',
            'country']


temp = (data[columnes].isnull().mean() * 100).reset_index()
temp.columns = ['Columna', 'Percentatge de Valors Nuls']
temp['Percentatge de Valors Nuls'] = temp['Percentatge de Valors Nuls'].round(2)
temp['Percentatge de Valors Nuls'] = temp['Percentatge de Valors Nuls'].apply(lambda x: '{:.2f}'.format(x))
styler = temp.style.hide_index()
st.write(fig_title)
st.write(styler.to_html(), unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')


###############################################################################


fig_title = "### RESERVES PER GÈNERE"
temp = data['customer.gender'].value_counts().reset_index()
temp.columns = ['gènere', 'total']
temp = temp.sort_values('gènere')
temp['gènere'] = temp['gènere'].replace({'M': 'Home', 'F': 'Dona'})
styler = temp.style.hide_index()
st.write(fig_title)
st.write(styler.to_html(), unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')

###############################################################################


fig_title = "### RESERVES PER EDAT"
temp = data['Age'].value_counts().reset_index()
temp.columns = ['edat', 'total']
temp = temp.sort_values('edat')
temp['edat'] = temp['edat'].apply(lambda x: '{:.0f}'.format(x))
styler = temp.style.hide_index()
st.write(fig_title)
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')


###############################################################################


fig_title = "### CORREUS DE LES RESERVES CANCEL·LADES"
cancelades = data[data['status']=='ca']

temp = cancelades['customer.email'].apply(agrupa_correus)
temp = pd.DataFrame({'customer.email': temp})
result = temp['customer.email'].value_counts().reset_index()
result.columns = ['email', 'total']
result = result.sort_values('total', ascending=False)
styler = result.style.hide_index()
st.write(fig_title)
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')

###############################################################################


fig_title = "### PAÍS DE LES RESERVES"
temp = data['country'].value_counts().reset_index()
temp.columns = ['país', 'total']
temp = temp.sort_values('total', ascending= False)
styler = temp.style.hide_index()
st.write(fig_title)
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')

###############################################################################


fig_title = "### CIUTAT DE LES RESERVES"
temp = data[data['customer.city'] != '.']['customer.city'].value_counts().reset_index()
temp.columns = ['ciutat', 'total']
temp = temp.sort_values('total', ascending = False)
styler = temp.style.hide_index()
st.write(fig_title)
html_table = styler.to_html(escape=False, index=False)
scrollable_html = f'<div style="overflow-x:auto; height: 300px;">{html_table}</div>'
st.write(scrollable_html, unsafe_allow_html=True, use_container_width=True)
st.write('')
st.write('')
st.write('')


###############################################################################


fig_title = "### RECOMPTE DE NULS"
columnes = ['customer.name', 'customer.lastname', 'customer.zip',
            'customer.city', 'customer.email', 'country', 'customer.language',
            'customer.province', 'Birthday', 'customer.gender']
nuls = data[columnes].isnull().sum()
no_nuls = data[columnes].notnull().sum()
df_nuls = pd.DataFrame({'Columna': nuls.index, 'Valors nuls': nuls.values})
df_no_nuls = pd.DataFrame({'Columna': no_nuls.index, 'Valors no nuls': no_nuls.values})
temp = pd.merge(df_nuls, df_no_nuls, on='Columna')
styler = temp.style.hide_index()
st.write(fig_title)
st.write(styler.to_html(), unsafe_allow_html=True, use_container_width=True)

