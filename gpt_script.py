import pandas as pd

# Variables iniciales y funciones
transferencia_mensual = 690  # Transferencia mensual en euros
porcentaje_inversion = 0.7  # 70% de la transferencia mensual se destina a inversión
porcentaje_ahorro = 0.3  # 30% se queda en la cuenta de ahorros con interés del 2.25% TAE

aportacion_inversion = transferencia_mensual * porcentaje_inversion  # Aportación destinada a inversión
aportacion_ahorro = transferencia_mensual * porcentaje_ahorro  # Aportación destinada al ahorro

rendimiento_mensual_msci = 0.06 / 12  # 6% anual para MSCI World
rendimiento_mensual_nasdaq = 0.10 / 12  # 10% anual para Nasdaq-100
tasa_ahorro_anual = 0.0225  # 2.25% TAE para la cuenta de ahorro
tasa_ahorro_mensual = tasa_ahorro_anual / 12  # Conversión a tasa mensual

# Funciones de cálculo
def calcular_valor_futuro_ahorro_con_interes_y_impuestos(aportacion_mensual, tasa_mensual, meses):
    saldo = 0
    impuestos_totales = 0
    for i in range(1, meses + 1):
        interes = saldo * tasa_mensual
        saldo += interes
        saldo += aportacion_mensual
        if i % 12 == 0:
            impuestos_a_pagar = interes * 0.19  # Aplicar 19% a las ganancias cada año
            saldo -= impuestos_a_pagar
            impuestos_totales += impuestos_a_pagar
    return saldo, impuestos_totales

def calcular_valor_futuro_con_aportaciones_diversificadas(aportacion_mensual, porcentaje, rendimiento_mensual, meses):
    saldo = 0
    for _ in range(meses):
        saldo += saldo * rendimiento_mensual
        saldo += aportacion_mensual * porcentaje
    return saldo

def calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_sin_intereses):
    return valor_total_fondos - dinero_invertido_sin_intereses

def calcular_impuestos_ahorro_revisado(saldo_anterior, saldo_actual, aportacion_total_anual):
    beneficio_anual = saldo_actual - saldo_anterior - aportacion_total_anual
    impuestos_anuales = beneficio_anual * 0.19  # Aplicar 19% al beneficio
    return round(impuestos_anuales, 2), round(beneficio_anual, 2)

def calcular_impuestos_liquidacion(beneficio_neto):
    if beneficio_neto <= 6000:
        impuesto = beneficio_neto * 0.19
    elif beneficio_neto <= 50000:
        impuesto = (6000 * 0.19) + ((beneficio_neto - 6000) * 0.21)
    elif beneficio_neto <= 200000:
        impuesto = (6000 * 0.19) + ((50000 - 6000) * 0.21) + ((beneficio_neto - 50000) * 0.23)
    else:
        impuesto = (6000 * 0.19) + ((50000 - 6000) * 0.21) + ((200000 - 50000) * 0.23) + ((beneficio_neto - 200000) * 0.27)
    return round(impuesto, 2)

# Proyección anual
proyeccion_completa = []
saldo_anterior = 0  # Saldo inicial en ahorro
aportacion_total_anual = aportacion_ahorro * 12  # Aportación anual al ahorro

for year in range(1, 31):
    meses = year * 12
    # Calcular los valores de ahorro
    saldo_actual_ahorro, impuestos_ahorro = calcular_valor_futuro_ahorro_con_interes_y_impuestos(
        aportacion_ahorro, tasa_ahorro_mensual, meses)
    impuestos_ahorro_revisado, beneficio_anual_ahorro = calcular_impuestos_ahorro_revisado(saldo_anterior, saldo_actual_ahorro, aportacion_total_anual)
    
    # Calcular los valores de la inversión en fondos
    valor_total_fondos = calcular_valor_futuro_con_aportaciones_diversificadas(
        aportacion_inversion, 0.7, rendimiento_mensual_msci, meses) + calcular_valor_futuro_con_aportaciones_diversificadas(
        aportacion_inversion, 0.3, rendimiento_mensual_nasdaq, meses)
    
    dinero_invertido_fondos = aportacion_inversion * meses
    beneficio_fondos = calcular_beneficio_fondos(valor_total_fondos, dinero_invertido_fondos)
    impuestos_liquidacion_fondos = calcular_impuestos_liquidacion(beneficio_fondos)
    
    # Sumar dinero total invertido (ahorro + fondos)
    dinero_total_invertido = (aportacion_ahorro + aportacion_inversion) * meses
    
    # Guardar los resultados en la tabla
    proyeccion_completa.append({
        "Año": year,
        "Valor Total del Ahorro con Interés (euros)": round(saldo_actual_ahorro, 2),
        "Beneficio Anual del Ahorro (euros)": round(beneficio_anual_ahorro, 2),
        "Impuestos Pagados en Ahorro (euros)": round(impuestos_ahorro_revisado, 2),
        "Valor Total Invertido en Fondos (euros)": round(valor_total_fondos, 2),
        "Beneficio de Fondos (euros)": round(beneficio_fondos, 2),
        "Impuestos de Liquidación Fondos (euros)": round(impuestos_liquidacion_fondos, 2),
        "Dinero Total Invertido (euros)": round(dinero_total_invertido, 2)
    })
    
    # Actualizar el saldo anterior para el próximo cálculo
    saldo_anterior = saldo_actual_ahorro

# Convertir los resultados en un DataFrame
df_proyeccion_completa = pd.DataFrame(proyeccion_completa)

import ace_tools as tools; tools.display_dataframe_to_user(name="Proyección Completa Anual a 30 Años", dataframe=df_proyeccion_completa)
