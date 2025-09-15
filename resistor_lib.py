import math

# Valori commerciali standard
e_series = {
    "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
    "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1],
    "E48": [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
            1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
            3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
            5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53]
}

# Package e potenze
package_power = {
    "0201": 0.05,
    "0402": 0.0625,
    "0603": 0.1,
    "0805": 0.125,
    "1206": 0.25,
    "1210": 0.33,
    "1812": 0.5,
    "2010": 0.75,
    "2512": 1.0,
    "AXIAL": 0.25,
    "RADIAL": 0.25
}

# Colori per codice a colori (nome -> (digit, hex))
color_codes = {
    "nero": (0, "#000000"),
    "marrone": (1, "#8B4513"),
    "rosso": (2, "#FF0000"),
    "arancione": (3, "#FFA500"),
    "giallo": (4, "#FFFF00"),
    "verde": (5, "#008000"),
    "blu": (6, "#0000FF"),
    "viola": (7, "#800080"),
    "grigio": (8, "#808080"),
    "bianco": (9, "#FFFFFF"),
    "oro": (-1, "#FFD700"),
    "argento": (-2, "#C0C0C0")
}
tolerance_colors = {
    "marrone": (1, "#8B4513"),
    "rosso": (2, "#FF0000"),
    "verde": (0.5, "#008000"),
    "blu": (0.25, "#0000FF"),
    "viola": (0.1, "#800080"),
    "grigio": (0.05, "#808080"),
    "oro": (5, "#FFD700"),
    "argento": (10, "#C0C0C0")
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


def format_value(value):
    if value >= 1e6:
        return f"{value / 1e6:.3f} MΩ"
    elif value >= 1e3:
        return f"{value / 1e3:.3f} kΩ"
    elif value >= 1:
        return f"{value:.3f} Ω"
    elif value >= 1e-3:
        return f"{value * 1e3:.3f} mΩ"
    else:
        return f"{value * 1e6:.3f} µΩ"


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

                if error < 0.1:
                    break
        if best_error < 0.1:
            break

    return {'value': best_value, 'error': best_error}


def calculate_series_total(resistances, conn_type='serie'):
    if not resistances:
        return 0.0, ''

    if conn_type == 'serie':
        total = sum(resistances)
        calc_str = ' + '.join(str(r) for r in resistances)
    else:
        total = 1 / sum(1 / r for r in resistances)
        calc_str = '1 / (' + ' + '.join(f'1/{r}' for r in resistances) + ')'

    return total, calc_str


def calc_tolerance_range(total_resistance, tolerances):
    if not tolerances:
        return total_resistance, total_resistance, 0.0
    tol_mean = sum(tolerances) / len(tolerances)
    min_total = total_resistance * (1 - tol_mean / 100)
    max_total = total_resistance * (1 + tol_mean / 100)
    return min_total, max_total, tol_mean
