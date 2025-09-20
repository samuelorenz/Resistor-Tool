
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

        result = f"Valore resistenza: {formatted_value}\n"
        result += f"Tolleranza: ±{tolerance_val}%\n"
        result += f"Range: {format_value(min_value)} - {format_value(max_value)}\n"
        result += f"Valore esatto: {value:.2f} Ω"

        return result, None
    except Exception as e:
        return None, f"Errore nel calcolo: {str(e)}"


def find_color_code_logic(value, e_series_data):
    try:
        best_match = find_best_color_match(value, e_series_data)

        if best_match:
            result = f"Valore richiesto: {format_value(value)}\n\n"
            result += "Codice colori suggerito:\n"
            result += f"Banda 1: {best_match['band1']}\n"
            result += f"Banda 2: {best_match['band2']}\n"
            result += f"Moltiplicatore: {best_match['multiplier']}\n"
            result += f"Tolleranza: {best_match['tolerance']} (±{best_match['tolerance_value']}%)\n"
            result += f"Valore ottenuto: {format_value(best_match['actual_value'])}\n"
            result += f"Errore: {best_match['error']:.2f}%"
            return result, None
        else:
            return None, "Nessun valore commerciale trovato"

    except ValueError:
        return None, "Inserisci un valore numerico valido"


def find_best_color_match(target_value, e_series_data):
    best_error = float("inf")
    best_match = None

    for series_name, series_values in e_series_data.items():
        for decade in range(-2, 6):  # Decadi da 0.01 a 1M
            for base_value in series_values:
                actual_value = base_value * (10**decade)
                error = abs((actual_value - target_value) / target_value) * 100

                if error < best_error:
                    best_error = error
                    best_match = {
                        "band1": get_color_from_digit(int(str(base_value)[0])),
                        "band2": get_color_from_digit(int(str(base_value)[1]))
                        if len(str(base_value)) > 1
                        else "nero",
                        "multiplier": get_multiplier_color(decade),
                        "tolerance": "oro",  # ±5%
                        "tolerance_value": 5,
                        "actual_value": actual_value,
                        "error": error,
                    }

                    if error < 1:  # Se l'errore è < 1%, accetta
                        return best_match

    return best_match


def calculate_series_parallel_logic(resistances, tolerances, conn_type):
    try:
        if conn_type == "serie":
            total_resistance = sum(resistances)
            calculation = " + ".join([format_value(r) for r in resistances])
        else:  # parallelo
            total_resistance = 1 / sum(1 / r for r in resistances)
            calculation = "1 / (" + " + ".join([f"1/{format_value(r)}" for r in resistances]) + ")"

        tol_mean = sum(tolerances) / len(tolerances) if tolerances else 0
        min_total = total_resistance * (1 - tol_mean / 100)
        max_total = total_resistance * (1 + tol_mean / 100)

        result = f"Resistenze: {[format_value(r) for r in resistances]}\n"
        result += f"Connessione: {conn_type.title()}\n"
        result += f"Calcolo: {calculation}\n\n"
        result += f"Resistenza totale: {format_value(total_resistance)}\n"
        result += f"Tolleranza (media): ±{tol_mean}%\n"
        result += f"Range: {format_value(min_total)} - {format_value(max_total)}"

        return result, total_resistance, None
    except Exception as e:
        return None, None, f"Errore nel calcolo: {str(e)}"


def optimize_with_commercial_logic(resistances, conn_type, series, e_series_data):
    try:
        if not resistances:
            return None, "Nessuna resistenza inserita"

        series_values = e_series_data.get(series, list(e_series_data.values())[0])

        optimized_resistances = []
        result = "Ottimizzazione con valori commerciali:\n\n"

        for i, target_r in enumerate(resistances):
            best_match = find_best_commercial_value(target_r, series_values)
            optimized_resistances.append(best_match["value"])

            result += f"R{i + 1}: {format_value(target_r)} → {format_value(best_match['value'])} "
            result += f"(errore: {best_match['error']:.2f}%)\n"

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

        result += f"\nResistenza totale originale: {format_value(original_total)}\n"
        result += f"Resistenza totale ottimizzata: {format_value(optimized_total)}\n"
        result += f"Errore totale: {total_error_percent:.2f}%"

        return result, None
    except Exception as e:
        return None, f"Errore nell'ottimizzazione: {str(e)}"

def find_best_commercial_value(target_value, series):
    best_error = float('inf')
    best_value = target_value

    for decade in range(-2, 6):
        for base_value in series:
            actual_value = base_value * (10 ** decade)
            error = abs((actual_value - target_value) / target_value) * 100

            if error < best_error:
                best_error = error
                best_value = actual_value

                if error < 0.1:  # Accetta se errore < 0.1%
                    break
        if best_error < 0.1:
            break

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

        tol_mean_percent = (tol1 + tol2) / 2 * 100
        result = f"Simulazione Monte Carlo ({iterations} iterazioni)\n"
        result += f"Tolleranza (media componenti): ±{tol_mean_percent:.2f}%\n\n"
        result += f"Vout teorico: {vout_theoretical:.3f} V\n"
        result += f"Media Vout: {vout_mean:.3f} V\n"
        result += f"Deviazione standard: {vout_std:.3f} V\n"
        result += f"Range Vout: {vout_min:.3f} - {vout_max:.3f} V\n"
        result += f"Errore massimo: {abs(vout_max - vout_min) / vout_theoretical * 100:.2f}%"

        return result, vout_values, vout_theoretical, None
    except Exception as e:
        return None, None, None, f"Errore nella simulazione: {str(e)}"


def calculate_power_logic(voltage, current, resistance, package_power_val, package_name):
    try:
        powers = []
        formulas = []

        if voltage > 0 and current > 0:
            power1 = voltage * current
            powers.append(power1)
            formulas.append(f"P = V × I = {voltage} × {current} = {power1:.6f} W")

        if voltage > 0 and resistance > 0:
            power2 = (voltage**2) / resistance
            powers.append(power2)
            formulas.append(f"P = V²/R = {voltage}²/{resistance} = {power2:.6f} W")

        if current > 0 and resistance > 0:
            power3 = (current**2) * resistance
            powers.append(power3)
            formulas.append(f"P = I² × R = {current}² × {resistance} = {power3:.6f} W")

        if not powers:
            return None, "Inserisci almeno due parametri"

        avg_power = sum(powers) / len(powers)
        safety_factor = package_power_val / avg_power if avg_power > 0 else float('inf')

        result = "Calcolo potenza:\n\n"
        for formula in formulas:
            result += formula + "\n"

        result += f"\nPotenza media: {avg_power:.6f} W\n"
        result += f"Potenza package ({package_name}): {package_power_val} W\n"

        if safety_factor >= 2:
            result += f"Fattore di sicurezza: {safety_factor:.1f}x - OK\n"
            result += "✓ Il package è adeguato"
        elif safety_factor >= 1:
            result += f"Fattore di sicurezza: {safety_factor:.1f}x - Limite\n"
            result += "⚠ Package al limite - considera un package più grande"
        else:
            result += f"Fattore di sicurezza: {safety_factor:.1f}x - INSUFFICIENTE\n"
            result += "✗ Il package non è adeguato - Scegli un package più grande!"

        return result, None
    except Exception as e:
        return None, f"Errore nel calcolo: {str(e)}"
