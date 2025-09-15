import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import math
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import sys
import traceback
from tkinter.scrolledtext import ScrolledText


class ElectronicTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Electronic Tool — Analisi e Didattica sulle Resistenze")
        self.root.geometry("1100x820")
        self.set_style()

        # Valori commerciali standard
        self.e_series = {
            "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
            "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
                    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1],
            "E48": [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
                    1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
                    3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
                    5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53]
        }

        # Package e potenze
        self.package_power = {
            "0201": 0.05,  # 1/20 W
            "0402": 0.0625,  # 1/16 W
            "0603": 0.1,  # 1/10 W
            "0805": 0.125,  # 1/8 W
            "1206": 0.25,  # 1/4 W
            "1210": 0.33,  # 1/3 W
            "1812": 0.5,  # 1/2 W
            "2010": 0.75,  # 3/4 W
            "2512": 1.0,  # 1 W
            "AXIAL": 0.25,  # 1/4 W
            "RADIAL": 0.25  # 1/4 W
        }

        # Colori per codice a colori
        self.color_codes = {
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

        self.tolerance_colors = {
            "marrone": (1, "#8B4513"),
            "rosso": (2, "#FF0000"),
            "verde": (0.5, "#008000"),
            "blu": (0.25, "#0000FF"),
            "viola": (0.1, "#800080"),
            "grigio": (0.05, "#808080"),
            "oro": (5, "#FFD700"),
            "argento": (10, "#C0C0C0")
        }

        self.create_widgets()

    def set_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TFrame', background='#F5F7FA')
        style.configure('TLabel', background='#F5F7FA')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Accent.TButton', foreground='#FFFFFF', background='#2E5AAC')
        self.root.configure(background='#F5F7FA')

    def create_widgets(self):
        # Menu principale
        self.create_menu()

        # Header informativo
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=12, pady=(8, 0))
        ttk.Label(header, text='Electronic Tool — Resistenza e Circuiti', style='Header.TLabel').pack(side=tk.LEFT)

        # Notebook per le diverse funzionalità
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Codice colori
        self.color_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.color_frame, text="Codice Colori")
        self.create_color_tab()

        # Tab 2: Serie/Parallelo
        self.series_parallel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.series_parallel_frame, text="Serie/Parallelo")
        self.create_series_parallel_tab()

        # Tab 3: Monte Carlo
        self.monte_carlo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monte_carlo_frame, text="Monte Carlo")
        self.create_monte_carlo_tab()

        # Tab 4: Potenza
        self.power_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.power_frame, text="Potenza")
        self.create_power_tab()

    def create_color_tab(self):
        # Frame per input
        input_frame = ttk.LabelFrame(self.color_frame, text="Inserisci Codice Colori — istruzioni: scegli le bande e premi 'Calcola Valore'")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Bande di colore
        bands_frame = ttk.Frame(input_frame)
        bands_frame.pack(fill=tk.X, padx=5, pady=5)

        # Selettore numero bande (4 o 5)
        ttk.Label(bands_frame, text="Numero bande:").grid(row=0, column=4, padx=5, pady=5)
        self.num_bands = tk.IntVar(value=4)
        ttk.Radiobutton(bands_frame, text="4", variable=self.num_bands, value=4, command=self.update_band_visibility).grid(row=0, column=5)
        ttk.Radiobutton(bands_frame, text="5", variable=self.num_bands, value=5, command=self.update_band_visibility).grid(row=0, column=6)

        ttk.Label(bands_frame, text="Banda 1:").grid(row=0, column=0, padx=5, pady=5)
        self.band1_var = tk.StringVar()
        self.band1_combo = ttk.Combobox(bands_frame, textvariable=self.band1_var,
                                        values=list(self.color_codes.keys())[:-2], width=12)
        self.band1_combo.grid(row=0, column=1, padx=5, pady=5)
        self.band1_combo.set("marrone")

        ttk.Label(bands_frame, text="Banda 2:").grid(row=0, column=2, padx=5, pady=5)
        self.band2_var = tk.StringVar()
        self.band2_combo = ttk.Combobox(bands_frame, textvariable=self.band2_var,
                                        values=list(self.color_codes.keys()), width=12)
        self.band2_combo.grid(row=0, column=3, padx=5, pady=5)
        self.band2_combo.set("nero")

        ttk.Label(bands_frame, text="Banda 3 (Moltiplicatore):").grid(row=1, column=0, padx=5, pady=5)
        self.multiplier_var = tk.StringVar()
        self.multiplier_combo = ttk.Combobox(bands_frame, textvariable=self.multiplier_var,
                                             values=list(self.color_codes.keys()), width=12)
        self.multiplier_combo.grid(row=1, column=1, padx=5, pady=5)
        self.multiplier_combo.set("rosso")

        ttk.Label(bands_frame, text="Tolleranza:").grid(row=1, column=2, padx=5, pady=5)
        self.tolerance_var = tk.StringVar()
        self.tolerance_combo = ttk.Combobox(bands_frame, textvariable=self.tolerance_var,
                                            values=list(self.tolerance_colors.keys()), width=12)
        self.tolerance_combo.grid(row=1, column=3, padx=5, pady=5)
        self.tolerance_combo.set("oro")

        # Pulsante calcola
        calc_btn = ttk.Button(input_frame, text="Calcola Valore", command=self.calculate_color_code)
        calc_btn.pack(pady=10)

        # Disegno resistenza con bande
        draw_frame = ttk.Frame(self.color_frame)
        draw_frame.pack(fill=tk.X, padx=10, pady=5)
        self.res_canvas = tk.Canvas(draw_frame, width=440, height=80, bg='#FFFFFF', highlightthickness=1, highlightbackground='#CCCCCC')
        self.res_canvas.pack(side=tk.LEFT, padx=5)
        self.update_resistor_drawing()

        # Frame per risultato
        result_frame = ttk.LabelFrame(self.color_frame, text="Risultato")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.color_result_text = ScrolledText(result_frame, height=8, width=60)
        self.color_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame per input valore numerico
        value_frame = ttk.LabelFrame(self.color_frame, text="Trova Codice Colori — inserisci valore e trova il codice commerciale più vicino")
        value_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(value_frame, text="Valore (Ω):").grid(row=0, column=0, padx=5, pady=5)
        self.value_entry = ttk.Entry(value_frame, width=15)
        self.value_entry.grid(row=0, column=1, padx=5, pady=5)
        self.value_entry.insert(0, "1000")

        find_btn = ttk.Button(value_frame, text="Trova Codice", command=self.find_color_code)
        find_btn.grid(row=0, column=2, padx=10, pady=5)

    def calculate_color_code(self):
        try:
            # Ottieni i valori dalle bande
            band1_val = self.color_codes[self.band1_var.get()][0]
            band2_val = self.color_codes[self.band2_var.get()][0]
            multiplier_val = self.color_codes[self.multiplier_var.get()][0]
            tolerance_val = self.tolerance_colors[self.tolerance_var.get()][0]

            # Calcola il valore
            value = (band1_val * 10 + band2_val) * (10 ** multiplier_val)
            min_value = value * (1 - tolerance_val / 100)
            max_value = value * (1 + tolerance_val / 100)

            # Formatta il valore
            formatted_value = self.format_value(value)

            result = f"Valore resistenza: {formatted_value}\n"
            result += f"Tolleranza: ±{tolerance_val}%\n"
            result += f"Range: {self.format_value(min_value)} - {self.format_value(max_value)}\n"
            result += f"Valore esatto: {value:.2f} Ω"

            self.color_result_text.delete(1.0, tk.END)
            self.color_result_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo: {str(e)}")
        finally:        
            self.update_resistor_drawing()
            try:
                self.update_resistor_drawing()
            except Exception:
                pass

    

    def update_band_visibility(self):
        # Aggiorna il disegno quando cambia il numero di bande
        self.update_resistor_drawing()

    def update_resistor_drawing(self):
        # Disegna una resistenza stilizzata con bande colorate
        try:
            self.res_canvas.delete('all')
        except Exception:
            return

        w = 440; h = 80
        # Corpo
        self.res_canvas.create_rectangle(40, 20, 400, 60, fill='#F0F0F0', outline='#333333')
        # Terminali
        self.res_canvas.create_line(0, 40, 40, 40, width=3, fill='#333333')
        self.res_canvas.create_line(400, 40, w, 40, width=3, fill='#333333')

        # Determina colori dalle scelte
        band_colors = []
        try:
            band_colors.append(self.color_codes[self.band1_var.get()][1])
            band_colors.append(self.color_codes[self.band2_var.get()][1])
            band_colors.append(self.color_codes[self.multiplier_var.get()][1])
            band_colors.append(self.tolerance_colors[self.tolerance_var.get()][1])
        except Exception:
            band_colors = ['#000000'] * 4

        n = self.num_bands.get()
        # Se 5 bande, inserisci una banda centrale addizionale (usiamo banda2 come placeholder)
        if n == 5:
            band_positions = [80, 140, 200, 260, 320]
            # ricostruisci colori se esiste banda3
            try:
                mid_color = self.color_codes.get(self.band2_var.get(), ('', '#000000'))[1]
                band_colors = [self.color_codes[self.band1_var.get()][1], mid_color, self.color_codes[self.band2_var.get()][1], self.color_codes[self.multiplier_var.get()][1], self.tolerance_colors[self.tolerance_var.get()][1]]
            except Exception:
                band_colors = ['#000000'] * 5
        else:
            band_positions = [110, 170, 230, 290]

        for i, pos in enumerate(band_positions[:len(band_colors)]):
            color = band_colors[i]
            self.res_canvas.create_rectangle(pos-8, 22, pos+8, 58, fill=color, outline='')

    def find_color_code(self):
        try:
            value = float(self.value_entry.get())

            # Trova il codice colore più vicino
            best_match = self.find_best_color_match(value)

            if best_match:
                result = f"Valore richiesto: {self.format_value(value)}\n\n"
                result += "Codice colori suggerito:\n"
                result += f"Banda 1: {best_match['band1']}\n"
                result += f"Banda 2: {best_match['band2']}\n"
                result += f"Moltiplicatore: {best_match['multiplier']}\n"
                result += f"Tolleranza: {best_match['tolerance']} (±{best_match['tolerance_value']}%)\n"
                result += f"Valore ottenuto: {self.format_value(best_match['actual_value'])}\n"
                result += f"Errore: {best_match['error']:.2f}%"

                self.color_result_text.delete(1.0, tk.END)
                self.color_result_text.insert(1.0, result)
            else:
                messagebox.showwarning("Attenzione", "Nessun valore commerciale trovato")

        except ValueError:
            messagebox.showerror("Errore", "Inserisci un valore numerico valido")

    def find_best_color_match(self, target_value):
        best_error = float('inf')
        best_match = None

        # Prova diverse combinazioni
        for series_name, series_values in self.e_series.items():
            for decade in range(-2, 6):  # Decadi da 0.01 a 1M
                for base_value in series_values:
                    actual_value = base_value * (10 ** decade)
                    error = abs((actual_value - target_value) / target_value) * 100

                    if error < best_error:
                        best_error = error
                        best_match = {
                            'band1': self.get_color_from_digit(int(str(base_value)[0])),
                            'band2': self.get_color_from_digit(int(str(base_value)[1])) if len(
                                str(base_value)) > 1 else "nero",
                            'multiplier': self.get_multiplier_color(decade),
                            'tolerance': "oro",  # ±5%
                            'tolerance_value': 5,
                            'actual_value': actual_value,
                            'error': error
                        }

                        if error < 1:  # Se l'errore è < 1%, accetta
                            return best_match

        return best_match

    def get_color_from_digit(self, digit):
        colors = ["nero", "marrone", "rosso", "arancione", "giallo",
                  "verde", "blu", "viola", "grigio", "bianco"]
        return colors[digit] if 0 <= digit <= 9 else "nero"

    def get_multiplier_color(self, exponent):
        if exponent == -2:
            return "argento"
        elif exponent == -1:
            return "oro"
        elif 0 <= exponent <= 9:
            return self.get_color_from_digit(exponent)
        else:
            return "nero"

    def create_series_parallel_tab(self):
        # Frame per input
        input_frame = ttk.LabelFrame(self.series_parallel_frame, text="Inserisci Resistenze — valori con tolleranza per singolo componente")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Tipo di connessione
        conn_frame = ttk.Frame(input_frame)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(conn_frame, text="Tipo connessione:").pack(side=tk.LEFT, padx=5)
        self.conn_type = tk.StringVar(value="serie")
        ttk.Radiobutton(conn_frame, text="Serie", variable=self.conn_type, value="serie").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(conn_frame, text="Parallelo", variable=self.conn_type, value="parallelo").pack(side=tk.LEFT)

        # Lista dinamica di resistenze (valore + tolleranza)
        list_frame = ttk.Frame(input_frame)
        list_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(list_frame, text="Riferimento: Valore (Ω)    Tolleranza (%)").grid(row=0, column=0, columnspan=3, sticky=tk.W)
        self.res_rows = []

        def add_res_row(value='1000', tol='5'):
            row = {}
            r = len(self.res_rows) + 1
            row['val'] = ttk.Entry(list_frame, width=20)
            row['val'].grid(row=r, column=0, padx=5, pady=2)
            row['val'].insert(0, str(value))
            row['tol'] = ttk.Entry(list_frame, width=10)
            row['tol'].grid(row=r, column=1, padx=5, pady=2)
            row['tol'].insert(0, str(tol))
            btn = ttk.Button(list_frame, text='Rimuovi', command=lambda rw=row: remove_res_row(rw))
            btn.grid(row=r, column=2, padx=5, pady=2)
            row['btn'] = btn
            self.res_rows.append(row)

        def remove_res_row(row):
            try:
                row['val'].destroy(); row['tol'].destroy(); row['btn'].destroy()
                self.res_rows.remove(row)
                # ricompatta le righe
                for idx, rw in enumerate(self.res_rows, start=1):
                    rw['val'].grid(row=idx, column=0)
                    rw['tol'].grid(row=idx, column=1)
                    rw['btn'].grid(row=idx, column=2)
            except Exception:
                pass

        # Inizializza con due resistenze
        add_res_row('1000', '5')
        add_res_row('2000', '5')

        add_btn = ttk.Button(list_frame, text='Aggiungi Resistenza', command=lambda: add_res_row('1000', '5'))
        add_btn.grid(row=99, column=0, pady=6, sticky=tk.W)

        # Serie commerciali
        series_frame = ttk.Frame(input_frame)
        series_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(series_frame, text="Serie commerciale:").pack(side=tk.LEFT, padx=5)
        self.series_var = tk.StringVar(value="E12")
        self.series_combo = ttk.Combobox(series_frame, textvariable=self.series_var,
                         values=list(self.e_series.keys()), width=10)
        self.series_combo.pack(side=tk.LEFT, padx=5, pady=5)

        # Pulsanti
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)

        calc_btn = ttk.Button(btn_frame, text="Calcola", command=self.calculate_series_parallel)
        calc_btn.pack(side=tk.LEFT, padx=5)

        optimize_btn = ttk.Button(btn_frame, text="Ottimizza con Valori Commerciali",
                                  command=self.optimize_with_commercial)
        optimize_btn.pack(side=tk.LEFT, padx=5)

        # Frame per risultato
        result_frame = ttk.LabelFrame(self.series_parallel_frame, text="Risultato")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.series_result_text = ScrolledText(result_frame, height=12, width=60)
        self.series_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame per grafico
        self.series_graph_frame = ttk.Frame(self.series_parallel_frame)
        self.series_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def calculate_series_parallel(self):
        try:
            # Leggi resistenze e tolleranze dalle righe
            resistances = []
            tolerances = []
            for rw in self.res_rows:
                try:
                    resistances.append(float(rw['val'].get()))
                    tolerances.append(float(rw['tol'].get()))
                except Exception:
                    pass

            if self.conn_type.get() == "serie":
                total_resistance = sum(resistances)
                calculation = " + ".join([self.format_value(r) for r in resistances])
            else:  # parallelo
                total_resistance = 1 / sum(1 / r for r in resistances)
                calculation = "1 / (" + " + ".join([f"1/{self.format_value(r)}" for r in resistances]) + ")"

            # Calcola tolleranza
            # Calcola tolleranza totale approssimata (non-lineare per parallelo)
            # Per semplicità mostriamo range usando la tolleranza media
            tol_mean = sum(tolerances) / len(tolerances) if tolerances else 0
            min_total = total_resistance * (1 - tol_mean / 100)
            max_total = total_resistance * (1 + tol_mean / 100)

            result = f"Resistenze: {[self.format_value(r) for r in resistances]}\n"
            result += f"Connessione: {self.conn_type.get().title()}\n"
            result += f"Calcolo: {calculation}\n\n"
            result += f"Resistenza totale: {self.format_value(total_resistance)}\n"
            result += f"Tolleranza (media): ±{tol_mean}%\n"
            result += f"Range: {self.format_value(min_total)} - {self.format_value(max_total)}"

            self.series_result_text.delete(1.0, tk.END)
            self.series_result_text.insert(1.0, result)

            # Crea grafico
            self.create_series_graph(resistances, total_resistance)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo: {str(e)}")

    def optimize_with_commercial(self):
        try:
            resistances_str = self.resistances_entry.get()
            resistances = [float(x.strip()) for x in resistances_str.split(',')]
            tolerance = float(self.tolerance_entry.get())
            series = self.e_series[self.series_var.get()]

            optimized_resistances = []
            total_error = 0

            result = "Ottimizzazione con valori commerciali:\n\n"

            for i, target_r in enumerate(resistances):
                best_match = self.find_best_commercial_value(target_r, series)
                optimized_resistances.append(best_match['value'])
                total_error += best_match['error']

                result += f"R{i + 1}: {self.format_value(target_r)} → {self.format_value(best_match['value'])} "
                result += f"(errore: {best_match['error']:.2f}%)\n"

            # Calcola resistenza totale ottimizzata
            if self.conn_type.get() == "serie":
                optimized_total = sum(optimized_resistances)
            else:
                optimized_total = 1 / sum(1 / r for r in optimized_resistances)

            original_total = sum(resistances) if self.conn_type.get() == "serie" else 1 / sum(
                1 / r for r in resistances)
            total_error_percent = abs((optimized_total - original_total) / original_total) * 100

            result += f"\nResistenza totale originale: {self.format_value(original_total)}\n"
            result += f"Resistenza totale ottimizzata: {self.format_value(optimized_total)}\n"
            result += f"Errore totale: {total_error_percent:.2f}%"

            self.series_result_text.delete(1.0, tk.END)
            self.series_result_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'ottimizzazione: {str(e)}")

    def find_best_commercial_value(self, target_value, series):
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

    def create_series_graph(self, resistances, total_resistance):
        # Pulisci frame grafico
        for widget in self.series_graph_frame.winfo_children():
            widget.destroy()

        # Crea figura
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Dati per il grafico
        x_pos = range(len(resistances))
        values = [r / total_resistance * 100 for r in resistances]  # Percentuale del totale

        colors = ['#c44e52', '#4c72b0', '#55a868', '#ffb347', '#7f5acd']
        bars = ax.bar(x_pos, values, color=colors[:len(resistances)])
        ax.set_xlabel('Resistenze')
        ax.set_ylabel('Percentuale del totale (%)')
        ax.set_title('Distribuzione delle resistenze')

        # Aggiungi valori sulle barre
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom')

        # Canvas per tkinter
        canvas = FigureCanvasTkAgg(fig, self.series_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_monte_carlo_tab(self):
        # Frame per input
        input_frame = ttk.LabelFrame(self.monte_carlo_frame, text="Parametri Monte Carlo")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Partitore di tensione
        divider_frame = ttk.LabelFrame(input_frame, text="Partitore di Tensione")
        divider_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(divider_frame, text="R1 (Ω):").grid(row=0, column=0, padx=5, pady=5)
        self.r1_entry = ttk.Entry(divider_frame, width=15)
        self.r1_entry.grid(row=0, column=1, padx=5, pady=5)
        self.r1_entry.insert(0, "1000")

        ttk.Label(divider_frame, text="R2 (Ω):").grid(row=0, column=2, padx=5, pady=5)
        self.r2_entry = ttk.Entry(divider_frame, width=15)
        self.r2_entry.grid(row=0, column=3, padx=5, pady=5)
        self.r2_entry.insert(0, "2000")

        ttk.Label(divider_frame, text="Vin (V):").grid(row=1, column=0, padx=5, pady=5)
        self.vin_entry = ttk.Entry(divider_frame, width=15)
        self.vin_entry.grid(row=1, column=1, padx=5, pady=5)
        self.vin_entry.insert(0, "10")

        # Parametri Monte Carlo
        mc_frame = ttk.LabelFrame(input_frame, text="Parametri Simulazione")
        mc_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(mc_frame, text="Tolleranza (%):").grid(row=0, column=0, padx=5, pady=5)
        self.mc_tolerance_entry = ttk.Entry(mc_frame, width=10)
        self.mc_tolerance_entry.grid(row=0, column=1, padx=5, pady=5)
        self.mc_tolerance_entry.insert(0, "5")

        ttk.Label(mc_frame, text="Numero simulazioni:").grid(row=0, column=2, padx=5, pady=5)
        self.mc_iterations_entry = ttk.Entry(mc_frame, width=10)
        self.mc_iterations_entry.grid(row=0, column=3, padx=5, pady=5)
        self.mc_iterations_entry.insert(0, "1000")

        # Pulsante simulazione
        sim_btn = ttk.Button(input_frame, text="Esegui Simulazione Monte Carlo",
                             command=self.run_monte_carlo)
        sim_btn.pack(pady=10)

        # Frame per risultato
        result_frame = ttk.LabelFrame(self.monte_carlo_frame, text="Risultati")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.mc_result_text = ScrolledText(result_frame, height=8, width=60)
        self.mc_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame per grafico
        self.mc_graph_frame = ttk.Frame(self.monte_carlo_frame)
        self.mc_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_monte_carlo(self):
        try:
            # Parametri
            r1_nominal = float(self.r1_entry.get())
            r2_nominal = float(self.r2_entry.get())
            vin = float(self.vin_entry.get())
            tolerance = float(self.mc_tolerance_entry.get()) / 100
            iterations = int(self.mc_iterations_entry.get())

            # Simulazione Monte Carlo
            vout_values = []
            r1_values = []
            r2_values = []

            for _ in range(iterations):
                # Genera valori con tolleranza
                r1 = r1_nominal * random.uniform(1 - tolerance, 1 + tolerance)
                r2 = r2_nominal * random.uniform(1 - tolerance, 1 + tolerance)

                # Calcola Vout
                vout = vin * r2 / (r1 + r2)

                vout_values.append(vout)
                r1_values.append(r1)
                r2_values.append(r2)

            # Statistiche
            vout_mean = np.mean(vout_values)
            vout_std = np.std(vout_values)
            vout_min = np.min(vout_values)
            vout_max = np.max(vout_values)

            # Vout teorico
            vout_theoretical = vin * r2_nominal / (r1_nominal + r2_nominal)

            result = f"Simulazione Monte Carlo ({iterations} iterazioni)\n"
            result += f"Tolleranza: ±{tolerance * 100}%\n\n"
            result += f"Vout teorico: {vout_theoretical:.3f} V\n"
            result += f"Media Vout: {vout_mean:.3f} V\n"
            result += f"Deviazione standard: {vout_std:.3f} V\n"
            result += f"Range Vout: {vout_min:.3f} - {vout_max:.3f} V\n"
            result += f"Errore massimo: {abs(vout_max - vout_min) / vout_theoretical * 100:.2f}%"

            self.mc_result_text.delete(1.0, tk.END)
            self.mc_result_text.insert(1.0, result)

            # Crea grafico
            self.create_mc_graph(vout_values, vout_theoretical)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella simulazione: {str(e)}")

    def create_mc_graph(self, vout_values, vout_theoretical):
        # Pulisci frame grafico
        for widget in self.mc_graph_frame.winfo_children():
            widget.destroy()

        # Crea figura
        fig = Figure(figsize=(10, 6), dpi=100)

        # Istogramma
        ax1 = fig.add_subplot(211)
        ax1.hist(vout_values, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(vout_theoretical, color='red', linestyle='--', linewidth=2,
                    label=f'Teorico: {vout_theoretical:.3f} V')
        ax1.set_xlabel('Vout (V)')
        ax1.set_ylabel('Frequenza')
        ax1.set_title('Distribuzione Monte Carlo di Vout')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Grafico scatter delle prime 100 simulazioni
        ax2 = fig.add_subplot(212)
        indices = range(min(100, len(vout_values)))
        ax2.scatter(indices, vout_values[:100], alpha=0.6, color='green')
        ax2.axhline(vout_theoretical, color='red', linestyle='--', linewidth=2,
                    label=f'Teorico: {vout_theoretical:.3f} V')
        ax2.set_xlabel('Simulazione')
        ax2.set_ylabel('Vout (V)')
        ax2.set_title('Prime 100 simulazioni')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Canvas per tkinter
        canvas = FigureCanvasTkAgg(fig, self.mc_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_power_tab(self):
        # Frame per input
        input_frame = ttk.LabelFrame(self.power_frame, text="Calcolo Potenza")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Parametri
        param_frame = ttk.Frame(input_frame)
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(param_frame, text="Tensione (V):").grid(row=0, column=0, padx=5, pady=5)
        self.voltage_entry = ttk.Entry(param_frame, width=15)
        self.voltage_entry.grid(row=0, column=1, padx=5, pady=5)
        self.voltage_entry.insert(0, "5")

        ttk.Label(param_frame, text="Corrente (A):").grid(row=0, column=2, padx=5, pady=5)
        self.current_entry = ttk.Entry(param_frame, width=15)
        self.current_entry.grid(row=0, column=3, padx=5, pady=5)
        self.current_entry.insert(0, "0.01")

        ttk.Label(param_frame, text="Resistenza (Ω):").grid(row=1, column=0, padx=5, pady=5)
        self.resistance_entry = ttk.Entry(param_frame, width=15)
        self.resistance_entry.grid(row=1, column=1, padx=5, pady=5)
        self.resistance_entry.insert(0, "500")

        # Package
        package_frame = ttk.Frame(input_frame)
        package_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(package_frame, text="Package:").pack(side=tk.LEFT, padx=5)
        self.package_var = tk.StringVar(value="0805")
        self.package_combo = ttk.Combobox(package_frame, textvariable=self.package_var,
                                          values=list(self.package_power.keys()), width=15)
        self.package_combo.pack(side=tk.LEFT, padx=5, pady=5)

        # Pulsante calcola
        calc_btn = ttk.Button(input_frame, text="Calcola Potenza", command=self.calculate_power)
        calc_btn.pack(pady=10)

        # Frame per risultato
        result_frame = ttk.LabelFrame(self.power_frame, text="Risultati")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.power_result_text = ScrolledText(result_frame, height=10, width=60)
        self.power_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame per informazioni package
        package_frame = ttk.LabelFrame(self.power_frame, text="Informazioni Package")
        package_frame.pack(fill=tk.X, padx=10, pady=10)

        self.package_info_text = ScrolledText(package_frame, height=6, width=60)
        self.package_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_package_info()

        # Aggiorna info quando cambia il package
        self.package_combo.bind('<<ComboboxSelected>>', lambda e: self.update_package_info())

    def calculate_power(self):
        try:
            voltage = float(self.voltage_entry.get()) if self.voltage_entry.get() else 0
            current = float(self.current_entry.get()) if self.current_entry.get() else 0
            resistance = float(self.resistance_entry.get()) if self.resistance_entry.get() else 0

            # Calcola potenza con le formule disponibili
            powers = []
            formulas = []

            if voltage > 0 and current > 0:
                power1 = voltage * current
                powers.append(power1)
                formulas.append(f"P = V × I = {voltage} × {current} = {power1:.6f} W")

            if voltage > 0 and resistance > 0:
                power2 = (voltage ** 2) / resistance
                powers.append(power2)
                formulas.append(f"P = V²/R = {voltage}²/{resistance} = {power2:.6f} W")

            if current > 0 and resistance > 0:
                power3 = (current ** 2) * resistance
                powers.append(power3)
                formulas.append(f"P = I² × R = {current}² × {resistance} = {power3:.6f} W")

            if not powers:
                messagebox.showwarning("Attenzione", "Inserisci almeno due parametri")
                return

            avg_power = sum(powers) / len(powers)

            # Verifica potenza del package
            package_power = self.package_power[self.package_var.get()]
            safety_factor = package_power / avg_power if avg_power > 0 else float('inf')

            result = "Calcolo potenza:\n\n"
            for formula in formulas:
                result += formula + "\n"

            result += f"\nPotenza media: {avg_power:.6f} W\n"
            result += f"Potenza package ({self.package_var.get()}): {package_power} W\n"

            if safety_factor >= 2:
                result += f"Fattore di sicurezza: {safety_factor:.1f}x - OK\n"
                result += "✓ Il package è adeguato"
            elif safety_factor >= 1:
                result += f"Fattore di sicurezza: {safety_factor:.1f}x - Limite\n"
                result += "⚠ Package al limite - considera un package più grande"
            else:
                result += f"Fattore di sicurezza: {safety_factor:.1f}x - INSUFFICIENTE\n"
                result += "✗ Il package non è adeguato - Scegli un package più grande!"

            self.power_result_text.delete(1.0, tk.END)
            self.power_result_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo: {str(e)}")

    def update_package_info(self):
        package = self.package_var.get()
        power = self.package_power.get(package, 0)

        info = f"Package: {package}\n"
        info += f"Potenza massima: {power} W\n"
        info += f"Potenza consigliata (50%): {power * 0.5} W\n"
        info += f"Potenza minima consigliata: {power * 0.25} W\n\n"

        info += "Guida ai package:\n"
        info += "• 0201/0402: Circuiti ad alta densità\n"
        info += "• 0603/0805: Uso generale\n"
        info += "• 1206/1210: Potenze medie\n"
        info += "• 1812/2010/2512: Potenze elevate\n"
        info += "• AXIAL/RADIAL: Through-hole, potenze alte"

        self.package_info_text.delete(1.0, tk.END)
        self.package_info_text.insert(1.0, info)

    def format_value(self, value):
        """Formatta il valore con il prefisso appropriato"""
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

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Esporta risultato...', command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label='Esci', command=self.root.quit)
        menubar.add_cascade(label='File', menu=file_menu)

        # Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='Guida rapida', command=self.show_quick_help)
        help_menu.add_command(label='Informazioni', command=self.show_about)
        menubar.add_cascade(label='Aiuto', menu=help_menu)

        self.root.config(menu=menubar)

        # Barra di stato
        self.status = tk.StringVar()
        self.status.set('Pronto')
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def export_results(self):
        try:
            content = ''
            # raccoglie contenuti visibili
            for widget in (self.color_result_text, self.series_result_text, self.mc_result_text, self.power_result_text):
                try:
                    content += widget.get(1.0, tk.END).strip() + '\n\n'
                except Exception:
                    pass

            if not content.strip():
                messagebox.showinfo('Esporta', 'Nessun risultato da esportare')
                return

            path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Testo', '*.txt')])
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo('Esporta', f'Risultati esportati in {path}')
                self.status.set(f'Risultati esportati: {path}')

        except Exception as e:
            messagebox.showerror('Errore export', str(e))

    def show_quick_help(self):
        help_text = (
            'Guida rapida:\n\n'
            '- Codice Colori: ricava valore dalla combinazione di bande.\n'
            '- Serie/Parallelo: calcola resistenza totale e ottimizza con serie commerciali.\n'
            '- Monte Carlo: simula variazioni dovute a tolleranza componenti.\n'
            '- Potenza: valuta potenza dissipata e confronto con package.'
        )
        messagebox.showinfo('Guida rapida', help_text)

    def show_about(self):
        about = 'Electronic Tool — versione educativa\nAutore: (tuo nome)\nFunzionalità: analisi resistenze, ottimizzazione e simulazioni Monte Carlo.'
        messagebox.showinfo('Informazioni', about)


def main():
    try:
        root = tk.Tk()
        app = ElectronicTool(root)
        root.mainloop()
    except Exception:
        with open('error.log', 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
        # Rilancia l'eccezione dopo averla loggata per visibilità in terminale
        raise


if __name__ == "__main__":
    main()