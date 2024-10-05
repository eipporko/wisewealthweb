# WiseWealthWeb - app.py

import streamlit as st
import pandas as pd
import math as Math
from translations import TRANSLATIONS

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

    # Calcular impuestos solo sobre los intereses acumulados del año
    if intereses_acumulados_anual > 0:
        impuestos_anuales = calcular_impuestos(intereses_acumulados_anual)
        if descontar_impuestos_de_ahorro:
            saldo -= impuestos_anuales  # Restar los impuestos al saldo si se elige descontar de la cuenta de ahorro
        impuestos_totales += impuestos_anuales  # Sumar al total de impuestos
    else:
        impuestos_anuales = 0
    
    return saldo, impuestos_totales, saldo, impuestos_anuales


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


def crear_entrada_fondo(index, fondos_info, idioma):
    default_names = ['MSCI World', 'Nasdaq-100']
    st.subheader(f"{TRANSLATIONS[idioma]['fund']} {index + 1}")
    nombre_fondo = st.text_input(f"{TRANSLATIONS[idioma]['fund_name']} {index + 1}:", value=default_names[index] if index < len(default_names) else f"{TRANSLATIONS[idioma]['fund']} {index + 1}", key=f'nombre_fondo_{index}')
    rendimiento_anual = st.number_input(f"{TRANSLATIONS[idioma]['annual_return']} {index + 1} (%):", min_value=0.0, value=6.0 if index == 0 else 10.0, step=0.1, key=f'rendimiento_anual_{index}') / 100
    porcentaje_fondo = st.slider(f"{TRANSLATIONS[idioma]['percentage_allocated']} {index + 1}:", min_value=0.0, max_value=1.0, value=fondos_info[index]['porcentaje'] if fondos_info else (0.7 if index == 0 else 0.3), step=0.05, key=f'porcentaje_fondo_{index}')
    saldo_inicial_fondo = st.number_input(f"{TRANSLATIONS[idioma]['initial_balance']} {index + 1} (€):", min_value=0.0, value=0.0, step=100.0, key=f'saldo_inicial_{index}')

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

# Selección de idioma
idioma = 'es'
idioma = st.sidebar.selectbox(TRANSLATIONS['es']['select_language'], ['es', 'en'])

# Mostrar la descripción inicial y el aviso importante
st.markdown(
    f"""
    # WiseWealthWeb

    **WiseWealthWeb** {TRANSLATIONS[idioma]['description']}
    
    ## {TRANSLATIONS[idioma]['instructions_title']}
    1. {TRANSLATIONS[idioma]['instructions_1']}
    2. {TRANSLATIONS[idioma]['instructions_2']}
    3. {TRANSLATIONS[idioma]['instructions_3']}
    4. {TRANSLATIONS[idioma]['instructions_4']}
    5. {TRANSLATIONS[idioma]['instructions_5']}

    ## {TRANSLATIONS[idioma]['important_notice']}
    > ⚠️ **{TRANSLATIONS[idioma]['risk_warning']}**
    """
)

# Entradas del usuario
st.sidebar.header(TRANSLATIONS[idioma]['projection_settings'])
transferencia_mensual = st.sidebar.number_input(TRANSLATIONS[idioma]['monthly_transfer'], min_value=0, value=690, step=10)
saldo_inicial_ahorro = st.sidebar.number_input(TRANSLATIONS[idioma]['initial_savings_balance'], min_value=0.0, value=0.0, step=100.0)

fondos = st.sidebar.slider(TRANSLATIONS[idioma]['number_of_funds'], min_value=0, max_value=5, value=2)

if fondos == 0:
    porcentaje_inversion = 0.0
    porcentaje_ahorro = 1.0
else:
    porcentaje_inversion = st.sidebar.slider(TRANSLATIONS[idioma]['percentage_investment'], min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    porcentaje_ahorro = 1 - porcentaje_inversion

# Mostrar entradas relacionadas con el ahorro si se asigna un porcentaje al ahorro
if porcentaje_ahorro > 0:
    tasa_ahorro_anual = st.sidebar.number_input(TRANSLATIONS[idioma]['annual_savings_interest'], min_value=0.0, value=2.25, step=0.1) / 100
    max_saldo_con_interes = st.sidebar.number_input(TRANSLATIONS[idioma]['max_balance_interest'], min_value=0, value=70000, step=1000)
    descontar_impuestos_de_ahorro = st.sidebar.checkbox(TRANSLATIONS[idioma]['deduct_taxes'], value=True)

# Mostrar entradas de configuración de fondos si se asigna un porcentaje a la inversión
fondos_info = []
if porcentaje_inversion > 0 and fondos > 0:
    st.write("## " + TRANSLATIONS[idioma]['fund_settings'])
    fondos_info = [{'porcentaje': 1.0 / fondos} for i in range(fondos)]
    fondos_info = [crear_entrada_fondo(i, fondos_info, idioma) for i in range(fondos)]

# Configuración de la proyección
años_proyeccion = st.sidebar.number_input(TRANSLATIONS[idioma]['projection_years'], min_value=1, value=30, step=1)

st.sidebar.markdown('---')

# Configuración de los tramos de impuestos
st.sidebar.header(TRANSLATIONS[idioma]['tax_bracket_settings'])
num_tramos = st.sidebar.number_input(TRANSLATIONS[idioma]['number_of_tax_brackets'], min_value=1, value=4, step=1)
tramos = []
for i in range(num_tramos):
    if i == num_tramos - 1:
        limite = Math.inf
    else:
        limite = st.sidebar.number_input(f"{TRANSLATIONS[idioma]['bracket_limit']} {i + 1} (€):", min_value=0, step=1000, value=[6000, 50000, 200000, int(1e9)][i] if i < 4 else 0)
    tipo = st.sidebar.number_input(f"{TRANSLATIONS[idioma]['tax_rate']} {i + 1} (%):", min_value=0.0, max_value=100.0, value=float([19, 21, 23, 27][i]) if i < 4 else 0.0, step=0.1) / 100
    separador = st.sidebar.markdown('---')
    tramos.append((limite, tipo))

# Cálculos y generación de la proyección
aportacion_inversion = transferencia_mensual * porcentaje_inversion
aportacion_ahorro = transferencia_mensual * porcentaje_ahorro
if porcentaje_ahorro > 0:
    tasa_ahorro_mensual = tasa_ahorro_anual / 12

proyeccion_completa = []
saldo_anterior = saldo_inicial_ahorro  # Saldo inicial en ahorro
aportacion_total_anual = aportacion_ahorro * 12  # Aportación anual al ahorro

for year in range(1, años_proyeccion + 1):
    # Calcular los valores de ahorro
    if porcentaje_ahorro > 0:
        saldo_actual_ahorro, impuestos_ahorro, saldo_anterior, impuestos_anuales_ahorro = calcular_valor_futuro_ahorro_con_interes_y_impuestos(
            aportacion_ahorro, tasa_ahorro_mensual, 12, saldo_anterior, max_saldo_con_interes, descontar_impuestos_de_ahorro)
    else:
        saldo_actual_ahorro, impuestos_anuales_ahorro = 0, 0
    
    # Calcular los valores de la inversión en fondos
    if porcentaje_inversion > 0 and fondos > 0:
        valor_total_fondos = 0
        detalle_fondos = []
        for fondo in fondos_info:
            valor_fondo = calcular_valor_futuro_con_aportaciones_diversificadas(
                aportacion_inversion, fondo['porcentaje'], fondo['rendimiento_anual'] / 12, 12, fondo['saldo_inicial']
            )
            valor_total_fondos += valor_fondo
            detalle_fondos.append(f"{fondo['nombre']}: {round(valor_fondo, 2)} €")
            # Actualizar el saldo inicial para el próximo año
            fondo['saldo_inicial'] = valor_fondo

        dinero_invertido_fondos = aportacion_inversion * 12 * year
        beneficio_fondos = calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_fondos)
        impuestos_liquidacion_fondos = calcular_impuestos(beneficio_fondos, tramos)
    else:
        valor_total_fondos = 0
        detalle_fondos = []
        beneficio_fondos = 0
        impuestos_liquidacion_fondos = 0

    # Sumar dinero total invertido (ahorro + fondos)
    dinero_total_invertido = (aportacion_ahorro + aportacion_inversion) * 12 * year
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
            "Impuestos de Liquidación Fondos (euros)": round(impuestos_liquidacion_fondos, 2),
            "Detalle de Fondos": "; ".join(detalle_fondos)
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

def formato_moneda(valor, idioma='es'):
    if idioma == 'en':
        return "{:,.2f}".format(valor)
    elif idioma == 'es':
        return "{:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

if st.button(TRANSLATIONS[idioma]['calculate_projection']):
    df_proyeccion_completa = obtener_proyeccion_dataframe(proyeccion_completa)
    st.write(f"## {TRANSLATIONS[idioma]['financial_projection_results']}")
    st.dataframe(df_proyeccion_completa.set_index('Año'))

    # Descripción de cada valor de la tabla
    st.write(f"### {TRANSLATIONS[idioma]['projection_summary']}")
    st.write("- **Año**: Representa el año de la proyección en curso.")
    if porcentaje_ahorro > 0:
        st.write("- **Valor Total del Ahorro con Interés (euros)**: Muestra el saldo total acumulado en la cuenta de ahorro, incluyendo los intereses generados hasta ese año. Si la opción está activada, se restan los impuestos correspondientes.")
        st.write("- **Impuestos Ahorro (euros)**: Indica la cantidad de impuestos pagados sobre los intereses generados en la cuenta de ahorro durante el año.")
    st.write("- **Dinero Total Invertido (euros)**: Es la suma total del dinero destinado tanto al ahorro como a la inversión, acumulado hasta el año en cuestión.")
    if porcentaje_inversion > 0 and fondos > 0:
        st.write("- **Valor Total Invertido en Fondos (euros)**: Muestra el valor total de los fondos invertidos, considerando el rendimiento de los fondos hasta ese año.")
        st.write("- **Beneficio de Fondos (euros)**: Representa el beneficio neto obtenido de las inversiones en fondos, después de descontar la cantidad invertida.")
        st.write("- **Impuestos de Liquidación Fondos (euros)**: Indica la cantidad de impuestos a pagar en caso de que se liquiden los fondos en ese año.")
        st.write("- **Detalle de Fondos**: Desglose del rendimiento individual de cada fondo de inversión.")
    if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0):
        st.write("- **Valor Total Ahorro + Inversión (euros)**: Representa la suma del valor total del ahorro con el valor total de los fondos invertidos hasta ese año.")

    st.write('---')

    # Texto antes de los gráficos
    st.write(f"### {TRANSLATIONS[idioma]['projection_charts']}")

    # Mostrar gráficos usando Streamlit line_chart
    columnas_grafica = ["Dinero Total Invertido (euros)"]
    if porcentaje_ahorro > 0:
        columnas_grafica.append("Valor Total del Ahorro con Interés (euros)")
    if porcentaje_inversion > 0 and fondos > 0:
        columnas_grafica.append("Valor Total Invertido en Fondos (euros)")
    if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0):
        columnas_grafica.append("Valor Total Ahorro + Inversión (euros)")
    st.line_chart(df_proyeccion_completa.set_index('Año')[columnas_grafica])

    st.write('---')

    # Resumen de la proyección
    st.write(f"### {TRANSLATIONS[idioma]['projection_summary']}")
    total_años = años_proyeccion
    total_invertido = df_proyeccion_completa["Dinero Total Invertido (euros)"].iloc[-1]
    total_ahorro = df_proyeccion_completa["Valor Total del Ahorro con Interés (euros)"].iloc[-1] if porcentaje_ahorro > 0 else 0
    total_fondos = df_proyeccion_completa["Valor Total Invertido en Fondos (euros)"].iloc[-1] if porcentaje_inversion > 0 and fondos > 0 else 0
    impuestos_liquidacion_fondos = df_proyeccion_completa["Impuestos de Liquidación Fondos (euros)"].iloc[-1] if porcentaje_inversion > 0 and fondos > 0 else 0
    valor_total_ahorro_e_inversion = df_proyeccion_completa["Valor Total Ahorro + Inversión (euros)"].iloc[-1] if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0) else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        if porcentaje_ahorro > 0:
            st.metric(label="Total Acumulado en Ahorro", value=formato_moneda(total_ahorro, idioma=idioma))
        if porcentaje_inversion > 0 and fondos > 0:
            st.metric(label="Total Acumulado en Fondos", value=formato_moneda(total_fondos, idioma=idioma))
    with col2:
        if porcentaje_ahorro > 0 or (porcentaje_inversion > 0 and fondos > 0):
            st.metric(label="Valor Total Ahorro + Inversión", value=formato_moneda(valor_total_ahorro_e_inversion, idioma=idioma))
            if porcentaje_inversion > 0 and fondos > 0:
                st.metric(label="Impuestos a Pagar por Liquidación de Fondos", value=formato_moneda(impuestos_liquidacion_fondos, idioma=idioma))
    with col3:
        st.metric(label="Años de Proyección", value=total_años)
        st.metric(label="Total Invertido", value=formato_moneda(total_invertido, idioma=idioma))

    if porcentaje_inversion > 0 and fondos > 0:
        st.write(f"### {TRANSLATIONS[idioma]['investment_fund_performance']}")
        for fondo in fondos_info:
            st.write(f"- **{fondo['nombre']}**: {formato_moneda(fondo['saldo_inicial'])}")
