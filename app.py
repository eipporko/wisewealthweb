# WiseWealthWeb - app.py

import streamlit as st
import pandas as pd
import math as Math

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



def calcular_impuestos(beneficio_neto, tramos=None):
    if tramos is None:
        # Tramos y tipos impositivos por defecto (España)
        tramos = [
            (6000, 0.19),
            (50000, 0.21),
            (200000, 0.23),
            (float('inf'), 0.27)
        ]
    impuesto = 0
    beneficio_restante = beneficio_neto

    for limite, tipo in tramos:
        if beneficio_restante <= 0:
            break
        if beneficio_restante > limite:
            impuesto += limite * tipo
            beneficio_restante -= limite
        else:
            impuesto += beneficio_restante * tipo
            beneficio_restante = 0

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
    porcentaje_total = sum(f['porcentaje'] for f in fondos_info)
    if porcentaje_total > 1.0:
        exceso = porcentaje_total - 1.0
        num_otros_fondos = len(fondos_info) - 1

        if num_otros_fondos > 0:
            ajuste_proporcional = exceso / num_otros_fondos
            for i, fondo in enumerate(fondos_info):
                if i != changed_index:
                    fondos_info[i]['porcentaje'] = max(0.0, fondos_info[i]['porcentaje'] - ajuste_proporcional)
    elif porcentaje_total < 1.0:
        deficit = 1.0 - porcentaje_total
        num_otros_fondos = len(fondos_info) - 1

        if num_otros_fondos > 0:
            ajuste_proporcional = deficit / num_otros_fondos
            for i, fondo in enumerate(fondos_info):
                if i != changed_index:
                    fondos_info[i]['porcentaje'] = min(1.0, fondos_info[i]['porcentaje'] + ajuste_proporcional)

    # Asegurarse de que los porcentajes sumen exactamente 1
    porcentaje_total = sum(f['porcentaje'] for f in fondos_info)
    if porcentaje_total != 1.0:
        diferencia = 1.0 - porcentaje_total
        ajuste_unitario = diferencia / (len(fondos_info) - 1)
        for i, fondo in enumerate(fondos_info):
            if i != changed_index:
                fondos_info[i]['porcentaje'] = min(1.0, max(0.0, fondos_info[i]['porcentaje'] + ajuste_unitario))

        # Ajustar el último fondo si aún hay diferencia debido a redondeo
        porcentaje_total = sum(f['porcentaje'] for f in fondos_info)
        if porcentaje_total != 1.0:
            diferencia_final = 1.0 - porcentaje_total
            for i, fondo in enumerate(fondos_info):
                if i != changed_index:
                    fondos_info[i]['porcentaje'] += diferencia_final
                    break




# Aplicación Streamlit
st.set_page_config(page_title='WiseWealthWeb', page_icon='💰')

# Mostrar la descripción inicial y el aviso importante
st.markdown(
    """
    # WiseWealthWeb

    **WiseWealthWeb** es una herramienta interactiva diseñada para ayudar a los usuarios a proyectar su situación financiera futura.
    Permite realizar simulaciones de ahorro e inversión en fondos indexados, considerando diferentes variables como el saldo inicial, las aportaciones mensuales, y los rendimientos esperados de los fondos.

    ## Instrucciones de uso:
    1. Introduce los parámetros iniciales en el menú lateral, como la cantidad mensual de transferencia, el saldo inicial del ahorro, y la cantidad de fondos a configurar.
    2. Ajusta los porcentajes de inversión y ahorro, así como el rendimiento anual esperado de los fondos.
    3. Haz clic en el botón **'Calcular Proyección'** para generar los resultados.
    4. Revisa los resultados proyectados en la tabla y gráficos, donde se muestra el crecimiento de las inversiones y el ahorro a lo largo de los años.
    5. Si seleccionaste la opción de restar los impuestos de la cuenta de ahorro, estos se aplicarán automáticamente a lo largo de los años.

    ## Aviso importante

    > ⚠️ **Inversiones conllevan riesgos. Los datos proporcionados por WiseWealthWeb son puramente orientativos y no deben considerarse como asesoramiento financiero. Se recomienda consultar a un gestor financiero profesional antes de tomar decisiones de inversión.**
    """
)

# Entradas del usuario
st.sidebar.header('Configuración de la Proyección')
transferencia_mensual = st.sidebar.number_input('Cantidad mensual de la transferencia (€):', min_value=0, value=690, step=10)
saldo_inicial_ahorro = st.sidebar.number_input('Saldo inicial de la cuenta de ahorro (€):', min_value=0.0, value=0.0, step=100.0)

fondos = st.sidebar.slider('Número de fondos a configurar:', min_value=0, max_value=5, value=2)

if fondos == 0:
    porcentaje_inversion = 0.0
    porcentaje_ahorro = 1.0
else:
    porcentaje_inversion = st.sidebar.slider('Porcentaje destinado a inversión:', min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    porcentaje_ahorro = 1 - porcentaje_inversion

# Mostrar entradas relacionadas con el ahorro si se asigna un porcentaje al ahorro
if porcentaje_ahorro > 0:
    tasa_ahorro_anual = st.sidebar.number_input('Interés anual de la cuenta de ahorro (%):', min_value=0.0, value=2.25, step=0.1) / 100
    max_saldo_con_interes = st.sidebar.number_input('Máximo saldo con interés aplicado (€):', min_value=0, value=70000, step=1000)
    descontar_impuestos_de_ahorro = st.sidebar.checkbox('Descontar impuestos de la cuenta de ahorro', value=True)

# Mostrar entradas de configuración de fondos si se asigna un porcentaje a la inversión
fondos_info = []
if porcentaje_inversion > 0 and fondos > 0:
    st.write("## Configuración de Fondos de Inversión")
    fondos_info = [{'porcentaje': 1.0 / fondos} for i in range(fondos)]
    fondos_info = [crear_entrada_fondo(i, fondos_info) for i in range(fondos)]

# Configuración de la proyección
años_proyeccion = st.sidebar.number_input('Años de proyección:', min_value=1, value=30, step=1)

st.sidebar.markdown('---')

# Configuración de los tramos de impuestos
st.sidebar.header('Configuración de Tramos Impositivos')
num_tramos = st.sidebar.number_input('Número de tramos impositivos:', min_value=1, value=4, step=1)
tramos = []
for i in range(num_tramos):
    if i == num_tramos - 1:
        limite = Math.inf
    else:
        limite = st.sidebar.number_input(f'Límite del Tramo {i + 1} (€):', min_value=0, step=1000, value=[6000, 50000, 200000, int(1e9)][i] if i < 4 else 0)
    tipo = st.sidebar.number_input(f'Tipo Impositivo del Tramo {i + 1} (%):', min_value=0.0, max_value=100.0, value=float([19, 21, 23, 27][i]) if i < 4 else 0.0, step=0.1) / 100
    separador = st.sidebar.markdown('---')
    tramos.append((limite, tipo))


# Cálculos
aportacion_inversion = transferencia_mensual * porcentaje_inversion
aportacion_ahorro = transferencia_mensual * porcentaje_ahorro
if porcentaje_ahorro > 0:
    tasa_ahorro_mensual = tasa_ahorro_anual / 12

meses_list = [year * 12 for year in range(1, años_proyeccion + 1)]

proyeccion_completa = []
saldo_anterior = saldo_inicial_ahorro  # Saldo inicial en ahorro
aportacion_total_anual = aportacion_ahorro * 12  # Aportación anual al ahorro

for year, meses in enumerate(meses_list, start=1):
    # Calcular los valores de ahorro
    if porcentaje_ahorro > 0:
        saldo_actual_ahorro, impuestos_ahorro, saldo_anterior, impuestos_anuales_ahorro = calcular_valor_futuro_ahorro_con_interes_y_impuestos(
            aportacion_ahorro, tasa_ahorro_mensual, meses, saldo_anterior, max_saldo_con_interes, descontar_impuestos_de_ahorro)
    else:
        saldo_actual_ahorro, impuestos_anuales_ahorro = 0, 0
    
    # Calcular los valores de la inversión en fondos
    if porcentaje_inversion > 0 and fondos > 0:
        valor_total_fondos = sum(
            calcular_valor_futuro_con_aportaciones_diversificadas(
                aportacion_inversion, fondo['porcentaje'], fondo['rendimiento_anual'] / 12, meses, fondo['saldo_inicial'])
            for fondo in fondos_info
        )
        dinero_invertido_fondos = aportacion_inversion * meses
        beneficio_fondos = calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_fondos)
        impuestos_liquidacion_fondos = calcular_impuestos(beneficio_fondos, tramos)
    else:
        valor_total_fondos = 0
        beneficio_fondos = 0
        impuestos_liquidacion_fondos = 0

    # Sumar dinero total invertido (ahorro + fondos)
    dinero_total_invertido = (aportacion_ahorro + aportacion_inversion) * meses
    valor_total_ahorro_e_inversion = saldo_actual_ahorro + valor_total_fondos

    # Guardar los resultados en la tabla
    entry = {
        "Año": year,
        "Dinero Total Invertido (euros)": round(dinero_total_invertido, 2)
    }
    if porcentaje_ahorro > 0:
        entry.update({
            "Valor Total del Ahorro con Interés (euros)": round(saldo_actual_ahorro, 2),
            "Impuestos Ahorro (euros)": round(impuestos_anuales_ahorro, 2)
        })
    if porcentaje_inversion > 0 and fondos > 0:
        entry.update({
            "Valor Total Invertido en Fondos (euros)": round(valor_total_fondos, 2),
            "Beneficio de Fondos (euros)": round(beneficio_fondos, 2),
            "Impuestos de Liquidación Fondos (euros)": round(impuestos_liquidacion_fondos, 2)
        })
    if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0):
        entry.update({
            "Valor Total Ahorro + Inversión (euros)": round(valor_total_ahorro_e_inversion, 2)
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
    if porcentaje_ahorro > 0:
        st.write("- **Valor Total del Ahorro con Interés (euros)**: Muestra el saldo total acumulado en la cuenta de ahorro, incluyendo los intereses generados hasta ese año. Si la opción está activada, se restan los impuestos correspondientes.")
        st.write("- **Impuestos Ahorro (euros)**: Indica la cantidad de impuestos pagados sobre los intereses generados en la cuenta de ahorro durante el año.")
    st.write("- **Dinero Total Invertido (euros)**: Es la suma total del dinero destinado tanto al ahorro como a la inversión, acumulado hasta el año en cuestión.")
    if porcentaje_inversion > 0 and fondos > 0:
        st.write("- **Valor Total Invertido en Fondos (euros)**: Muestra el valor total de los fondos invertidos, considerando el rendimiento de los fondos hasta ese año.")
        st.write("- **Beneficio de Fondos (euros)**: Representa el beneficio neto obtenido de las inversiones en fondos, después de descontar la cantidad invertida.")
        st.write("- **Impuestos de Liquidación Fondos (euros)**: Indica la cantidad de impuestos a pagar en caso de que se liquiden los fondos en ese año.")
    if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0):
        st.write("- **Valor Total Ahorro + Inversión (euros)**: Representa la suma del valor total del ahorro con el valor total de los fondos invertidos hasta ese año.")

    # Texto antes de los gráficos
    st.write("### Gráficas de la Proyección Financiera")

    # Mostrar gráficos usando Streamlit line_chart
    columnas_grafica = ["Dinero Total Invertido (euros)"]
    if porcentaje_ahorro > 0:
        columnas_grafica.append("Valor Total del Ahorro con Interés (euros)")
    if porcentaje_inversion > 0 and fondos > 0:
        columnas_grafica.append("Valor Total Invertido en Fondos (euros)")
    if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0):
        columnas_grafica.append("Valor Total Ahorro + Inversión (euros)")
    st.line_chart(df_proyeccion_completa.set_index('Año')[columnas_grafica])