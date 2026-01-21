
import math

# Valori commerciali standard (IEC 60063)
e_series = {
    "E3": [1.0, 2.2, 4.7],
    "E6": [1.0, 1.5, 2.2, 3.3, 4.7, 6.8],
    "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
    "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1],
    "E48": [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
            1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
            3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
            5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53],
    "E96": [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
            1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
            1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
            2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
            3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
            4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
            5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
            7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76],
    "E192": [1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11, 1.13, 1.14, 1.15, 1.17, 1.18, 1.20, 1.21, 1.23, 1.24, 1.26, 1.27, 1.29, 1.30, 1.32, 1.33, 1.35, 1.37, 1.38, 1.40, 1.42, 1.43, 1.45, 1.47, 1.49, 1.50, 1.52, 1.54, 1.56, 1.58, 1.60, 1.62, 1.64, 1.65, 1.67, 1.69, 1.72, 1.74, 1.76, 1.78, 1.80, 1.82, 1.84, 1.87, 1.89, 1.91, 1.93, 1.96, 1.98, 2.00, 2.03, 2.05, 2.08, 2.10, 2.13, 2.15, 2.18, 2.21, 2.23, 2.26, 2.29, 2.32, 2.34, 2.37, 2.40, 2.43, 2.46, 2.49, 2.52, 2.55, 2.58, 2.61, 2.64, 2.67, 2.71, 2.74, 2.77, 2.80, 2.84, 2.87, 2.91, 2.94, 2.98, 3.01, 3.05, 3.09, 3.12, 3.16, 3.20, 3.24, 3.28, 3.32, 3.36, 3.40, 3.44, 3.48, 3.52, 3.57, 3.61, 3.65, 3.70, 3.74, 3.79, 3.83, 3.88, 3.92, 3.97, 4.02, 4.07, 4.12, 4.17, 4.22, 4.27, 4.32, 4.37, 4.42, 4.48, 4.53, 4.59, 4.64, 4.70, 4.75, 4.81, 4.87, 4.93, 4.99, 5.05, 5.11, 5.17, 5.23, 5.30, 5.36, 5.42, 5.49, 5.56, 5.62, 5.69, 5.76, 5.83, 5.90, 5.97, 6.04, 6.12, 6.19, 6.26, 6.34, 6.42, 6.49, 6.57, 6.65, 6.73, 6.81, 6.90, 6.98, 7.06, 7.15, 7.23, 7.32, 7.41, 7.50, 7.59, 7.68, 7.77, 7.87, 7.96, 8.06, 8.16, 8.25, 8.35, 8.45, 8.56, 8.66, 8.76, 8.87, 8.98, 9.09, 9.20, 9.31, 9.42, 9.53, 9.65, 9.76, 9.88]
}

# Package e potenze (valori tipici, consultare datasheet per derating)
# Aggiunta resistenza termica indicativa (Rthja in °C/W) per analisi avanzata
package_data = {
    "0201": {"power": 0.05, "rthja": 1000}, 
    "0402": {"power": 0.0625, "rthja": 800}, 
    "0603": {"power": 0.1, "rthja": 600}, 
    "0805": {"power": 0.125, "rthja": 400},
    "1206": {"power": 0.25, "rthja": 300}, 
    "1210": {"power": 0.33, "rthja": 250}, 
    "1812": {"power": 0.5, "rthja": 200}, 
    "2010": {"power": 0.75, "rthja": 150}, 
    "2512": {"power": 1.0, "rthja": 100},
    "AXIAL-0.25": {"power": 0.25, "rthja": 150}, 
    "AXIAL-0.5": {"power": 0.5, "rthja": 100}
}
# Mantengo package_power per compatibilità retroattiva
package_power = {k: v["power"] for k, v in package_data.items()}

# Parametri per il derating termico (valori tipici, da datasheet)
derating_start_temp_c = 70  # Temperatura (in °C) a cui inizia il derating
derating_percent_per_c = 0.8 # Percentuale di potenza persa per ogni °C sopra la start_temp

# Codice colori (IEC 60062)
color_codes = {
    "nero": (0, "#000000"), "marrone": (1, "#8B4513"), "rosso": (2, "#FF0000"),
    "arancione": (3, "#FFA500"), "giallo": (4, "#FFFF00"), "verde": (5, "#008000"),
    "blu": (6, "#0000FF"), "viola": (7, "#800080"), "grigio": (8, "#808080"),
    "bianco": (9, "#FFFFFF"), "oro": (-1, "#FFD700"), "argento": (-2, "#C0C0C0")
}

# Tolleranze (IEC 60062)
tolerance_colors = {
    "marrone": (1, "#8B4513"), "rosso": (2, "#FF0000"), "verde": (0.5, "#008000"),
    "blu": (0.25, "#0000FF"), "viola": (0.1, "#800080"), "grigio": (0.05, "#808080"),
    "oro": (5, "#FFD700"), "argento": (10, "#C0C0C0"), "nessuno": (20, "#D3D3D3")
}

# Standard EIA-96 per resistori SMD (1% tolleranza)
eia96_value_codes = {
    '01': 100, '02': 102, '03': 105, '04': 107, '05': 110, '06': 113, '07': 115, '08': 118,
    '09': 121, '10': 124, '11': 127, '12': 130, '13': 133, '14': 137, '15': 140, '16': 143,
    '17': 147, '18': 150, '19': 154, '20': 158, '21': 162, '22': 165, '23': 169, '24': 174,
    '25': 178, '26': 182, '27': 187, '28': 191, '29': 196, '30': 200, '31': 205, '32': 210,
    '33': 215, '34': 221, '35': 226, '36': 232, '37': 237, '38': 243, '39': 249, '40': 255,
    '41': 261, '42': 267, '43': 274, '44': 280, '45': 287, '46': 294, '47': 301, '48': 309,
    '49': 316, '50': 324, '51': 332, '52': 340, '53': 348, '54': 357, '55': 365, '56': 374,
    '57': 383, '58': 392, '59': 402, '60': 412, '61': 422, '62': 432, '63': 442, '64': 453,
    '65': 464, '66': 475, '67': 487, '68': 499, '69': 511, '70': 523, '71': 536, '72': 549,
    '73': 562, '74': 576, '75': 590, '76': 604, '77': 619, '78': 634, '79': 649, '80': 665,
    '81': 681, '82': 698, '83': 715, '84': 732, '85': 750, '86': 768, '87': 787, '88': 806,
    '89': 825, '90': 845, '91': 866, '92': 887, '93': 909, '94': 931, '95': 953, '96': 976
}

eia96_multiplier_codes = {
    'Z': 0.001, 'Y': 0.01, 'X': 0.1, 'A': 1, 'B': 10, 'C': 100, 'D': 1000, 'E': 10000, 'F': 100000
}

def get_color_from_digit(digit):
    colors = ["nero", "marrone", "rosso", "arancione", "giallo",
              "verde", "blu", "viola", "grigio", "bianco"]
    return colors[digit] if 0 <= digit <= 9 else "nero"

def get_multiplier_color(exponent):
    if exponent == -2:
        return "argento"
    elif exponent == -1:
        return "oro"
    elif 0 <= exponent <= 9:
        return get_color_from_digit(exponent)
    else:
        return "nero"

# Specifiche Regolatori Lineari
regulator_specs = {
    "LM317": {"vref": 1.25, "iadj_ua": 50, "r1_recommended": 240},
    "LM337": {"vref": -1.25, "iadj_ua": 50, "r1_recommended": 240},
    "LM350": {"vref": 1.25, "iadj_ua": 50, "r1_recommended": 120},
    "AMS1117-ADJ": {"vref": 1.25, "iadj_ua": 60, "r1_recommended": 120}
}

# Tabella AWG (American Wire Gauge)
awg_table = {
    10: {"diameter_mm": 2.588, "area_mm2": 5.26, "res_ohm_km": 3.27, "max_amp": 30},
    12: {"diameter_mm": 2.053, "area_mm2": 3.31, "res_ohm_km": 5.21, "max_amp": 20},
    14: {"diameter_mm": 1.628, "area_mm2": 2.08, "res_ohm_km": 8.28, "max_amp": 15},
    16: {"diameter_mm": 1.291, "area_mm2": 1.31, "res_ohm_km": 13.17, "max_amp": 10},
    18: {"diameter_mm": 1.024, "area_mm2": 0.823, "res_ohm_km": 20.95, "max_amp": 7},
    20: {"diameter_mm": 0.812, "area_mm2": 0.518, "res_ohm_km": 33.31, "max_amp": 5},
    22: {"diameter_mm": 0.644, "area_mm2": 0.326, "res_ohm_km": 52.96, "max_amp": 3},
    24: {"diameter_mm": 0.511, "area_mm2": 0.205, "res_ohm_km": 84.22, "max_amp": 2},
    26: {"diameter_mm": 0.405, "area_mm2": 0.129, "res_ohm_km": 133.9, "max_amp": 1},
    28: {"diameter_mm": 0.321, "area_mm2": 0.081, "res_ohm_km": 212.9, "max_amp": 0.5},
    30: {"diameter_mm": 0.255, "area_mm2": 0.050, "res_ohm_km": 338.6, "max_amp": 0.3}
}

# Glossario Tecnico
glossary_data = {
    "AEC-Q200": "Standard di qualificazione per componenti passivi in ambito automotive.",
    "Derating": "Riduzione della potenza operativa di un componente per aumentarne l'affidabilità in condizioni di stress.",
    "E-Series": "Serie di valori preferiti per componenti elettronici definita dallo standard IEC 60063.",
    "IEC 60062": "Standard internazionale per i codici di marcatura di resistori e condensatori.",
    "PPM/°C": "Parti per milione per grado Celsius. Indica il coefficiente di temperatura.",
    "Tolleranza": "Variazione massima consentita del valore reale rispetto al nominale.",
    "Vref": "Tensione di riferimento interna di un regolatore.",
    "Rthja": "Resistenza termica tra giunzione e ambiente.",
    "SMD": "Surface Mount Device. Componenti a montaggio superficiale.",
    "Through-hole": "Componenti con reofori passanti."
}

