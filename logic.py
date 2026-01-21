
import random
import numpy as np
from resistor_lib import (
    e_series, get_color_from_digit, get_multiplier_color,
    eia96_value_codes, eia96_multiplier_codes,
    derating_start_temp_c, derating_percent_per_c,
    regulator_specs, awg_table, glossary_data
)
from utils import format_value

def parse_value_to_mantissa_exp(val):
    """Semplifica un valore Ohm in mantissa (2 cifre) ed esponente per codice colori."""
    if val <= 0: return 0, 0
    exp = int(np.floor(np.log10(val))) - 1
    mantissa = int(round(val / (10**exp)))
    if mantissa >= 100: # Gestione arrotondamento (es. 9.99 -> 10.0)
        mantissa //= 10
        exp += 1
    return mantissa, exp

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

def find_color_code_logic(value, e_series_data, custom_values=None):
    try:
        best_match = find_best_color_match(value, e_series_data, custom_values=custom_values)
        if best_match:
            source = "BOM Personalizzata" if custom_values else f"Serie {best_match['series_name']}"
            result = f"--- Ricerca Valore Commerciale ---\n\nValore richiesto: {format_value(value)}\nSorgente: {source}\n\nCodice colori suggerito per il valore più vicino:\n- Banda 1: {best_match['band1']}\n- Banda 2: {best_match['band2']}\n- Moltiplicatore: {best_match['multiplier']}\n- Tolleranza: {best_match['tolerance']} (±{best_match['tolerance_value']}%)\n\nValore trovato: {format_value(best_match['actual_value'])}\nErrore rispetto al valore richiesto: {best_match['error']:.2f}%\n\nSpiegazione:\nÈ stato cercato il valore più vicino tra quelli disponibili per minimizzare l'errore percentuale."
            return result, None
        else:
            return None, "Nessun valore trovato"
    except ValueError:
        return None, "Inserisci un valore numerico valido"

def find_best_color_match(target_value, e_series_data, custom_values=None):
    best_error = float("inf")
    best_match = None
    
    # Se abbiamo valori custom, cerchiamo in quelli
    if custom_values:
        for val in custom_values:
            error = abs((val - target_value) / target_value) * 100
            if error < best_error:
                best_error = error
                # Calcola bande per questo valore (approssimate a 2 cifre per semplicità visuale)
                # NOTA: Per valori non standard da BOM, il codice colori potrebbe essere 
                # un'approssimazione a 2 cifre + moltiplicatore
                val_mantissa, val_exp = parse_value_to_mantissa_exp(val)
                best_match = {
                    "series_name": "BOM",
                    "band1": get_color_from_digit(val_mantissa // 10),
                    "band2": get_color_from_digit(val_mantissa % 10),
                    "multiplier": get_multiplier_color(val_exp),
                    "tolerance": "marrone", # Tipico per resistori di precisione da BOM
                    "tolerance_value": 1,
                    "actual_value": val,
                    "error": error,
                }
        return best_match

    for series_name, series_values in e_series_data.items():
        for decade in range(-2, 8):
            for base_value in series_values:
                actual_value = base_value * (10**decade)
                error = abs((actual_value - target_value) / target_value) * 100
                if error < best_error:
                    best_error = error
                    # Assicuriamoci che base_value sia formattato per estrarre le cifre correttamente
                    # Per valori come 1.0, 2.2 ecc. vogliamo le prime due cifre significative
                    base_str = f"{base_value:g}".replace(".", "")
                    if len(base_str) == 1:
                        digit1 = int(base_str[0])
                        digit2 = 0
                    else:
                        digit1 = int(base_str[0])
                        digit2 = int(base_str[1])

                    best_match = {
                        "series_name": series_name,
                        "band1": get_color_from_digit(digit1),
                        "band2": get_color_from_digit(digit2),
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

def optimize_with_commercial_logic(resistances, conn_type, series, e_series_data, custom_values=None):
    try:
        if not resistances: return None, "Nessuna resistenza inserita"
        series_values = e_series_data.get(series, list(e_series_data.values())[0])
        source_name = "BOM" if custom_values else f"Serie {series}"
        result = f"--- Ottimizzazione con Valori Commerciali ({source_name}) ---\n\nOgni resistenza teorica viene sostituita con il valore più vicino disponibile.\n\n"
        optimized_resistances = []
        for i, target_r in enumerate(resistances):
            best_match = find_best_commercial_value(target_r, series_values, custom_values=custom_values)
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

def design_voltage_divider_logic(vin, vout_target, e_series_values=None, custom_values=None):
    """
    Trova le migliori coppie di resistori per un partitore di tensione.
    Supporta serie E o una lista personalizzata (BOM).
    """
    if vin <= 0 or vout_target <= 0 or vout_target >= vin:
        return None, "Vin deve essere > 0, Vout deve essere > 0 e Vin > Vout."

    target_ratio = vout_target / vin
    best_pairs = []

    # Genera i valori disponibili
    commercial_values = []
    if custom_values:
        commercial_values = custom_values
    elif e_series_values:
        for decade in range(-1, 7):  # da 0.1 a 10M ohm
            for base_val in e_series_values:
                commercial_values.append(base_val * (10**decade))

    # Itera su tutte le coppie possibili
    for r1 in commercial_values:
        for r2 in commercial_values:
            # Evita divisione per zero e coppie identiche se non necessario
            if r1 == 0 or r2 == 0:
                continue

            actual_ratio = r2 / (r1 + r2)
            error = abs((actual_ratio - target_ratio) / target_ratio) * 100

            # Salva le N migliori coppie
            if len(best_pairs) < 10 or error < best_pairs[-1]['error']:
                best_pairs.append({
                    'r1': r1,
                    'r2': r2,
                    'vout_actual': vin * actual_ratio,
                    'error': error
                })
                # Mantieni la lista ordinata per errore e limitata a 10 elementi
                best_pairs.sort(key=lambda x: x['error'])
                if len(best_pairs) > 10:
                    best_pairs.pop()

    # Formatta il risultato per la visualizzazione
    if not best_pairs:
        msg = "Nessuna combinazione trovata."
        if custom_values: msg += " La BOM caricata non ha abbastanza valori compatibili."
        else: msg += " Prova a cambiare la serie E."
        return None, msg

    source_name = "BOM Personalizzata" if custom_values else "Serie E"
    result = f"--- Progettazione Partitore di Tensione ---\n"
    result += f"Sorgente Valori: {source_name}\n\n"
    result += f"Obiettivo: Vin={vin}V, Vout={vout_target:.3f}V (Rapporto: {target_ratio:.4f})\n"
    result += "Migliori 10 coppie di resistori trovate:\n\n"
    result += "{:<15} {:<15} {:<15} {:<10}\n".format("R1", "R2", "Vout Reale", "Errore")
    result += "-"*55 + "\n"

    for pair in best_pairs:
        result += "{:<15} {:<15} {:<15.3f} {:<10.2f}%\n".format(
            format_value(pair['r1']),
            format_value(pair['r2']),
            pair['vout_actual'],
            pair['error']
        )

    result += "\nSpiegazione: Sono state testate tutte le combinazioni di resistori della serie E scelta per trovare quelle che minimizzano l'errore sul rapporto Vout/Vin."

    return result, None

def find_best_commercial_value(target_value, series_values=None, custom_values=None):
    """
    Trova il miglior valore commerciale. 
    Se custom_values è fornito (es. da una BOM), cerca solo in quelli.
    Altrimenti usa series_values (valori base) e calcola le decadi.
    """
    best_match = {'value': -1, 'error': float('inf')}
    
    if custom_values:
        for value in custom_values:
            error = abs((value - target_value) / target_value) * 100
            if error < best_match['error']:
                best_match['value'] = value
                best_match['error'] = error
        return best_match

    # Comportamento standard con serie E
    if series_values:
        for decade in range(-2, 8):  # da 0.01 a 100M
            for base in series_values:
                value = base * (10**decade)
                error = abs((value - target_value) / target_value) * 100
                if error < best_match['error']:
                    best_match['value'] = value
                    best_match['error'] = error
    
    return best_match

def calculate_led_resistor_logic(v_supply, v_led, i_led, e_series_values=None, package_power=None, custom_values=None):
    """
    Calcola il resistore per un LED, suggerisce un valore commerciale e un package.
    """
    if v_supply <= v_led:
        return None, "La tensione di alimentazione (Vsupply) deve essere maggiore della tensione del LED (Vf)."
    if i_led <= 0:
        return None, "La corrente del LED (If) deve essere maggiore di zero."

    # 1. Calcolo del resistore ideale
    r_ideal = (v_supply - v_led) / (i_led / 1000.0)  # i_led è in mA

    # 2. Trova il valore commerciale più vicino
    best_match = find_best_commercial_value(r_ideal, series_values=e_series_values, custom_values=custom_values)
    r_commercial = best_match['value']

    # 3. Calcolo della potenza dissipata con il valore commerciale
    i_actual = (v_supply - v_led) / r_commercial
    power_dissipated = (v_supply - v_led) * i_actual

    # 4. Raccomandazione del package
    recommended_package = "Nessuno (potenza troppo elevata)"
    safety_factor = 2.0  # Fattore di sicurezza minimo del 200%

    # Ordina i package per potenza crescente
    sorted_packages = sorted(package_power.items(), key=lambda item: item[1])

    for pkg_name, pkg_power in sorted_packages:
        if pkg_power >= (power_dissipated * safety_factor):
            recommended_package = f"{pkg_name} ({pkg_power}W)"
            break

    # Formattazione del risultato
    source_name = "BOM Personalizzata" if custom_values else "Serie E"
    result = f"--- Calcolo Resistore per LED ---\n"
    result += f"Sorgente Valori: {source_name}\n\n"
    result += f"Parametri di Input:\n"
    result += f"- Tensione di Alimentazione: {v_supply} V\n"
    result += f"- Tensione di Caduta LED (Vf): {v_led} V\n"
    result += f"- Corrente LED (If): {i_led} mA\n\n"

    result += f"--- Risultati ---\n"
    result += f"1. Valore Resistore Ideale: {format_value(r_ideal)}\n"
    result += f"2. Valore Commerciale più Vicino: {format_value(r_commercial)} (Errore: {best_match['error']:.2f}%)\n"
    result += f"   - Corrente Reale con questo resistore: {i_actual*1000:.2f} mA\n"
    result += f"3. Potenza Dissipata dal Resistore: {power_dissipated:.4f} W\n"
    result += f"4. Package Raccomandato (con fattore di sicurezza >{safety_factor:.0f}x): {recommended_package}\n\n"

    result += "Spiegazione:\n"
    result += "Il resistore limita la corrente che scorre nel LED. Il valore commerciale è stato scelto dalla serie E selezionata. La potenza dissipata determina la dimensione fisica (package) del resistore necessaria per operare in sicurezza."

    return result, None

def design_rc_filter_logic(f_c_target, r_series_values=None, c_series_values=None, custom_values=None):
    """
    Trova le migliori coppie R/C per un filtro passa-basso.
    """
    if f_c_target <= 0:
        return None, "La frequenza di taglio deve essere maggiore di zero."

    best_pairs = []

    # Genera i valori disponibili per i resistori
    commercial_resistors = []
    if custom_values:
        commercial_resistors = custom_values
    elif r_series_values:
        for decade in range(0, 7):  # 1 ohm a 10M ohm
            for base_val in r_series_values:
                commercial_resistors.append(base_val * (10**decade))
    else:
        return None, "Nessun valore resistivo fornito."

    # Genera un range di valori commerciali per i condensatori
    commercial_capacitors = []
    for decade in range(-12, -4):  # 1pF a 1uF
        for base_val in c_series_values:
            commercial_capacitors.append(base_val * (10**decade))

    # Itera sui resistori e trova il miglior condensatore per ciascuno
    for r in commercial_resistors:
        # Calcola il condensatore ideale per questo resistore
        c_ideal = 1 / (2 * np.pi * r * f_c_target)

        # Trova il condensatore commerciale più vicino
        best_c = min(commercial_capacitors, key=lambda c: abs(c - c_ideal))

        # Calcola la frequenza reale e l'errore
        f_c_actual = 1 / (2 * np.pi * r * best_c)
        error = abs((f_c_actual - f_c_target) / f_c_target) * 100

        # Salva le N migliori coppie
        if len(best_pairs) < 15 or error < best_pairs[-1]['error']:
            best_pairs.append({
                'r': r,
                'c': best_c,
                'f_c_actual': f_c_actual,
                'error': error
            })
            best_pairs.sort(key=lambda x: x['error'])
            if len(best_pairs) > 15:
                best_pairs.pop()

    if not best_pairs:
        return None, "Nessuna combinazione R/C trovata."

    source_name = "BOM Personalizzata" if custom_values else "Serie E"
    result = f"--- Progettazione Filtro RC Passa-Basso ---\n"
    result += f"Sorgente Resistori: {source_name}\n\n"
    result += f"Obiettivo Frequenza di Taglio (fc): {format_value(f_c_target, unit='Hz')}\n"
    result += "Migliori 15 combinazioni R/C trovate:\n\n"
    result += "{:<15} {:<15} {:<20} {:<10}\n".format("Resistore", "Condensatore", "fc Reale", "Errore")
    result += "-"*65 + "\n"

    for pair in best_pairs:
        result += "{:<15} {:<15} {:<20} {:<10.2f}%\n".format(
            format_value(pair['r']),
            format_value(pair['c'], unit='F'),
            format_value(pair['f_c_actual'], unit='Hz'),
            pair['error']
        )

    result += "\nSpiegazione: Per ogni resistore della serie E, è stato trovato il condensatore (anch'esso da una serie E) che minimizza l'errore sulla frequenza di taglio."
    return result, None

def calculate_regulator_logic(vin, vout_target, regulator_name, e_series_values=None, custom_values=None):
    """
    Calcola le coppie R1/R2 per un regolatore lineare (es. LM317).
    """
    if regulator_name not in regulator_specs:
        return None, "Regolatore non supportato."
    
    spec = regulator_specs[regulator_name]
    vref = spec['vref']
    iadj = spec['iadj_ua'] / 1e6
    r1_val = spec['r1_recommended']

    if abs(vout_target) < abs(vref):
        return None, f"La tensione target ({vout_target}V) deve essere maggiore della Vref ({vref}V)."

    best_pairs = []
    
    # Testiamo diversi valori di R1 intorno a quello consigliato
    for r1 in [r1_val, 120, 240, 330, 470]:
        # Formule basate su segno di Vref (regolatori positivi o negativi)
        # Vout = Vref * (1 + R2/R1) + Iadj * R2
        # Resolvendo per R2: R2 = (Vout - Vref) / (Vref/R1 + Iadj)
        try:
            target_r2 = (abs(vout_target) - abs(vref)) / (abs(vref)/r1 + iadj)
            if target_r2 < 0: continue
            
            best_r2_match = find_best_commercial_value(target_r2, e_series_values)
            r2_commercial = best_r2_match['value']
            
            vout_actual = vref * (1 + r2_commercial/r1) + (iadj * r2_commercial if vref > 0 else -iadj * r2_commercial)
            error = abs((vout_actual - vout_target) / vout_target) * 100
            
            best_pairs.append({
                'r1': r1,
                'r2': r2_commercial,
                'vout': vout_actual,
                'error': error
            })
        except ZeroDivisionError:
            continue

    best_pairs.sort(key=lambda x: x['error'])
    
    result = f"--- Progettazione Regolatore {regulator_name} ---\n\n"
    result += f"Obiettivo: Vout = {vout_target}V (Vref = {vref}V)\n\n"
    result += "{:<10} {:<10} {:<15} {:<10}\n".format("R1", "R2", "Vout Reale", "Errore")
    result += "-"*50 + "\n"
    for p in best_pairs[:5]:
        result += "{:<10} {:<10} {:<15.3f} {:<10.2f}%\n".format(
            format_value(p['r1']), format_value(p['r2']), p['vout'], p['error']
        )
    
    return result, None

def calculate_current_divider_logic(i_total, resistances):
    """
    Calcola la corrente in ogni ramo di un ripartitore di corrente.
    """
    if not resistances:
        return None, "Inserisci almeno una resistenza."
    
    try:
        g_total = sum(1/r for r in resistances)
        v_equiv = i_total / g_total
        
        result = "--- Analisi Ripartitore di Corrente ---\n\n"
        result += f"Corrente Totale: {i_total} A\n\n"
        result += "{:<10} {:<15} {:<15}\n".format("Ramo", "Resistenza", "Corrente")
        result += "-"*40 + "\n"
        
        for i, r in enumerate(resistances):
            i_branch = v_equiv / r
            result += "R{:<9} {:<15} {:<15.4f} A\n".format(i+1, format_value(r), i_branch)
            
        return result, None
    except ZeroDivisionError:
        return None, "La resistenza non può essere zero."

def convert_awg_logic(awg_val):
    if awg_val in awg_table:
        data = awg_table[awg_val]
        result = f"--- Dati Cavo AWG {awg_val} ---\n\n"
        result += f"- Diametro: {data['diameter_mm']} mm\n"
        result += f"- Sezione: {data['area_mm2']} mm²\n"
        result += f"- Resistenza: {data['res_ohm_km']} Ω/km\n"
        result += f"- Corrente Max (indicativa): {data['max_amp']} A\n"
        return result, None
    else:
        return None, "Valore AWG non in tabella (supportati 10-30)."

def search_glossary_logic(query):
    query = query.lower()
    results = []
    for term, definition in glossary_data.items():
        if query in term.lower() or query in definition.lower():
            results.append(f"**{term}**: {definition}")
    if not results: return "Nessun risultato trovato nel glossario."
    return "\n\n".join(results)
