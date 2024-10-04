# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Definir funciones de cálculo

def calcular_valor_futuro_ahorro_con_interes_y_impuestos(aportacion_mensual, tasa_mensual, meses):
    saldo = 0
    impuestos_totales = 0
    for i in range(1, meses + 1):
        interes = saldo * tasa_mensual
        saldo += interes
        saldo += aportacion_mensual
        if i % 12 == 0:
            impuestos_totales += aplicar_impuesto_anual(interes)
            saldo -= impuestos_totales
    return saldo, impuestos_totales

def aplicar_impuesto_anual(interes_anual):
    return interes_anual * 0.19  # Aplicar 19% a las ganancias cada año


def calcular_valor_futuro_con_aportaciones_diversificadas(aportacion_mensual, porcentaje, rendimiento_mensual, meses):
    saldo = 0
    for _ in range(meses):
        saldo += saldo * rendimiento_mensual
        saldo += aportacion_mensual * porcentaje
    return saldo


def calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_sin_intereses):
    return valor_total_fondos - dinero_invertido_sin_intereses


def calcular_impuestos_liquidacion(beneficio_neto):
    if beneficio_neto <= 6000:
        impuesto = beneficio_neto * 0.19
    elif beneficio_neto <= 50000:
        impuesto = (6000 * 0.19) + ((beneficio_neto - 6000) * 0.21)
    elif beneficio_neto <= 200000:
        impuesto = (6000 * 0.19) + ((50000 - 6000) * 0.21) + ((beneficio_neto - 50000) * 0.23)
    else:
        impuesto = (6000 * 0.19) + ((50000 - 6000) * 0.21) + ((beneficio_neto - 50000) * 0.23) + ((beneficio_neto - 200000) * 0.27)
    return round(impuesto, 2)

def crear_entrada_fondo(index):
    st.subheader(f'Fondo {index + 1}')
    nombre_fondo = st.text_input(f'Nombre del Fondo {index + 1}:', value=f'Fondo {index + 1}')
    rendimiento_anual = st.number_input(f'Rendimiento anual del Fondo {index + 1} (%):', min_value=0.0, value=6.0 if index == 0 else 10.0, step=0.1) / 100
    porcentaje_fondo = st.slider(f'Porcentaje destinado al Fondo {index + 1}:', min_value=0.0, max_value=1.0, value=0.7 if index == 0 else 0.3, step=0.05)
    return {'nombre': nombre_fondo, 'rendimiento_anual': rendimiento_anual, 'porcentaje': porcentaje_fondo}

# Aplicación Streamlit
st.title('Visualizador de Proyección Financiera')

# Entradas del usuario
st.sidebar.header('Configuración de la Proyección')
transferencia_mensual = st.sidebar.number_input('Cantidad mensual de la transferencia (€):', min_value=0, value=690, step=10)
porcentaje_inversion = st.sidebar.slider('Porcentaje destinado a inversión:', min_value=0.0, max_value=1.0, value=0.7, step=0.05)
porcentaje_ahorro = 1 - porcentaje_inversion

tasa_ahorro_anual = st.sidebar.number_input('Interés anual de la cuenta de ahorro (%):', min_value=0.0, value=2.25, step=0.1) / 100
fondos = st.sidebar.slider('Número de fondos a configurar:', min_value=1, max_value=5, value=2)

fondos_info = [crear_entrada_fondo(i) for i in range(fondos)]

años_proyeccion = st.sidebar.number_input('Años de proyección:', min_value=1, value=30, step=1)

# Cálculos
aportacion_inversion = transferencia_mensual * porcentaje_inversion
aportacion_ahorro = transferencia_mensual * porcentaje_ahorro
tasa_ahorro_mensual = tasa_ahorro_anual / 12

meses_list = [year * 12 for year in range(1, años_proyeccion + 1)]

proyeccion_completa = []
saldo_anterior = 0  # Saldo inicial en ahorro
aportacion_total_anual = aportacion_ahorro * 12  # Aportación anual al ahorro

for year, meses in enumerate(meses_list, start=1):
    # Calcular los valores de ahorro
    saldo_actual_ahorro, impuestos_ahorro = calcular_valor_futuro_ahorro_con_interes_y_impuestos(
        aportacion_ahorro, tasa_ahorro_mensual, meses)
    
    # Calcular los valores de la inversión en fondos
    valor_total_fondos = sum(
        calcular_valor_futuro_con_aportaciones_diversificadas(
            aportacion_inversion, fondo['porcentaje'], fondo['rendimiento_anual'] / 12, meses)
        for fondo in fondos_info
    )

    dinero_invertido_fondos = aportacion_inversion * meses
    beneficio_fondos = calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_fondos)
    impuestos_liquidacion_fondos = calcular_impuestos_liquidacion(beneficio_fondos)

    # Sumar dinero total invertido (ahorro + fondos)
    dinero_total_invertido = (aportacion_ahorro + aportacion_inversion) * meses

    # Guardar los resultados en la tabla
    proyeccion_completa.append({
        "Año": year,
        "Valor Total del Ahorro con Interés (euros)": round(saldo_actual_ahorro, 2),
        "Valor Total Invertido en Fondos (euros)": round(valor_total_fondos, 2),
        "Beneficio de Fondos (euros)": round(beneficio_fondos, 2),
        "Impuestos de Liquidación Fondos (euros)": round(impuestos_liquidacion_fondos, 2),
        "Dinero Total Invertido (euros)": round(dinero_total_invertido, 2)
    })

    # Actualizar el saldo anterior para el próximo cálculo
    saldo_anterior = saldo_actual_ahorro

# Mostrar resultados
@st.cache_data
def obtener_proyeccion_dataframe(proyeccion_completa):
    return pd.DataFrame(proyeccion_completa)

if st.button('Calcular Proyección'):
    df_proyeccion_completa = obtener_proyeccion_dataframe(proyeccion_completa)
    st.write("## Resultados de la Proyección Financiera")
    st.dataframe(df_proyeccion_completa)

    # Mostrar gráficos
    st.write("### Evolución del Valor del Ahorro y de los Fondos")
    st.line_chart(df_proyeccion_completa.set_index('Año')[['Valor Total del Ahorro con Interés (euros)', 'Valor Total Invertido en Fondos (euros)']])

    st.write("### Evolución del Beneficio de Fondos")
    st.line_chart(df_proyeccion_completa.set_index('Año')['Beneficio de Fondos (euros)'])