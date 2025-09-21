
import random
import numpy as np
from resistor_lib import (
    e_series, get_color_from_digit, get_multiplier_color,
    eia96_value_codes, eia96_multiplier_codes,
    derating_start_temp_c, derating_percent_per_c
)
from utils import format_value

def decode_smd_code_logic(code, code_type):
    try:
        code = code.strip().upper()
        if not code:
            return None, "Il codice non può essere vuoto."

        if code_type == "standard":
            return decode_standard_smd(code)
        elif code_type == "eia96":
            return decode_eia96_smd(code)
        else:
            return None, "Tipo di codice non valido."

    except Exception as e:
        return None, f"Errore durante la decodifica: {str(e)}"

def decode_standard_smd(code):
    result = f"--- Decodifica Codice SMD Standard ---\n\nCodice Inserito: {code}\n"
    value = 0

    if 'R' in code:
        parts = code.split('R')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None, "Formato 'R' non valido. Esempio valido: '4R7' per 4.7Ω."
        value = float(f"{parts[0]}.{parts[1]}")
        result += f"Spiegazione: La 'R' rappresenta il punto decimale. Valore: {parts[0]}.{parts[1]}Ω.\n"
    elif len(code) == 3:
        mantissa = int(code[:2])
        exponent = int(code[2])
        value = mantissa * (10 ** exponent)
        result += f"Spiegazione: Le prime due cifre ({code[:2]}) sono la mantissa, la terza ({code[2]}) è il moltiplicatore (10^{code[2]}).\n"
    elif len(code) == 4:
        mantissa = int(code[:3])
        exponent = int(code[3])
        value = mantissa * (10 ** exponent)
        result += f"Spiegazione: Le prime tre cifre ({code[:3]}) sono la mantissa, la quarta ({code[3]}) è il moltiplicatore (10^{code[3]}).\n"
    else:
        return None, "Il codice standard deve avere 3 o 4 cifre, o usare la notazione 'R'."

    result += f"\nValore Calcolato: {format_value(value)}"
    return result, None

def decode_eia96_smd(code):
    if len(code) != 3:
        return None, "Il codice EIA-96 deve essere di 3 caratteri (2 cifre per il valore, 1 lettera per il moltiplicatore)."

    value_code = code[:2]
    multiplier_char = code[2]

    if value_code not in eia96_value_codes:
        return None, f"Codice valore '{value_code}' non trovato nello standard EIA-96."
    if multiplier_char not in eia96_multiplier_codes:
        return None, f"Lettera moltiplicatore '{multiplier_char}' non valida."

    base_value = eia96_value_codes[value_code]
    multiplier = eia96_multiplier_codes[multiplier_char]
    final_value = base_value * multiplier

    result = f"--- Decodifica Codice EIA-96 ---\n\nCodice Inserito: {code}\n"
    result += f"Spiegazione:\n"
    result += f"- Le prime due cifre '{value_code}' corrispondono al valore base: {base_value}.\n"
    result += f"- La lettera '{multiplier_char}' corrisponde a un moltiplicatore: x{multiplier}.\n\n"
    result += f"Calcolo: {base_value} × {multiplier} = {final_value}\n"
    result += f"Valore Calcolato: {format_value(final_value)}"
    return result, None

def calculate_power_logic(voltage, current, resistance, package_power_val, package_name, ambient_temp):
    try:
        # ... (calcolo potenza media, come prima) ...
        powers = []
        if voltage > 0 and current > 0: powers.append(voltage * current)
        if voltage > 0 and resistance > 0: powers.append((voltage**2) / resistance)
        if current > 0 and resistance > 0: powers.append((current**2) * resistance)
        if not powers: return None, "Fornisci almeno due parametri (V, I, R)."
        avg_power = sum(powers) / len(powers)

        # Calcolo Derating Termico
        derated_power = package_power_val
        if ambient_temp > derating_start_temp_c:
            temp_diff = ambient_temp - derating_start_temp_c
            derating_factor = temp_diff * (derating_percent_per_c / 100.0)
            derated_power = package_power_val * (1 - derating_factor)
            if derated_power < 0: derated_power = 0

        # Costruzione della stringa di risultato
        result = f"--- Analisi Potenza e Derating Termico ---\n\n"
        result += f"Potenza dissipata calcolata: {avg_power:.4f} W\n\n"
        result += f"--- Valutazione Package: {package_name} ---\n"
        result += f"Potenza Nominale Package (a 25°C): {package_power_val} W\n"
        result += f"Temperatura Ambiente Impostata: {ambient_temp}°C\n\n"
        result += f"--- Analisi Derating ---\n"
        result += f"La potenza massima di un resistore diminuisce con la temperatura. \n"
        result += f"(Modello usato: derating lineare a partire da {derating_start_temp_c}°C)\n"
        result += f"Potenza Massima Reale a {ambient_temp}°C: {derated_power:.4f} W\n\n"

        result += f"--- Raccomandazioni ---\n"
        if avg_power > derated_power:
            result += f"✗ CRITICO: La potenza dissipata ({avg_power:.4f}W) supera la potenza massima del package alla temperatura di lavoro ({derated_power:.4f}W). Rischio di guasto imminente! Scegli un package più grande."
        else:
            safety_factor_derated = derated_power / avg_power if avg_power > 0 else float('inf')
            result += f"Fattore di Sicurezza (reale, a {ambient_temp}°C): {safety_factor_derated:.1f}x\n"
            if safety_factor_derated >= 2.0:
                result += "✓ OTTIMO: Il componente lavora in un regime di sicurezza eccellente."
            elif safety_factor_derated >= 1.5:
                result += "✓ BUONO: Il componente ha un margine di sicurezza adeguato per la maggior parte delle applicazioni."
            else:
                result += "⚠ ATTENZIONE: Margine di sicurezza ridotto. Il componente potrebbe surriscaldarsi in condizioni di stress o scarsa ventilazione. Valuta un package superiore per una maggiore affidabilità."
        
        return result, None

    except Exception as e:
        return None, f"Errore nel calcolo: {str(e)}"

# ... (le altre funzioni logiche rimangono invariate) ...

def calculate_color_code_logic(color_codes, tolerance_colors, band1, band2, multiplier, tolerance):
    try:
        band1_val = color_codes[band1][0]
        band2_val = color_codes[band2][0]
        multiplier_val = color_codes[multiplier][0]
        tolerance_val = tolerance_colors[tolerance][0]
        value = (band1_val * 10 + band2_val) * (10**multiplier_val)
        min_value = value * (1 - tolerance_val / 100)
        max_value = value * (1 + tolerance_val / 100)
        result = f"--- Analisi del Codice Colori (IEC 60062) ---\n\nValore Nominale: {format_value(value)}\nTolleranza: ±{tolerance_val}%\nRange di funzionamento: da {format_value(min_value)} a {format_value(max_value)}\n\nSpiegazione:\nIl valore è calcolato combinando le prime due bande ({band1_val} e {band2_val}) e moltiplicando per 10^{multiplier_val}."
        return result, None
    except Exception as e:
        return None, f"Errore nel calcolo: {str(e)}"

def find_color_code_logic(value, e_series_data):
    try:
        best_match = find_best_color_match(value, e_series_data)
        if best_match:
            result = f"--- Ricerca Valore Commerciale (IEC 60063) ---\n\nValore richiesto: {format_value(value)}\nSerie E selezionata: {best_match['series_name']}\n\nCodice colori suggerito per il valore più vicino:\n- Banda 1: {best_match['band1']}\n- Banda 2: {best_match['band2']}\n- Moltiplicatore: {best_match['multiplier']}\n- Tolleranza: {best_match['tolerance']} (±{best_match['tolerance_value']}%)\n\nValore commerciale ottenuto: {format_value(best_match['actual_value'])}\nErrore rispetto al valore richiesto: {best_match['error']:.2f}%\n\nSpiegazione:\nÈ stato cercato il valore standard nella serie selezionata che minimizza l'errore percentuale."
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
                        "band2": get_color_from_digit(int(str(base_value)[1])) if len(str(base_value)) > 1 else "nero",
                        "multiplier": get_multiplier_color(decade),
                        "tolerance": "oro",
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
        else:
            total_resistance = 1 / sum(1 / r for r in resistances)
            formula = "R_tot = 1 / (1/R1 + 1/R2 + ...)"
            calculation = f"R_tot = 1 / ({' + '.join([f'1/{format_value(r)}' for r in resistances])})"
        tol_mean = sum(tolerances) / len(tolerances) if tolerances else 0
        min_total = total_resistance * (1 - tol_mean / 100)
        max_total = total_resistance * (1 + tol_mean / 100)
        result = f"--- Calcolo {conn_type.title()} ---\n\nFormula utilizzata: {formula}\nCalcolo: {calculation}\n\nResistenza Totale Calcolata: {format_value(total_resistance)}\nTolleranza media (approssimata): ±{tol_mean:.2f}%\nRange di funzionamento stimato: da {format_value(min_total)} a {format_value(max_total)}\n"
        return result, total_resistance, None
    except Exception as e:
        return None, None, f"Errore nel calcolo: {str(e)}"

def optimize_with_commercial_logic(resistances, conn_type, series, e_series_data):
    try:
        if not resistances: return None, "Nessuna resistenza inserita"
        series_values = e_series_data.get(series, list(e_series_data.values())[0])
        result = f"--- Ottimizzazione con Valori Commerciali (Serie {series}) ---\n\nSpiegazione: Ogni resistenza teorica viene sostituita con il valore più vicino disponibile nella serie E scelta.\n\n"
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
        total_error_percent = (abs((optimized_total - original_total) / original_total) * 100 if original_total != 0 else 0)
        result += f"\n--- Risultato Finale ---\nResistenza totale teorica: {format_value(original_total)}\nResistenza totale ottimizzata: {format_value(optimized_total)}\nErrore totale sull'equivalente: {total_error_percent:.2f}%\n"
        return result, None
    except Exception as e:
        return None, f"Errore nell'ottimizzazione: {str(e)}"

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
        result = f"--- Analisi Monte Carlo per Partitore di Tensione ---\n\nSpiegazione: La simulazione Monte Carlo testa il circuito migliaia di volte, \nvariando casualmente i valori dei resistori entro la loro tolleranza. \nQuesto aiuta a prevedere il comportamento reale del circuito.\n\nParametri di simulazione:\n- R1: {format_value(r1_nominal)} ±{tol1*100:.2f}%\n- R2: {format_value(r2_nominal)} ±{tol2*100:.2f}%\n- Vin: {vin} V\n- Iterazioni: {iterations}\n\n--- Risultati Statistici ---\nVout Teorico (calcolato con valori nominali): {vout_theoretical:.4f} V\nVout Medio (risultato della simulazione): {vout_mean:.4f} V\nDeviazione Standard (σ): {vout_std:.4f} V\nRange Vout: da {vout_min:.4f} V a {vout_max:.4f} V\n"
        return result, vout_values, vout_theoretical, None
    except Exception as e:
        return None, None, None, f"Errore nella simulazione: {str(e)}"
