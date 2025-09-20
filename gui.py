
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from resistor_lib import (
    e_series, package_power, color_codes, tolerance_colors
)
from utils import create_menu, format_value
from logic import (
    calculate_color_code_logic,
    find_color_code_logic,
    calculate_series_parallel_logic,
    optimize_with_commercial_logic,
    run_monte_carlo_logic,
    calculate_power_logic,
)


class ElectronicTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Electronic Tool — Analisi e Didattica sulle Resistenze")
        self.root.geometry("1100x820")
        self.set_style()

        # Imported constants and helpers from resistor_lib
        self.e_series = e_series
        self.package_power = package_power
        self.color_codes = color_codes
        self.tolerance_colors = tolerance_colors

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
        create_menu(self)

        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=12, pady=(8, 0))
        ttk.Label(header, text='Electronic Tool — Resistenza e Circuiti', style='Header.TLabel').pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.color_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.color_frame, text="Codice Colori")
        self.create_color_tab()

        self.series_parallel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.series_parallel_frame, text="Serie/Parallelo")
        self.create_series_parallel_tab()

        self.monte_carlo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monte_carlo_frame, text="Monte Carlo")
        self.create_monte_carlo_tab()

        self.power_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.power_frame, text="Potenza")
        self.create_power_tab()
        
        self.status = tk.StringVar()
        self.status.set('Pronto')
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def create_color_tab(self):
        input_frame = ttk.LabelFrame(self.color_frame, text="Inserisci Codice Colori — istruzioni: scegli le bande e premi 'Calcola Valore'")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        bands_frame = ttk.Frame(input_frame)
        bands_frame.pack(fill=tk.X, padx=5, pady=5)

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

        calc_btn = ttk.Button(input_frame, text="Calcola Valore", command=self.calculate_color_code)
        calc_btn.pack(pady=10)

        draw_frame = ttk.Frame(self.color_frame)
        draw_frame.pack(fill=tk.X, padx=10, pady=5)
        self.res_canvas = tk.Canvas(draw_frame, width=440, height=80, bg='#FFFFFF', highlightthickness=1, highlightbackground='#CCCCCC')
        self.res_canvas.pack(side=tk.LEFT, padx=5)
        self.update_resistor_drawing()

        result_frame = ttk.LabelFrame(self.color_frame, text="Risultato")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.color_result_text = ScrolledText(result_frame, height=8, width=60)
        self.color_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        value_frame = ttk.LabelFrame(self.color_frame, text="Trova Codice Colori — inserisci valore e trova il codice commerciale più vicino")
        value_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(value_frame, text="Valore (Ω):").grid(row=0, column=0, padx=5, pady=5)
        self.value_entry = ttk.Entry(value_frame, width=15)
        self.value_entry.grid(row=0, column=1, padx=5, pady=5)
        self.value_entry.insert(0, "1000")

        find_btn = ttk.Button(value_frame, text="Trova Codice", command=self.find_color_code)
        find_btn.grid(row=0, column=2, padx=10, pady=5)

    def calculate_color_code(self):
        result, error = calculate_color_code_logic(
            self.color_codes, self.tolerance_colors,
            self.band1_var.get(), self.band2_var.get(),
            self.multiplier_var.get(), self.tolerance_var.get()
        )
        if error:
            messagebox.showerror("Errore", error)
        else:
            self.color_result_text.delete(1.0, tk.END)
            self.color_result_text.insert(1.0, result)
        self.update_resistor_drawing()

    def update_band_visibility(self):
        self.update_resistor_drawing()

    def update_resistor_drawing(self):
        try:
            self.res_canvas.delete('all')
        except Exception:
            return

        w = 440; h = 80
        self.res_canvas.create_rectangle(40, 20, 400, 60, fill='#F0F0F0', outline='#333333')
        self.res_canvas.create_line(0, 40, 40, 40, width=3, fill='#333333')
        self.res_canvas.create_line(400, 40, w, 40, width=3, fill='#333333')

        band_colors = []
        try:
            band_colors.append(self.color_codes[self.band1_var.get()][1])
            band_colors.append(self.color_codes[self.band2_var.get()][1])
            band_colors.append(self.color_codes[self.multiplier_var.get()][1])
            band_colors.append(self.tolerance_colors[self.tolerance_var.get()][1])
        except Exception:
            band_colors = ['#000000'] * 4

        n = self.num_bands.get()
        if n == 5:
            band_positions = [80, 140, 200, 260, 320]
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
            result, error = find_color_code_logic(value, self.e_series)
            if error:
                messagebox.showwarning("Attenzione", error)
            else:
                self.color_result_text.delete(1.0, tk.END)
                self.color_result_text.insert(1.0, result)
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un valore numerico valido")

    def create_series_parallel_tab(self):
        input_frame = ttk.LabelFrame(self.series_parallel_frame, text="Inserisci Resistenze — valori con tolleranza per singolo componente")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        conn_frame = ttk.Frame(input_frame)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(conn_frame, text="Tipo connessione:").pack(side=tk.LEFT, padx=5)
        self.conn_type = tk.StringVar(value="serie")
        ttk.Radiobutton(conn_frame, text="Serie", variable=self.conn_type, value="serie").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(conn_frame, text="Parallelo", variable=self.conn_type, value="parallelo").pack(side=tk.LEFT)

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
                for idx, rw in enumerate(self.res_rows, start=1):
                    rw['val'].grid(row=idx, column=0)
                    rw['tol'].grid(row=idx, column=1)
                    rw['btn'].grid(row=idx, column=2)
            except Exception:
                pass

        add_res_row('1000', '5')
        add_res_row('2000', '5')

        add_btn = ttk.Button(list_frame, text='Aggiungi Resistenza', command=lambda: add_res_row('1000', '5'))
        add_btn.grid(row=99, column=0, pady=6, sticky=tk.W)

        series_frame = ttk.Frame(input_frame)
        series_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(series_frame, text="Serie commerciale:").pack(side=tk.LEFT, padx=5)
        self.series_var = tk.StringVar(value="E12")
        self.series_combo = ttk.Combobox(series_frame, textvariable=self.series_var,
                         values=list(self.e_series.keys()), width=10)
        self.series_combo.pack(side=tk.LEFT, padx=5, pady=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)

        calc_btn = ttk.Button(btn_frame, text="Calcola", command=self.calculate_series_parallel)
        calc_btn.pack(side=tk.LEFT, padx=5)

        optimize_btn = ttk.Button(btn_frame, text="Ottimizza con Valori Commerciali",
                                  command=self.optimize_with_commercial)
        optimize_btn.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(self.series_parallel_frame, text="Risultato")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.series_result_text = ScrolledText(result_frame, height=12, width=60)
        self.series_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.series_graph_frame = ttk.Frame(self.series_parallel_frame)
        self.series_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def calculate_series_parallel(self):
        try:
            resistances = [float(rw['val'].get()) for rw in self.res_rows]
            tolerances = [float(rw['tol'].get()) for rw in self.res_rows]
            result, total_resistance, error = calculate_series_parallel_logic(resistances, tolerances, self.conn_type.get())
            if error:
                messagebox.showerror("Errore", error)
            else:
                self.series_result_text.delete(1.0, tk.END)
                self.series_result_text.insert(1.0, result)
                self.create_series_graph(resistances, total_resistance)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo: {str(e)}")

    def optimize_with_commercial(self):
        try:
            resistances = [float(rw['val'].get()) for rw in self.res_rows]
            result, error = optimize_with_commercial_logic(resistances, self.conn_type.get(), self.series_var.get(), self.e_series)
            if error:
                messagebox.showwarning('Ottimizza', error)
            else:
                self.series_result_text.delete(1.0, tk.END)
                self.series_result_text.insert(1.0, result)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'ottimizzazione: {str(e)}")

    def create_series_graph(self, resistances, total_resistance):
        for widget in self.series_graph_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        x_pos = range(len(resistances))
        values = [r / total_resistance * 100 for r in resistances]

        colors = ['#c44e52', '#4c72b0', '#55a868', '#ffb347', '#7f5acd']
        bars = ax.bar(x_pos, values, color=colors[:len(resistances)])
        ax.set_xlabel('Resistenze')
        ax.set_ylabel('Percentuale del totale (%)')
        ax.set_title('Distribuzione delle resistenze')

        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(fig, self.series_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_monte_carlo_tab(self):
        input_frame = ttk.LabelFrame(self.monte_carlo_frame, text="Parametri Monte Carlo")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

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

        sim_btn = ttk.Button(input_frame, text="Esegui Simulazione Monte Carlo",
                             command=self.run_monte_carlo)
        sim_btn.pack(pady=10)

        result_frame = ttk.LabelFrame(self.monte_carlo_frame, text="Risultati")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.mc_result_text = ScrolledText(result_frame, height=8, width=60)
        self.mc_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.mc_graph_frame = ttk.Frame(self.monte_carlo_frame)
        self.mc_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_monte_carlo(self):
        try:
            vin = float(self.vin_entry.get())
            iterations = int(self.mc_iterations_entry.get())

            r1_nominal, tol1, r2_nominal, tol2 = None, None, None, None
            if len(self.res_rows) >= 2:
                try:
                    r1_nominal = float(self.res_rows[0]['val'].get())
                    tol1 = float(self.res_rows[0]['tol'].get()) / 100
                except Exception:
                    pass
                try:
                    r2_nominal = float(self.res_rows[1]['val'].get())
                    tol2 = float(self.res_rows[1]['tol'].get()) / 100
                except Exception:
                    pass

            if r1_nominal is None:
                r1_nominal = float(self.r1_entry.get())
                tol1 = float(self.mc_tolerance_entry.get()) / 100
            if r2_nominal is None:
                r2_nominal = float(self.r2_entry.get())
                tol2 = float(self.mc_tolerance_entry.get()) / 100

            result, vout_values, vout_theoretical, error = run_monte_carlo_logic(vin, iterations, r1_nominal, tol1, r2_nominal, tol2)

            if error:
                messagebox.showerror("Errore", error)
            else:
                self.mc_result_text.delete(1.0, tk.END)
                self.mc_result_text.insert(1.0, result)
                self.create_mc_graph(vout_values, vout_theoretical)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella simulazione: {str(e)}")

    def create_mc_graph(self, vout_values, vout_theoretical):
        for widget in self.mc_graph_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(10, 6), dpi=100)

        ax1 = fig.add_subplot(211)
        ax1.hist(vout_values, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(vout_theoretical, color='red', linestyle='--', linewidth=2,
                    label=f'Teorico: {vout_theoretical:.3f} V')
        ax1.set_xlabel('Vout (V)')
        ax1.set_ylabel('Frequenza')
        ax1.set_title('Distribuzione Monte Carlo di Vout')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

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

        canvas = FigureCanvasTkAgg(fig, self.mc_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_power_tab(self):
        input_frame = ttk.LabelFrame(self.power_frame, text="Calcolo Potenza")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

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

        package_frame = ttk.Frame(input_frame)
        package_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(package_frame, text="Package:").pack(side=tk.LEFT, padx=5)
        self.package_var = tk.StringVar(value="0805")
        self.package_combo = ttk.Combobox(package_frame, textvariable=self.package_var,
                                          values=list(self.package_power.keys()), width=15)
        self.package_combo.pack(side=tk.LEFT, padx=5, pady=5)

        calc_btn = ttk.Button(input_frame, text="Calcola Potenza", command=self.calculate_power)
        calc_btn.pack(pady=10)

        result_frame = ttk.LabelFrame(self.power_frame, text="Risultati")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.power_result_text = ScrolledText(result_frame, height=10, width=60)
        self.power_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        package_info_frame = ttk.LabelFrame(self.power_frame, text="Informazioni Package")
        package_info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.package_info_text = ScrolledText(package_info_frame, height=6, width=60)
        self.package_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_package_info()

        self.package_combo.bind('<<ComboboxSelected>>', lambda e: self.update_package_info())

    def calculate_power(self):
        try:
            voltage = float(self.voltage_entry.get()) if self.voltage_entry.get() else 0
            current = float(self.current_entry.get()) if self.current_entry.get() else 0
            resistance = float(self.resistance_entry.get()) if self.resistance_entry.get() else 0
            package_name = self.package_var.get()
            package_power_val = self.package_power[package_name]

            result, error = calculate_power_logic(voltage, current, resistance, package_power_val, package_name)

            if error:
                messagebox.showwarning("Attenzione", error)
            else:
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
