# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:10:42 2024

@author: Emmanuel Maruri 
"""

# Librerías
#import numpy as np 
import pandas as pd
#import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px


# Cargar y ver la base 
dire = 'Bases/'
#base = pd.read_csv(dire+"raiavl_venta_mensual_tr_cifra_2023.csv")
#base.head()
for year in range(2019, 2025, 1):
    base_i = pd.read_csv(dire + "raiavl_venta_mensual_tr_cifra_" + str(year) + ".csv")
    if year == 2019: 
        base = base_i.copy()
    else: 
        base = pd.concat([base, base_i])

# Convertir a minusculas
base = base.rename(columns=str.lower)

# Formato de fecha 
base['fecha'] = pd.to_datetime(base['anio'].astype(str) + base['id_mes'].astype(str), format='%Y%m')

# Cambiar el orden de las variables
nuevo_orden = ['fecha'] + base.columns.drop(['fecha', 'anio', 'id_mes']).tolist()
base = base[nuevo_orden]

# Juntar con la base de países
base_paises = pd.read_csv(dire+"tc_pais_origen.csv")
# Convertir a minusculas
base_paises = base_paises.rename(columns=str.lower)
# Luego hacemos un merge sobre las bases
base = pd.merge(base, base_paises, on='id_pais_origen')

# Eliminar cosas que no usan
del base_i, base_paises, nuevo_orden, year 

# Lista de marcas
lista_marcas = list(base.marca.unique())
# Ordenar 
lista_marcas.sort()
# Agregar total 
lista_marcas = ['Total'] + lista_marcas


# Página -----------------------------------------
st.title('Ventas de automóviles en México')

# Controles 
# Periodo
periodo = st.sidebar.slider('Seleccione un año:',
                               min_value = 2019, max_value = 2024, 
                               value = (2019, 2024) )
# Marca 
marca_seleccionada = st.sidebar.selectbox('Seleccione una marca: ', lista_marcas)

# Filtro de fecha
base = base.loc[(base['fecha'] >= str(periodo[0])+'-01-01') & (base['fecha'] <= str(periodo[1])+'-01-01')]



### SECCIÓN DE GRÁFICAS ------------------------------------------------
def plot_ventas_totales(marca_seleccionada): 
    ventas_totales = base.groupby(['fecha', 'marca'])['uni_veh'].sum().reset_index()
    if (marca_seleccionada == 'Total'): 
        ventas_totales = ventas_totales.groupby(['fecha'])['uni_veh'].sum().reset_index()
    else: 
        ventas_totales = ventas_totales[ventas_totales['marca'] == marca_seleccionada]
    
    # Plot linea
    fig_ventas = px.line(ventas_totales, x="fecha", y="uni_veh", 
                         title='Ventas totales por mes', 
                         labels={'fecha':'', 
                                 'uni_veh': 'Unidades vendidas'})

    return fig_ventas

# Imprimir figura en el dashboard
fig_ventas = plot_ventas_totales(marca_seleccionada)
    
# Contribuciones por segmento
def plot_contribuciones_ventas(marca_seleccionada): 
    if (marca_seleccionada == 'Total'): 
        ventas_segmento = base.groupby(['fecha', 'segmento'])['uni_veh'].sum().reset_index()
        #ventas_segmento = ventas_segmento.pivot(index=['fecha'], columns='segmento', values='uni_veh').reset_index()
    else: 
        ventas_segmento = base.groupby(['fecha', 'marca', 'segmento'])['uni_veh'].sum().reset_index()
        ventas_segmento = ventas_segmento[ventas_segmento['marca'] == marca_seleccionada]
        #ventas_segmento = ventas_segmento.pivot(index=['fecha'], columns='segmento', values='uni_veh').reset_index()
    
    ventas_segmento = ventas_segmento.fillna(0)
    # Plot
    fig_contribuciones = px.bar(ventas_segmento, 
                                x="fecha", y="uni_veh", 
                                color="segmento", 
                                title='Ventas por segmento',
                                labels={'fecha':'', 
                                        'uni_veh': 'Unidades vendidas', 
                                        'segmento': 'Segmento'})
    return fig_contribuciones

# Imprimir figura en el dashboard
fig_contribuciones = plot_contribuciones_ventas(marca_seleccionada)

# Origen de ventas    
def plot_origen_ventas(marca_seleccionada): 
    if (marca_seleccionada == 'Total'): 
        origen_ventas = base.groupby(['origen'])['uni_veh'].sum().reset_index()
    else:
        origen_ventas = base.groupby(['origen', 'marca'])['uni_veh'].sum().reset_index()
        origen_ventas = origen_ventas[origen_ventas['marca'] == marca_seleccionada]
    origen_ventas['porcentaje'] = origen_ventas['uni_veh'] / origen_ventas['uni_veh'].sum() * 100
    origen_ventas = origen_ventas[['origen', 'porcentaje']]
    # Figura 
    #fig_origen, ax = plt.subplots()
    #ax.pie(origen_ventas['porcentaje'], labels=origen_ventas['origen'], autopct='%1.1f%%')
    #ax.set_title('Origen de las unidades vendidas')
    fig_origen = px.pie(origen_ventas, values='porcentaje', names='origen', 
                        title='Origen de las unidades vendidas')
    return fig_origen

# Imprimir figura en el dashboard
fig_origen = plot_origen_ventas(marca_seleccionada)

# Tabla de autos más 
def plot_modelos_mas_vendidos(marca_seleccionada):
    if marca_seleccionada == 'Total': 
        df = base.groupby(['modelo'])['uni_veh'].sum().sort_values(ascending=False).head().reset_index()
    else: 
        df = base[base['marca'] == marca_seleccionada]
        df = df.groupby(['modelo'])['uni_veh'].sum().sort_values(ascending=False).head().reset_index()
    
    fig_modelos = px.bar(df, x = 'modelo', y = 'uni_veh', #orientation='h', 
                         title = 'Modelos más vendidos', 
                         labels = {'modelo': 'Modelo', 
                                   'uni_veh': 'Unidades vendidas'})
    return fig_modelos 

modelos_mas_vendidos = plot_modelos_mas_vendidos(marca_seleccionada)

def cuadro_autos(marca_seleccionada): 
    df = base.groupby(['marca','modelo'])['uni_veh'].sum().sort_values(ascending=False).reset_index()
    df = df[df['uni_veh'] > 0]
    
    # Plot
    fig_cuadro = px.icicle(df, names='modelo', parents='marca', values='uni_veh')   
    
    return fig_cuadro

fig_cuadro = cuadro_autos(marca_seleccionada)

# Página -----------------------------------------
# Columnas 
left_column, right_column = st.columns(2)
# Streamlit functions inside a "with" block:
with left_column:
    #st.write(fig_ventas)
    st.plotly_chart(fig_ventas, use_container_width=True)

    #st.write(fig_origen)
    st.plotly_chart(fig_origen, use_container_width=True)

    
with right_column:
    #st.write(fig_contribuciones)
    st.plotly_chart(fig_contribuciones, use_container_width=True)
    #st.write(modelos_mas_vendidos)
    st.plotly_chart(modelos_mas_vendidos, use_container_width=True)
    
#    st.plotly_chart(fig_cuadro)