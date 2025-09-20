
import random
import numpy as np
from resistor_lib import (
    e_series,
    get_color_from_digit,
    get_multiplier_color,
    find_best_commercial_value as find_best_commercial_value_from_lib,
)
from utils import format_value


def calculate_color_code_logic(
    color_codes, tolerance_colors, band1, band2, multiplier, tolerance
):
    try:
        band1_val = color_codes[band1][0]
        band2_val = color_codes[band2][0]
        multiplier_val = color_codes[multiplier][0]
        tolerance_val = tolerance_colors[tolerance][0]

        value = (band1_val * 10 + band2_val) * (10**multiplier_val)
        min_value = value * (1 - tolerance_val / 100)
        max_value = value * (1 + tolerance_val / 100)

        formatted_value = format_value(value)

        result = f"--- Analisi del Codice Colori (IEC 60062) ---\n\n"
        result += f"Valore Nominale: {formatted_value}\n"
        result += f"Tolleranza: ±{tolerance_val}%\n"
        result += f"Range di funzionamento: da {format_value(min_value)} a {format_value(max_value)}\n\n"
        result += f"Spiegazione:\n"
        result += f"Il valore è calcolato combinando le prime due bande ({band1_val} e {band2_val}) e moltiplicando per 10^{multiplier_val}."

        return result, None
    except Exception as e:
        return None, f"Errore nel calcolo: {str(e)}"


def find_color_code_logic(value, e_series_data):
    try:
        best_match = find_best_color_match(value, e_series_data)

        if best_match:
            result = f"--- Ricerca Valore Commerciale (IEC 60063) ---\n\n"
            result += f"Valore richiesto: {format_value(value)}\n"
            result += f"Serie E selezionata: {best_match['series_name']}\n\n"
            result += "Codice colori suggerito per il valore più vicino:\n"
            result += f"- Banda 1: {best_match['band1']}\n"
            result += f"- Banda 2: {best_match['band2']}\n"
            result += f"- Moltiplicatore: {best_match['multiplier']}\n"
            result += f"- Tolleranza: {best_match['tolerance']} (±{best_match['tolerance_value']}%)\n\n"
            result += f"Valore commerciale ottenuto: {format_value(best_match['actual_value'])}\n"
            result += f"Errore rispetto al valore richiesto: {best_match['error']:.2f}%\n\n"
            result += "Spiegazione:\nÈ stato cercato il valore standard nella serie selezionata che minimizza l'errore percentuale."
            return result, None
        else:
            return None, "Nessun valore commerciale trovato"

    except ValueError:
        return None, "Inserisci un valore numerico valido"


def find_best_color_match(target_value, e_series_data):
    best_error = float("inf")
    best_match = None

    for series_name, series_values in e_series_data.items():
        for decade in range(-2, 8):
            for base_value in series_values:
                actual_value = base_value * (10**decade)
                error = abs((actual_value - target_value) / target_value) * 100

                if error < best_error:
                    best_error = error
                    best_match = {
                        "series_name": series_name,
                        "band1": get_color_from_digit(int(str(base_value)[0])),
                        "band2": get_color_from_digit(int(str(base_value)[1]))
                        if len(str(base_value)) > 1
                        else "nero",
                        "multiplier": get_multiplier_color(decade),
                        "tolerance": "oro",  # Default, l'utente può cambiarlo
                        "tolerance_value": 5,
                        "actual_value": actual_value,
                        "error": error,
                    }
    return best_match


def calculate_series_parallel_logic(resistances, tolerances, conn_type):
    try:
        if conn_type == "serie":
            total_resistance = sum(resistances)
            formula = "R_tot = R1 + R2 + ..."
            calculation = f"R_tot = {' + '.join([format_value(r) for r in resistances])}"
        else:  # parallelo
            total_resistance = 1 / sum(1 / r for r in resistances)
            formula = "R_tot = 1 / (1/R1 + 1/R2 + ...)"
            calculation = f"R_tot = 1 / ({' + '.join([f'1/{format_value(r)}' for r in resistances])})"

        tol_mean = sum(tolerances) / len(tolerances) if tolerances else 0
        min_total = total_resistance * (1 - tol_mean / 100)
        max_total = total_resistance * (1 + tol_mean / 100)

        result = f"--- Calcolo {conn_type.title()} ---\n\n"
        result += f"Formula utilizzata: {formula}\n"
        result += f"Calcolo: {calculation}\n\n"
        result += f"Resistenza Totale Calcolata: {format_value(total_resistance)}\n"
        result += f"Tolleranza media (approssimata): ±{tol_mean:.2f}%\n"
        result += f"Range di funzionamento stimato: da {format_value(min_total)} a {format_value(max_total)}\n"

        return result, total_resistance, None
    except Exception as e:
        return None, None, f"Errore nel calcolo: {str(e)}"


def optimize_with_commercial_logic(resistances, conn_type, series, e_series_data):
    try:
        if not resistances:
            return None, "Nessuna resistenza inserita"

        series_values = e_series_data.get(series, list(e_series_data.values())[0])

        result = f"--- Ottimizzazione con Valori Commerciali (Serie {series}) ---\n\n"
        result += "Spiegazione: Ogni resistenza teorica viene sostituita con il valore più vicino disponibile nella serie E scelta.\n\n"

        optimized_resistances = []
        for i, target_r in enumerate(resistances):
            best_match = find_best_commercial_value(target_r, series_values)
            optimized_resistances.append(best_match["value"])
            result += f"- R{i + 1}: {format_value(target_r)} → {format_value(best_match['value'])} (Errore: {best_match['error']:.2f}%)\n"

        if conn_type == "serie":
            optimized_total = sum(optimized_resistances)
            original_total = sum(resistances)
        else:
            optimized_total = 1 / sum(1 / r for r in optimized_resistances)
            original_total = 1 / sum(1 / r for r in resistances)

        total_error_percent = (
            abs((optimized_total - original_total) / original_total) * 100
            if original_total != 0
            else 0
        )

        result += f"\n--- Risultato Finale ---\n"
        result += f"Resistenza totale teorica: {format_value(original_total)}\n"
        result += f"Resistenza totale ottimizzata: {format_value(optimized_total)}\n"
        result += f"Errore totale sull'equivalente: {total_error_percent:.2f}%\n"

        return result, None
    except Exception as e:
        return None, f"Errore nell'ottimizzazione: {str(e)}"


def find_best_commercial_value(target_value, series):
    best_error = float('inf')
    best_value = target_value

    for decade in range(-2, 8):
        for base_value in series:
            actual_value = base_value * (10 ** decade)
            error = abs((actual_value - target_value) / target_value) * 100

            if error < best_error:
                best_error = error
                best_value = actual_value

    return {'value': best_value, 'error': best_error}

def run_monte_carlo_logic(vin, iterations, r1_nominal, tol1, r2_nominal, tol2):
    try:
        vout_values = []
        for _ in range(iterations):
            r1 = r1_nominal * random.uniform(1 - tol1, 1 + tol1)
            r2 = r2_nominal * random.uniform(1 - tol2, 1 + tol2)
            vout = vin * r2 / (r1 + r2)
            vout_values.append(vout)

        vout_mean = np.mean(vout_values)
        vout_std = np.std(vout_values)
        vout_min = np.min(vout_values)
        vout_max = np.max(vout_values)

        vout_theoretical = vin * r2_nominal / (r1_nominal + r2_nominal)

        result = f"--- Analisi Monte Carlo per Partitore di Tensione ---\n\n"
        result += "Spiegazione: La simulazione Monte Carlo testa il circuito migliaia di volte, \n"
        result += "variando casualmente i valori dei resistori entro la loro tolleranza. \n"
        result += "Questo aiuta a prevedere il comportamento reale del circuito.\n\n"
        result += f"Parametri di simulazione:\n"
        result += f"- R1: {format_value(r1_nominal)} ±{tol1*100:.2f}%\n"
        result += f"- R2: {format_value(r2_nominal)} ±{tol2*100:.2f}%\n"
        result += f"- Vin: {vin} V\n"
        result += f"- Iterazioni: {iterations}\n\n"
        result += f"--- Risultati Statistici ---\n"
        result += f"Vout Teorico (calcolato con valori nominali): {vout_theoretical:.4f} V\n"
        result += f"Vout Medio (risultato della simulazione): {vout_mean:.4f} V\n"
        result += f"Deviazione Standard (σ): {vout_std:.4f} V\n"
        result += f"Range Vout: da {vout_min:.4f} V a {vout_max:.4f} V\n"

        return result, vout_values, vout_theoretical, None
    except Exception as e:
        return None, None, None, f"Errore nella simulazione: {str(e)}"


def calculate_power_logic(voltage, current, resistance, package_power_val, package_name):
    try:
        powers = []
        formulas = []

        result = "--- Calcolo Potenza Dissipata ---\n\n"
        result += "Spiegazione: La potenza dissipata da un resistore può essere calcolata con la legge di Ohm, \n"
        result += "usando due delle tre grandezze: Tensione (V), Corrente (I) e Resistenza (R).\n\n"

        if voltage > 0 and current > 0:
            power = voltage * current
            powers.append(power)
            formulas.append(f"- Con Tensione e Corrente: P = V × I = {voltage}V × {current}A = {power:.4f} W")

        if voltage > 0 and resistance > 0:
            power = (voltage**2) / resistance
            powers.append(power)
            formulas.append(f"- Con Tensione e Resistenza: P = V²/R = {voltage}²V / {resistance}Ω = {power:.4f} W")

        if current > 0 and resistance > 0:
            power = (current**2) * resistance
            powers.append(power)
            formulas.append(f"- Con Corrente e Resistenza: P = I²×R = {current}²A × {resistance}Ω = {power:.4f} W")

        if not powers:
            return None, "Per calcolare la potenza, fornisci almeno due dei tre parametri (V, I, R)."

        result += "Formule Applicate:\n"
        result += "\n".join(formulas)
        result += "\n\n"

        avg_power = sum(powers) / len(powers)
        result += f"--- Analisi Risultati ---\n"
        result += f"Potenza media dissipata: {avg_power:.4f} W\n"
        result += "(Se hai fornito tre parametri, la media serve a verificare la coerenza dei tuoi dati secondo la legge di Ohm)\n\n"

        result += f"--- Valutazione del Package ({package_name}) ---\n"
        result += f"Potenza massima del package: {package_power_val} W\n"
        safety_factor = package_power_val / avg_power if avg_power > 0 else float('inf')
        result += f"Fattore di sicurezza: {safety_factor:.1f}x\n\n"

        result += "Spiegazione del Derating:\n"
        result += "Un buon progetto richiede un 'derating' di potenza, cioè si sceglie un componente che possa dissipare \n"
        result += "molta più potenza di quella richiesta. Una regola comune è usare un resistore con potenza doppia (derating del 50%), \n"
        result += "per garantirne affidabilità e durata, specialmente ad alte temperature (come richiesto da standard quali AEC-Q200).\n\n"

        if safety_factor >= 2:
            result += "✓ RACCOMANDAZIONE: Il package è scelto correttamente e opera con un buon margine di sicurezza."
        elif safety_factor >= 1.2:
            result += "⚠ ATTENZIONE: Il package è tecnicamente sufficiente, ma opera con un margine di sicurezza ridotto. Considera un package più grande per una maggiore affidabilità."
        else:
            result += "✗ CRITICO: Il package non è adeguato! La potenza dissipata è superiore a quella che può gestire. Scegli IMMEDIATAMENTE un package con potenza superiore."

        return result, None
    except Exception as e:
        return None, f"Errore nel calcolo: {str(e)}"





















































































































































































































































































































































































































































































































































































































































































































































































































'