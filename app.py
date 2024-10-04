# app.py
import streamlit as st
import pandas as pd

# Definir funciones de cálculo

def calcular_valor_futuro_ahorro_con_interes_y_impuestos(aportacion_mensual, tasa_mensual, meses, saldo_anterior, max_saldo_con_interes, descontar_impuestos_de_ahorro):
    saldo = saldo_anterior
    impuestos_totales = 0
    intereses_acumulados_anual = 0
    for i in range(1, meses + 1):
        # Calcular el interés mensual basado en el saldo actual, pero solo aplica hasta max_saldo_con_interes
        saldo_a_interesar = min(saldo, max_saldo_con_interes)
        interes = saldo_a_interesar * tasa_mensual
        saldo += interes  # Sumar el interés mensual al saldo
        intereses_acumulados_anual += interes  # Sumar el interés del mes al total anual
        saldo += aportacion_mensual  # Añadir la aportación mensual

    # Al final del periodo, calcular impuestos sobre el interés acumulado
    if intereses_acumulados_anual > 0:
        impuestos_anuales = calcular_impuestos(intereses_acumulados_anual)
        if descontar_impuestos_de_ahorro:
            saldo -= impuestos_anuales  # Restar los impuestos al saldo si se elige descontar de la cuenta de ahorro
        impuestos_totales += impuestos_anuales  # Sumar al total de impuestos
    else:
        impuestos_anuales = 0
    
    return saldo, impuestos_totales, saldo_anterior, impuestos_anuales


def calcular_valor_futuro_con_aportaciones_diversificadas(aportacion_mensual, porcentaje, rendimiento_mensual, meses, saldo_inicial):
    saldo = saldo_inicial
    for _ in range(meses):
        saldo += saldo * rendimiento_mensual
        saldo += aportacion_mensual * porcentaje
    return saldo


def calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_sin_intereses):
    return valor_total_fondos - dinero_invertido_sin_intereses


def calcular_impuestos(beneficio_neto):
    if beneficio_neto <= 6000:
        impuesto = beneficio_neto * 0.19
    elif beneficio_neto <= 50000:
        impuesto = (6000 * 0.19) + ((beneficio_neto - 6000) * 0.21)
    elif beneficio_neto <= 200000:
        impuesto = (6000 * 0.19) + ((50000 - 6000) * 0.21) + ((beneficio_neto - 50000) * 0.23)
    else:
        impuesto = (6000 * 0.19) + ((50000 - 6000) * 0.21) + ((200000 - 50000) * 0.23) + ((beneficio_neto - 200000) * 0.27)
    return round(impuesto, 2)

def crear_entrada_fondo(index, fondos_info):
    st.subheader(f'Fondo {index + 1}')
    nombre_fondo = st.text_input(f'Nombre del Fondo {index + 1}:', value=f'Fondo {index + 1}', key=f'nombre_fondo_{index}')
    rendimiento_anual = st.number_input(f'Rendimiento anual del Fondo {index + 1} (%):', min_value=0.0, value=6.0 if index == 0 else 10.0, step=0.1, key=f'rendimiento_anual_{index}') / 100
    porcentaje_fondo = st.slider(f'Porcentaje destinado al Fondo {index + 1}:', min_value=0.0, max_value=1.0, value=fondos_info[index]['porcentaje'] if fondos_info else (0.7 if index == 0 else 0.3), step=0.05, key=f'porcentaje_fondo_{index}')
    saldo_inicial_fondo = st.number_input(f'Saldo inicial del Fondo {index + 1} (€):', min_value=0.0, value=0.0, step=100.0, key=f'saldo_inicial_{index}')

    # Actualizar el porcentaje en fondos_info y reajustar los demás fondos
    fondos_info[index]['porcentaje'] = porcentaje_fondo
    reajustar_porcentajes(index, fondos_info)

    return {'nombre': nombre_fondo, 'rendimiento_anual': rendimiento_anual, 'porcentaje': fondos_info[index]['porcentaje'], 'saldo_inicial': saldo_inicial_fondo}

def reajustar_porcentajes(changed_index, fondos_info):
    porcentaje_actual = fondos_info[changed_index]['porcentaje']
    porcentaje_restante = 1.0 - porcentaje_actual
    num_otros_fondos = len(fondos_info) - 1

    if num_otros_fondos > 0:
        ajuste_proporcional = porcentaje_restante / num_otros_fondos
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = ajuste_proporcional

def reajustar_porcentajes(changed_index, fondos_info):
    porcentaje_actual = fondos_info[changed_index]['porcentaje']
    porcentaje_restante = 1.0 - porcentaje_actual
    num_otros_fondos = len(fondos_info) - 1

    if num_otros_fondos > 0:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = porcentaje_restante / num_otros_fondos

def reajustar_porcentajes(changed_index, fondos_info):
    total_porcentaje_restante = 1.0 - fondos_info[changed_index]['porcentaje']
    num_otros_fondos = len(fondos_info) - 1

    if num_otros_fondos > 0:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = total_porcentaje_restante / num_otros_fondos

def reajustar_porcentajes(changed_index, fondos_info):
    total_porcentaje = sum(fondo['porcentaje'] for i, fondo in enumerate(fondos_info) if i != changed_index)
    porcentaje_restante = 1.0 - fondos_info[changed_index]['porcentaje']
    
    if total_porcentaje > 0:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = (fondo['porcentaje'] / total_porcentaje) * porcentaje_restante
    else:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = porcentaje_restante / (len(fondos_info) - 1)

def reajustar_porcentajes(changed_index, fondos_info):
    total_porcentaje = sum(fondo['porcentaje'] for i, fondo in enumerate(fondos_info) if i != changed_index)
    porcentaje_restante = 1.0 - fondos_info[changed_index]['porcentaje']
    
    if total_porcentaje > 0:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = (fondo['porcentaje'] / total_porcentaje) * porcentaje_restante
    else:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = porcentaje_restante / (len(fondos_info) - 1)

def reajustar_porcentajes(changed_index, fondos_info):
    total_porcentaje = sum(fondo['porcentaje'] for i, fondo in enumerate(fondos_info) if i != changed_index)
    porcentaje_restante = 1.0 - fondos_info[changed_index]['porcentaje']
    
    if total_porcentaje > 0:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = (fondo['porcentaje'] / total_porcentaje) * porcentaje_restante
    else:
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = porcentaje_restante / (len(fondos_info) - 1)

# Aplicación Streamlit
st.title('Visualizador de Proyección Financiera')

# Entradas del usuario
st.sidebar.header('Configuración de la Proyección')
transferencia_mensual = st.sidebar.number_input('Cantidad mensual de la transferencia (€):', min_value=0, value=690, step=10)
saldo_inicial_ahorro = st.sidebar.number_input('Saldo inicial de la cuenta de ahorro (€):', min_value=0.0, value=0.0, step=100.0)

fondos = st.sidebar.slider('Número de fondos a configurar:', min_value=0, max_value=5, value=2)
if fondos == 0:
    porcentaje_inversion = 0.0
else:
    porcentaje_inversion = st.sidebar.slider('Porcentaje destinado a inversión:', min_value=0.0, max_value=1.0, value=0.7, step=0.05)
porcentaje_ahorro = 1 - porcentaje_inversion

tasa_ahorro_anual = st.sidebar.number_input('Interés anual de la cuenta de ahorro (%):', min_value=0.0, value=2.25, step=0.1) / 100
max_saldo_con_interes = st.sidebar.number_input('Máximo saldo con interés aplicado (€):', min_value=0, value=70000, step=1000)
descontar_impuestos_de_ahorro = st.sidebar.checkbox('Descontar impuestos de la cuenta de ahorro', value=True)

fondos_info = [{'porcentaje': 1.0 / fondos} for i in range(fondos)] if fondos > 0 else []
fondos_info = [{'porcentaje': 0.7 if i == 0 else 0.3} for i in range(fondos)] if fondos > 0 else []
fondos_info = [{'porcentaje': 1.0 / fondos} for i in range(fondos)] if fondos > 0 else []
fondos_info = [{'porcentaje': 1.0 / fondos} for i in range(fondos)] if fondos > 0 else []
fondos_info = [crear_entrada_fondo(i, fondos_info) for i in range(fondos)] if fondos > 0 else []



años_proyeccion = st.sidebar.number_input('Años de proyección:', min_value=1, value=30, step=1)

# Cálculos
aportacion_inversion = transferencia_mensual * porcentaje_inversion
aportacion_ahorro = transferencia_mensual * porcentaje_ahorro
tasa_ahorro_mensual = tasa_ahorro_anual / 12

meses_list = [year * 12 for year in range(1, años_proyeccion + 1)]

proyeccion_completa = []
saldo_anterior = saldo_inicial_ahorro  # Saldo inicial en ahorro
aportacion_total_anual = aportacion_ahorro * 12  # Aportación anual al ahorro

for year, meses in enumerate(meses_list, start=1):
    # Calcular los valores de ahorro
    saldo_actual_ahorro, impuestos_ahorro, saldo_anterior, impuestos_anuales_ahorro = calcular_valor_futuro_ahorro_con_interes_y_impuestos(
        aportacion_ahorro, tasa_ahorro_mensual, meses, saldo_anterior, max_saldo_con_interes, descontar_impuestos_de_ahorro)
    
    # Calcular los valores de la inversión en fondos
    if fondos > 0:
        valor_total_fondos = sum(
            calcular_valor_futuro_con_aportaciones_diversificadas(
                aportacion_inversion, fondo['porcentaje'], fondo['rendimiento_anual'] / 12, meses, fondo['saldo_inicial'])
            for fondo in fondos_info
        )
        dinero_invertido_fondos = aportacion_inversion * meses
        beneficio_fondos = calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_fondos)
        impuestos_liquidacion_fondos = calcular_impuestos(beneficio_fondos)
    else:
        valor_total_fondos = 0
        beneficio_fondos = 0
        impuestos_liquidacion_fondos = 0

    # Sumar dinero total invertido (ahorro + fondos)
    dinero_total_invertido = (aportacion_ahorro + aportacion_inversion) * meses

    # Guardar los resultados en la tabla
    entry = {
        "Año": year,
        "Valor Total del Ahorro con Interés (euros)": round(saldo_actual_ahorro, 2),
        "Impuestos Ahorro (euros)": round(impuestos_anuales_ahorro, 2),
        "Dinero Total Invertido (euros)": round(dinero_total_invertido, 2)
    }
    if fondos > 0:
        entry.update({
            "Valor Total Invertido en Fondos (euros)": round(valor_total_fondos, 2),
            "Beneficio de Fondos (euros)": round(beneficio_fondos, 2),
            "Impuestos de Liquidación Fondos (euros)": round(impuestos_liquidacion_fondos, 2)
        })
    proyeccion_completa.append(entry)

# Mostrar resultados
@st.cache_data
def obtener_proyeccion_dataframe(proyeccion_completa):
    return pd.DataFrame(proyeccion_completa)

if st.button('Calcular Proyección'):
    df_proyeccion_completa = obtener_proyeccion_dataframe(proyeccion_completa)
    st.write("## Resultados de la Proyección Financiera")
    st.dataframe(df_proyeccion_completa)

    # Descripción de cada valor de la tabla
    st.write("### Descripción de los valores de la tabla")
    st.write("- **Año**: Representa el año de la proyección en curso.")
    st.write("- **Valor Total del Ahorro con Interés (euros)**: Muestra el saldo total acumulado en la cuenta de ahorro, incluyendo los intereses generados hasta ese año.")
    st.write("- **Impuestos Ahorro (euros)**: Indica la cantidad de impuestos pagados sobre los intereses generados en la cuenta de ahorro durante el año.")
    st.write("- **Dinero Total Invertido (euros)**: Es la suma total del dinero destinado tanto al ahorro como a la inversión, acumulado hasta el año en cuestión.")
    if fondos > 0:
        st.write("- **Valor Total Invertido en Fondos (euros)**: Muestra el valor total de los fondos invertidos, considerando el rendimiento de los fondos hasta ese año.")
        st.write("- **Beneficio de Fondos (euros)**: Representa el beneficio neto obtenido de las inversiones en fondos, después de descontar la cantidad invertida.")
        st.write("- **Impuestos de Liquidación Fondos (euros)**: Indica la cantidad de impuestos a pagar en caso de que se liquiden los fondos en ese año.")

    # Texto antes de los gráficos
    st.write("### Gráficas de la Proyección Financiera")

    # Mostrar gráficos usando Streamlit line_chart
    if fondos > 0:
        df_proyeccion_completa['Total Ahorro + Fondos (euros)'] = df_proyeccion_completa['Valor Total del Ahorro con Interés (euros)'] + df_proyeccion_completa['Valor Total Invertido en Fondos (euros)']
        st.line_chart(df_proyeccion_completa.set_index('Año')[['Dinero Total Invertido (euros)', 'Valor Total del Ahorro con Interés (euros)', 'Valor Total Invertido en Fondos (euros)', 'Total Ahorro + Fondos (euros)']])
    else:
        st.line_chart(df_proyeccion_completa.set_index('Año')[['Valor Total del Ahorro con Interés (euros)']])
