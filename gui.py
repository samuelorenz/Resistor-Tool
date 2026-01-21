
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
    decode_smd_code_logic,
    design_voltage_divider_logic,
    calculate_led_resistor_logic,
    design_rc_filter_logic,
    calculate_regulator_logic,
    calculate_current_divider_logic,
    convert_awg_logic,
    search_glossary_logic
)
from resistor_lib import (
    e_series, package_power, color_codes, tolerance_colors,
    regulator_specs, awg_table
)
from capacitor_lib import capacitor_e_series

class ElectronicTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Electronic Tool — Dashboard Professionale")
        self.root.geometry("1100x820")
        
        # Inizializzazione dati
        self.e_series = e_series
        self.capacitor_e_series = capacitor_e_series
        self.package_power = package_power
        self.color_codes = color_codes
        self.tolerance_colors = tolerance_colors
        
        self.set_style()
        self.create_widgets()
        self.show_dashboard()

    def set_style(self):
        style = ttk.Style(self.root)
        try: style.theme_use('clam')
        except: pass
        
        # Palette Professionale Light
        self.bg_color = "#F5F7FA"
        self.surface_color = "#FFFFFF"
        self.primary_color = "#2563EB"
        self.text_color = "#1F2937"
        
        self.root.configure(background=self.bg_color)
        
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=self.primary_color)
        style.configure('Subheader.TLabel', font=('Segoe UI', 12, 'bold'), foreground=self.text_color)
        
        style.configure('Card.TFrame', background=self.surface_color, relief='flat')
        style.configure('TButton', font=('Segoe UI', 10))
        
        # Stile specifico per bottoni Dashboard
        style.configure('Dash.TButton', font=('Segoe UI', 11, 'bold'), padding=10)

    def create_widgets(self):
        create_menu(self)
        
        # Top Bar
        self.top_bar = ttk.Frame(self.root)
        self.top_bar.pack(fill=tk.X, padx=20, pady=15)
        
        self.title_label = ttk.Label(self.top_bar, text="Electronic Tool", style='Header.TLabel')
        self.title_label.pack(side=tk.LEFT)
        
        self.nav_label = ttk.Label(self.top_bar, text=" > Dashboard", style='Subheader.TLabel')
        self.nav_label.pack(side=tk.LEFT, padx=10)

        # Main Content Area
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status Bar
        self.status = tk.StringVar(value='Pronto')
        status_bar = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W, font=('Segoe UI', 9))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def clear_main_container(self, new_nav_text=""):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.nav_label.config(text=f" > {new_nav_text}")

    def show_dashboard(self):
        self.clear_main_container("Dashboard")
        
        dash_frame = ttk.Frame(self.main_container)
        dash_frame.pack(fill=tk.BOTH, expand=True)
        
        categories = [
            ("CALCOLATORI BASE", [
                ("🎨 Codice Colori", "color"),
                ("🔢 Codici SMD", "smd")
            ]),
            ("ANALISI", [
                ("⚡ Serie/Parallelo", "series_parallel"),
                ("📊 Monte Carlo", "monte_carlo"),
                ("🌡️ Potenza/Derating", "power")
            ]),
            ("PROGETTAZIONE", [
                ("📐 Partitore", "divider"),
                ("🔌 Regolatori", "regulator"),
                ("〰️ Filtri RC", "filter"),
                ("💡 LED Resistor", "led")
            ]),
            ("UTILITY", [
                ("📏 Tabella AWG", "awg"),
                ("🌊 Ripartitore I", "curr_div"),
                ("📚 Glossario", "glossary")
            ])
        ]
        
        for i, (cat_name, tools) in enumerate(categories):
            cat_frame = ttk.LabelFrame(dash_frame, text=f"  {cat_name}  ")
            cat_frame.grid(row=i//2, column=i%2, padx=15, pady=15, sticky='nsew')
            dash_frame.grid_columnconfigure(i%2, weight=1)
            dash_frame.grid_rowconfigure(i//2, weight=1)
            
            for tool_name, tool_id in tools:
                btn = ttk.Button(cat_frame, text=tool_name, style='Dash.TButton', 
                                 command=lambda tid=tool_id: self.show_tool(tid))
                btn.pack(fill=tk.X, padx=20, pady=8)

    def show_tool(self, tool_id):
        tool_map = {
            "color": (self.create_color_view, "Codice Colori"),
            "smd": (self.create_smd_view, "Codici SMD"),
            "series_parallel": (self.create_series_parallel_view, "Serie e Parallelo"),
            "monte_carlo": (self.create_monte_carlo_view, "Analisi Monte Carlo"),
            "power": (self.create_power_view, "Potenza e Derating"),
            "divider": (self.create_divider_view, "Partitore di Tensione"),
            "regulator": (self.create_regulator_view, "Regolatori"),
            "filter": (self.create_rc_filter_view, "Filtri RC"), # Renamed from create_design_calculator_tab
            "led": (self.create_led_resistor_view, "Resistore LED"), # Renamed from create_design_calculator_tab
            "awg": (self.create_awg_view, "Tabella AWG"), # Renamed from create_utility_tab
            "curr_div": (self.create_current_divider_view, "Ripartitore di Corrente"), # Renamed from create_utility_tab
            "glossary": (self.create_glossary_view, "Glossario Tecnico")
        }
        
        if tool_id in tool_map:
            func, label = tool_map[tool_id]
            self.clear_main_container(label)
            
            # Pulsante "Indietro" fisso in alto a destra o sinistra
            back_btn = ttk.Button(self.main_container, text="⬅ Torna alla Dashboard", command=self.show_dashboard)
            back_btn.pack(anchor=tk.NW, pady=(0, 10))
            
            func()

    def create_color_view(self):
        input_frame = ttk.LabelFrame(self.main_container, text="1. Decodifica Codice Colori (IEC 60062)")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        bands_frame = ttk.Frame(input_frame)
        bands_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(bands_frame, text="Numero bande:").grid(row=0, column=4, padx=5, pady=5)
        self.num_bands = tk.IntVar(value=4)
        ttk.Radiobutton(bands_frame, text="4", variable=self.num_bands, value=4, command=self.update_band_visibility).grid(row=0, column=5)
        ttk.Radiobutton(bands_frame, text="5", variable=self.num_bands, value=5, command=self.update_band_visibility).grid(row=0, column=6)
        ttk.Label(bands_frame, text="Banda 1:").grid(row=0, column=0, padx=5, pady=5)
        self.band1_var = tk.StringVar()
        self.band1_combo = ttk.Combobox(bands_frame, textvariable=self.band1_var, values=list(self.color_codes.keys())[:-2], width=12)
        self.band1_combo.grid(row=0, column=1, padx=5, pady=5)
        self.band1_combo.set("marrone")
        ttk.Label(bands_frame, text="Banda 2:").grid(row=0, column=2, padx=5, pady=5)
        self.band2_var = tk.StringVar()
        self.band2_combo = ttk.Combobox(bands_frame, textvariable=self.band2_var, values=list(self.color_codes.keys()), width=12)
        self.band2_combo.grid(row=0, column=3, padx=5, pady=5)
        self.band2_combo.set("nero")
        ttk.Label(bands_frame, text="Banda 3 (Moltiplicatore):").grid(row=1, column=0, padx=5, pady=5)
        self.multiplier_var = tk.StringVar()
        self.multiplier_combo = ttk.Combobox(bands_frame, textvariable=self.multiplier_var, values=list(self.color_codes.keys()), width=12)
        self.multiplier_combo.grid(row=1, column=1, padx=5, pady=5)
        self.multiplier_combo.set("rosso")
        ttk.Label(bands_frame, text="Tolleranza:").grid(row=1, column=2, padx=5, pady=5)
        self.tolerance_var = tk.StringVar()
        self.tolerance_combo = ttk.Combobox(bands_frame, textvariable=self.tolerance_var, values=list(self.tolerance_colors.keys()), width=12)
        self.tolerance_combo.grid(row=1, column=3, padx=5, pady=5)
        self.tolerance_combo.set("oro")
        calc_btn = ttk.Button(input_frame, text="Decodifica e Spiega", command=self.calculate_color_code)
        calc_btn.pack(pady=10)
        draw_frame = ttk.Frame(self.color_frame)
        draw_frame.pack(fill=tk.X, padx=10, pady=5)
        self.res_canvas = tk.Canvas(draw_frame, width=440, height=80, bg='#FFFFFF', highlightthickness=1, highlightbackground='#CCCCCC')
        self.res_canvas.pack(side=tk.LEFT, padx=5)
        self.update_resistor_drawing()
        result_frame = ttk.LabelFrame(self.color_frame, text="Analisi e Spiegazione")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.color_result_text = ScrolledText(result_frame, height=10, width=60, wrap=tk.WORD)
        self.color_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        value_frame = ttk.LabelFrame(self.color_frame, text="2. Trova Valore Commerciale e Codice (IEC 60063)")
        value_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(value_frame, text="Valore Desiderato (Ω):").grid(row=0, column=0, padx=5, pady=5)
        self.value_entry = ttk.Entry(value_frame, width=15)
        self.value_entry.grid(row=0, column=1, padx=5, pady=5)
        self.value_entry.insert(0, "1000")
        find_btn = ttk.Button(value_frame, text="Trova e Spiega", command=self.find_color_code)
        find_btn.grid(row=0, column=2, padx=10, pady=5)

    def create_smd_view(self):
        input_frame = ttk.LabelFrame(self.main_container, text="1. Inserisci Codice Resistore SMD")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Codice:").pack(side=tk.LEFT, padx=5, pady=5)
        self.smd_code_entry = ttk.Entry(input_frame, width=15)
        self.smd_code_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.smd_code_entry.insert(0, "103")
        
        self.smd_code_type = tk.StringVar(value="standard")
        ttk.Radiobutton(input_frame, text="Standard (3/4 cifre, R)", variable=self.smd_code_type, value="standard").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(input_frame, text="EIA-96 (1%)", variable=self.smd_code_type, value="eia96").pack(side=tk.LEFT, padx=10)
        
        calc_btn = ttk.Button(self.main_container, text="Decodifica e Spiega", command=self.decode_smd_code)
        calc_btn.pack(pady=10)
        
        result_frame = ttk.LabelFrame(self.main_container, text="Analisi e Spiegazione")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.smd_result_text = ScrolledText(result_frame, height=15, width=60, wrap=tk.WORD)
        self.smd_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def decode_smd_code(self):
        code = self.smd_code_entry.get()
        code_type = self.smd_code_type.get()
        result, error = decode_smd_code_logic(code, code_type)
        if error:
            messagebox.showerror("Errore di Decodifica", error)
        else:
            self.smd_result_text.delete(1.0, tk.END)
            self.smd_result_text.insert(1.0, result)

    def create_power_view(self):
        input_frame = ttk.LabelFrame(self.main_container, text="1. Inserisci Parametri Elettrici e Termici")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        param_frame = ttk.Frame(input_frame)
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Tensione (V):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.voltage_entry = ttk.Entry(param_frame, width=15)
        self.voltage_entry.grid(row=0, column=1, padx=5, pady=5)
        self.voltage_entry.insert(0, "5")
        
        ttk.Label(param_frame, text="Corrente (A):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.current_entry = ttk.Entry(param_frame, width=15)
        self.current_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Resistenza (Ω):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.resistance_entry = ttk.Entry(param_frame, width=15)
        self.resistance_entry.grid(row=1, column=1, padx=5, pady=5)
        self.resistance_entry.insert(0, "500")
        
        ttk.Label(param_frame, text="Temp. Ambiente (°C):").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.ambient_temp_entry = ttk.Entry(param_frame, width=15)
        self.ambient_temp_entry.grid(row=1, column=3, padx=5, pady=5)
        self.ambient_temp_entry.insert(0, "25")
        
        package_frame = ttk.LabelFrame(self.main_container, text="2. Scegli il Package del Resistore")
        package_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(package_frame, text="Package:").pack(side=tk.LEFT, padx=5)
        self.package_var = tk.StringVar(value="0805")
        self.package_combo = ttk.Combobox(package_frame, textvariable=self.package_var, values=list(self.package_power.keys()), width=15)
        self.package_combo.pack(side=tk.LEFT, padx=5, pady=5)
        
        calc_btn = ttk.Button(self.main_container, text="Calcola Potenza e Analizza Package", command=self.calculate_power)
        calc_btn.pack(pady=10)
        
        result_frame = ttk.LabelFrame(self.main_container, text="Analisi della Potenza e Raccomandazioni")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.power_result_text = ScrolledText(result_frame, height=15, width=60, wrap=tk.WORD)
        self.power_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def calculate_power(self):
        try:
            voltage = float(self.voltage_entry.get()) if self.voltage_entry.get() else 0
            current = float(self.current_entry.get()) if self.current_entry.get() else 0
            resistance = float(self.resistance_entry.get()) if self.resistance_entry.get() else 0
            ambient_temp = float(self.ambient_temp_entry.get()) if self.ambient_temp_entry.get() else 25
            package_name = self.package_var.get()
            package_power_val = self.package_power[package_name]

            result, error = calculate_power_logic(voltage, current, resistance, package_power_val, package_name, ambient_temp)

            if error:
                messagebox.showwarning("Attenzione", error)
            else:
                self.power_result_text.delete(1.0, tk.END)
                self.power_result_text.insert(1.0, result)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo: {str(e)}")

    # --- Metodi esistenti (invariati) ---
    def calculate_color_code(self):
        result, error = calculate_color_code_logic(self.color_codes, self.tolerance_colors, self.band1_var.get(), self.band2_var.get(), self.multiplier_var.get(), self.tolerance_var.get())
        if error: messagebox.showerror("Errore", error)
        else: 
            self.color_result_text.delete(1.0, tk.END)
            self.color_result_text.insert(1.0, result)
        self.update_resistor_drawing()

    def update_band_visibility(self):
        self.update_resistor_drawing()

    def update_resistor_drawing(self):
        try: self.res_canvas.delete('all')
        except Exception: return
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
        except Exception: band_colors = ['#000000'] * 4
        n = self.num_bands.get()
        if n == 5:
            band_positions = [80, 140, 200, 260, 320]
            try:
                mid_color = self.color_codes.get(self.band2_var.get(), ('', '#000000'))[1]
                band_colors = [self.color_codes[self.band1_var.get()][1], mid_color, self.color_codes[self.band2_var.get()][1], self.color_codes[self.multiplier_var.get()][1], self.tolerance_colors[self.tolerance_var.get()][1]]
            except Exception: band_colors = ['#000000'] * 5
        else: band_positions = [110, 170, 230, 290]
        for i, pos in enumerate(band_positions[:len(band_colors)]): self.res_canvas.create_rectangle(pos-8, 22, pos+8, 58, fill=band_colors[i], outline='')

    def find_color_code(self):
        try:
            value = float(self.value_entry.get())
            result, error = find_color_code_logic(value, self.e_series)
            if error: messagebox.showwarning("Attenzione", error)
            else: 
                self.color_result_text.delete(1.0, tk.END)
                self.color_result_text.insert(1.0, result)
        except ValueError: messagebox.showerror("Errore", "Inserisci un valore numerico valido")

    def create_series_parallel_view(self):
        input_frame = ttk.LabelFrame(self.main_container, text="1. Inserisci i Componenti Teorici")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        conn_frame = ttk.Frame(input_frame)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(conn_frame, text="Tipo connessione:").pack(side=tk.LEFT, padx=5)
        self.conn_type = tk.StringVar(value="serie")
        ttk.Radiobutton(conn_frame, text="Serie", variable=self.conn_type, value="serie").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(conn_frame, text="Parallelo", variable=self.conn_type, value="parallelo").pack(side=tk.LEFT)
        list_frame = ttk.Frame(input_frame)
        list_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(list_frame, text="Valore (Ω)    Tolleranza (%)").grid(row=0, column=0, columnspan=3, sticky=tk.W)
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
            except Exception: pass
        add_res_row('1000', '5')
        add_res_row('2200', '5')
        add_btn = ttk.Button(list_frame, text='Aggiungi Resistenza', command=lambda: add_res_row('1000', '5'))
        add_btn.grid(row=99, column=0, pady=6, sticky=tk.W)
        series_frame = ttk.LabelFrame(self.main_container, text="2. Scegli una Serie Commerciale (IEC 60063)")
        series_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(series_frame, text="Serie E:").pack(side=tk.LEFT, padx=5)
        self.series_var = tk.StringVar(value="E24")
        self.series_combo = ttk.Combobox(series_frame, textvariable=self.series_var, values=list(self.e_series.keys()), width=10)
        self.series_combo.pack(side=tk.LEFT, padx=5, pady=5)
        btn_frame = ttk.LabelFrame(self.main_container, text="3. Esegui Calcolo")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        calc_btn = ttk.Button(btn_frame, text="Calcola Equivalente Teorico", command=self.calculate_series_parallel)
        calc_btn.pack(side=tk.LEFT, padx=5)
        optimize_btn = ttk.Button(btn_frame, text="Ottimizza con Valori Commerciali", command=self.optimize_with_commercial)
        optimize_btn.pack(side=tk.LEFT, padx=5)
        result_frame = ttk.LabelFrame(self.main_container, text="Analisi e Risultati")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.series_result_text = ScrolledText(result_frame, height=12, width=60, wrap=tk.WORD)
        self.series_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.series_graph_frame = ttk.Frame(self.main_container)
        self.series_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def calculate_series_parallel(self):
        try:
            resistances = [float(rw['val'].get()) for rw in self.res_rows]
            tolerances = [float(rw['tol'].get()) for rw in self.res_rows]
            result, total_resistance, error = calculate_series_parallel_logic(resistances, tolerances, self.conn_type.get())
            if error: messagebox.showerror("Errore", error)
            else:
                self.series_result_text.delete(1.0, tk.END)
                self.series_result_text.insert(1.0, result)
                self.create_series_graph(resistances, total_resistance)
        except Exception as e: messagebox.showerror("Errore", f"Errore nel calcolo: {str(e)}")

    def optimize_with_commercial(self):
        try:
            resistances = [float(rw['val'].get()) for rw in self.res_rows]
            result, error = optimize_with_commercial_logic(resistances, self.conn_type.get(), self.series_var.get(), self.e_series)
            if error: messagebox.showwarning('Ottimizza', error)
            else: 
                self.series_result_text.delete(1.0, tk.END)
                self.series_result_text.insert(1.0, result)
        except Exception as e: messagebox.showerror("Errore", f"Errore nell'ottimizzazione: {str(e)}")

    def create_series_graph(self, resistances, total_resistance):
        for widget in self.series_graph_frame.winfo_children(): widget.destroy()
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        x_pos = range(len(resistances))
        values = [r / total_resistance * 100 for r in resistances]
        colors = ['#c44e52', '#4c72b0', '#55a868', '#ffb347', '#7f5acd']
        bars = ax.bar(x_pos, values, color=colors[:len(resistances)])
        ax.set_xlabel('Resistenze')
        ax.set_ylabel('Contributo Percentuale al Totale (%)')
        ax.set_title('Composizione della Resistenza Equivalente')
        for i, (bar, value) in enumerate(zip(bars, values)): ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{value:.1f}%', ha='center', va='bottom')
        canvas = FigureCanvasTkAgg(fig, self.series_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_monte_carlo_view(self):
        info_frame = ttk.LabelFrame(self.main_container, text="Cos'è l'Analisi Monte Carlo?")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        info_text = "L'analisi Monte Carlo è una tecnica di simulazione che prevede il comportamento di un sistema (come un circuito) tenendo conto della variazione casuale dei suoi componenti. Invece di usare solo valori nominali, esegue migliaia di calcoli usando valori che variano all'interno della tolleranza specificata, fornendo una visione statistica del comportamento reale del circuito."
        ttk.Label(info_frame, text=info_text, wraplength=1000, justify=tk.LEFT).pack(padx=5, pady=5)
        
        input_frame = ttk.LabelFrame(self.main_container, text="1. Imposta i Parametri del Circuito e della Simulazione")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        divider_frame = ttk.LabelFrame(input_frame, text="Circuito: Partitore di Tensione")
        divider_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(divider_frame, text="R1 (Ω):").grid(row=0, column=0, padx=5, pady=5)
        self.r1_entry = ttk.Entry(divider_frame, width=15)
        self.r1_entry.grid(row=0, column=1, padx=5, pady=5)
        self.r1_entry.insert(0, "1000")
        
        ttk.Label(divider_frame, text="R2 (Ω):").grid(row=0, column=2, padx=5, pady=5)
        self.r2_entry = ttk.Entry(divider_frame, width=15)
        self.r2_entry.grid(row=0, column=3, padx=5, pady=5)
        self.r2_entry.insert(0, "2200")
        
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
        
        ttk.Label(mc_frame, text="Numero Iterazioni:").grid(row=0, column=2, padx=5, pady=5)
        self.mc_iterations_entry = ttk.Entry(mc_frame, width=10)
        self.mc_iterations_entry.grid(row=0, column=3, padx=5, pady=5)
        self.mc_iterations_entry.insert(0, "5000")
        
        sim_btn = ttk.Button(input_frame, text="Esegui Simulazione e Analizza", command=self.run_monte_carlo)
        sim_btn.pack(pady=10)
        
        result_frame = ttk.LabelFrame(self.main_container, text="Analisi Statistica e Spiegazione")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.mc_result_text = ScrolledText(result_frame, height=10, width=64, wrap=tk.WORD)
        self.mc_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.mc_graph_frame = ttk.Frame(self.main_container)
        self.mc_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_monte_carlo(self):
        try:
            vin = float(self.vin_entry.get())
            iterations = int(self.mc_iterations_entry.get())
            r1_nominal, tol1, r2_nominal, tol2 = None, None, None, None
            if len(self.res_rows) >= 2:
                try: r1_nominal = float(self.res_rows[0]['val'].get()); tol1 = float(self.res_rows[0]['tol'].get()) / 100
                except Exception: pass
                try: r2_nominal = float(self.res_rows[1]['val'].get()); tol2 = float(self.res_rows[1]['tol'].get()) / 100
                except Exception: pass
            if r1_nominal is None: r1_nominal = float(self.r1_entry.get()); tol1 = float(self.mc_tolerance_entry.get()) / 100
            if r2_nominal is None: r2_nominal = float(self.r2_entry.get()); tol2 = float(self.mc_tolerance_entry.get()) / 100
            result, vout_values, vout_theoretical, error = run_monte_carlo_logic(vin, iterations, r1_nominal, tol1, r2_nominal, tol2)
            if error: messagebox.showerror("Errore", error)
            else:
                self.mc_result_text.delete(1.0, tk.END)
                self.mc_result_text.insert(1.0, result)
                self.create_mc_graph(vout_values, vout_theoretical)
        except Exception as e: messagebox.showerror("Errore", f"Errore nella simulazione: {str(e)}")

    def create_mc_graph(self, vout_values, vout_theoretical):
        for widget in self.mc_graph_frame.winfo_children(): widget.destroy()
        fig = Figure(figsize=(10, 6), dpi=100)
        ax1 = fig.add_subplot(211)
        ax1.hist(vout_values, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(vout_theoretical, color='red', linestyle='--', linewidth=2, label=f'Vout Teorico: {vout_theoretical:.3f} V')
        ax1.set_xlabel('Tensione di Uscita (Vout)')
        ax1.set_ylabel('Frequenza')
        ax1.set_title('Distribuzione di Vout (Istogramma)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax2 = fig.add_subplot(212)
        indices = range(min(100, len(vout_values)))
        ax2.scatter(indices, vout_values[:100], alpha=0.6, color='green')
        ax2.axhline(vout_theoretical, color='red', linestyle='--', linewidth=2, label='Vout Teorico')
        ax2.set_xlabel('Numero Simulazione')
        ax2.set_ylabel('Tensione di Uscita (Vout)')
        ax2.set_title('Andamento delle Prime 100 Simulazioni')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.mc_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_divider_view(self):
        input_frame = ttk.LabelFrame(self.main_container, text="1. Imposta i Parametri del Partitore di Tensione")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        params_frame = ttk.Frame(input_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(params_frame, text="Tensione di Ingresso (Vin):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.divider_vin_entry = ttk.Entry(params_frame, width=15)
        self.divider_vin_entry.grid(row=0, column=1, padx=5, pady=5)
        self.divider_vin_entry.insert(0, "12")

        ttk.Label(params_frame, text="Tensione di Uscita (Vout) Desiderata:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.divider_vout_entry = ttk.Entry(params_frame, width=15)
        self.divider_vout_entry.grid(row=1, column=1, padx=5, pady=5)
        self.divider_vout_entry.insert(0, "3.3")

        ttk.Label(params_frame, text="Serie E per Resistori:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.divider_series_var = tk.StringVar(value="E24")
        self.divider_series_combo = ttk.Combobox(params_frame, textvariable=self.divider_series_var, values=list(self.e_series.keys()), width=12)
        self.divider_series_combo.grid(row=2, column=1, padx=5, pady=5)

        calc_btn = ttk.Button(self.main_container, text="Trova Migliori Combinazioni", command=self.design_voltage_divider)
        calc_btn.pack(pady=10)

        result_frame = ttk.LabelFrame(self.main_container, text="Risultati e Combinazioni Suggerite")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.divider_result_text = ScrolledText(result_frame, height=15, width=80, wrap=tk.WORD, font=("Courier New", 9))
        self.divider_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def design_voltage_divider(self):
        try:
            vin = float(self.divider_vin_entry.get())
            vout_target = float(self.divider_vout_entry.get())
            series_name = self.divider_series_var.get()
            e_series_values = self.e_series[series_name]

            result, error = design_voltage_divider_logic(vin, vout_target, e_series_values)

            if error:
                messagebox.showerror("Errore di Progettazione", error)
            else:
                self.divider_result_text.delete(1.0, tk.END)
                self.divider_result_text.insert(1.0, result)

        except ValueError:
            messagebox.showerror("Errore", "Assicurati che Vin e Vout siano valori numerici validi.")
        except Exception as e:
            messagebox.showerror("Errore Inaspettato", f"Si è verificato un errore: {str(e)}")

    def create_led_resistor_view(self):
        led_frame = ttk.LabelFrame(self.main_container, text="Calcolatore Resistore per LED")
        led_frame.pack(fill=tk.X, padx=10, pady=10)
        params_frame = ttk.Frame(led_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(params_frame, text="Tensione Alimentazione (V):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.led_vsupply_entry = ttk.Entry(params_frame, width=15)
        self.led_vsupply_entry.grid(row=0, column=1, padx=5, pady=5)
        self.led_vsupply_entry.insert(0, "5")
        ttk.Label(params_frame, text="Tensione LED (Vf):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.led_vf_entry = ttk.Entry(params_frame, width=15)
        self.led_vf_entry.grid(row=1, column=1, padx=5, pady=5)
        self.led_vf_entry.insert(0, "2.1")
        ttk.Label(params_frame, text="Corrente LED (mA):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.led_if_entry = ttk.Entry(params_frame, width=15)
        self.led_if_entry.grid(row=2, column=1, padx=5, pady=5)
        self.led_if_entry.insert(0, "20")
        ttk.Label(params_frame, text="Serie E per Resistore:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.led_series_var = tk.StringVar(value="E24")
        self.led_series_combo = ttk.Combobox(params_frame, textvariable=self.led_series_var, values=list(self.e_series.keys()), width=12)
        self.led_series_combo.grid(row=3, column=1, padx=5, pady=5)
        
        calc_btn = ttk.Button(led_frame, text="Calcola Resistore e Package", command=self.calculate_led_resistor)
        calc_btn.pack(pady=10)
        
        result_frame = ttk.LabelFrame(self.main_container, text="Risultati e Raccomandazioni")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.led_result_text = ScrolledText(result_frame, height=15, width=80, wrap=tk.WORD)
        self.led_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_rc_filter_view(self):
        filter_frame = ttk.LabelFrame(self.main_container, text="Progettazione Filtro RC Passa-Basso")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        filter_params_frame = ttk.Frame(filter_frame)
        filter_params_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(filter_params_frame, text="Frequenza di Taglio (Hz):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.filter_fc_entry = ttk.Entry(filter_params_frame, width=15)
        self.filter_fc_entry.grid(row=0, column=1, padx=5, pady=5)
        self.filter_fc_entry.insert(0, "1000")
        ttk.Label(filter_params_frame, text="Serie E (Resistori):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.filter_r_series_var = tk.StringVar(value="E24")
        self.filter_r_series_combo = ttk.Combobox(filter_params_frame, textvariable=self.filter_r_series_var, values=list(self.e_series.keys()), width=12)
        self.filter_r_series_combo.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(filter_params_frame, text="Serie E (Condensatori):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.filter_c_series_var = tk.StringVar(value="E12")
        self.filter_c_series_combo = ttk.Combobox(filter_params_frame, textvariable=self.filter_c_series_var, values=list(self.capacitor_e_series.keys()), width=12)
        self.filter_c_series_combo.grid(row=2, column=1, padx=5, pady=5)
        
        filter_calc_btn = ttk.Button(filter_frame, text="Trova Combinazioni R/C", command=self.design_rc_filter)
        filter_calc_btn.pack(pady=10)
        
        filter_result_frame = ttk.LabelFrame(self.main_container, text="Combinazioni R/C Suggerite")
        filter_result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.filter_result_text = ScrolledText(filter_result_frame, height=15, width=80, wrap=tk.WORD, font=("Courier New", 9))
        self.filter_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def calculate_led_resistor(self):
        try:
            v_supply = float(self.led_vsupply_entry.get())
            v_led = float(self.led_vf_entry.get())
            i_led = float(self.led_if_entry.get())
            series_name = self.led_series_var.get()
            e_series_values = self.e_series[series_name]

            result, error = calculate_led_resistor_logic(v_supply, v_led, i_led, e_series_values, self.package_power)

            if error:
                messagebox.showerror("Errore di Calcolo", error)
            else:
                self.led_result_text.delete(1.0, tk.END)
                self.led_result_text.insert(1.0, result)

        except ValueError:
            messagebox.showerror("Errore", "Assicurati che tutti i campi siano valori numerici validi.")
        except Exception as e:
            messagebox.showerror("Errore Inaspettato", f"Si è verificato un errore: {str(e)}")

    def design_rc_filter(self):
        try:
            f_c_target = float(self.filter_fc_entry.get())
            r_series_name = self.filter_r_series_var.get()
            c_series_name = self.filter_c_series_var.get()

            r_series_values = self.e_series[r_series_name]
            c_series_values = self.capacitor_e_series[c_series_name]

            result, error = design_rc_filter_logic(f_c_target, r_series_values, c_series_values)

            if error:
                messagebox.showerror("Errore di Progettazione", error)
            else:
                self.filter_result_text.delete(1.0, tk.END)
                self.filter_result_text.insert(1.0, result)

        except ValueError:
            messagebox.showerror("Errore", "Assicurati che la frequenza sia un valore numerico valido.")
        except Exception as e:
            messagebox.showerror("Errore Inaspettato", f"Si è verificato un errore: {str(e)}")

    def create_regulator_view(self):
        input_frame = ttk.LabelFrame(self.main_container, text="Progettazione Regolatore di Tensione")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Regolatore:").grid(row=0, column=0, padx=5, pady=5)
        self.reg_name_var = tk.StringVar(value="LM317")
        self.reg_combo = ttk.Combobox(input_frame, textvariable=self.reg_name_var, values=list(regulator_specs.keys()), width=15)
        self.reg_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Vout Desiderata (V):").grid(row=0, column=2, padx=5, pady=5)
        self.reg_vout_entry = ttk.Entry(input_frame, width=10)
        self.reg_vout_entry.grid(row=0, column=3, padx=5, pady=5)
        self.reg_vout_entry.insert(0, "5.0")
        
        calc_btn = ttk.Button(input_frame, text="Calcola R1/R2", command=self.calculate_regulator)
        calc_btn.grid(row=0, column=4, padx=10, pady=5)
        
        result_frame = ttk.LabelFrame(self.main_container, text="Risultati")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.reg_result_text = ScrolledText(result_frame, height=15, width=80, font=("Courier New", 9))
        self.reg_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def calculate_regulator(self):
        try:
            vout = float(self.reg_vout_entry.get())
            result, error = calculate_regulator_logic(0, vout, self.reg_name_var.get(), self.e_series["E24"])
            if error: messagebox.showerror("Errore", error)
            else:
                self.reg_result_text.delete(1.0, tk.END)
                self.reg_result_text.insert(1.0, result)
        except ValueError: messagebox.showerror("Errore", "Inserisci un numero valido.")

    def create_awg_view(self):
        awg_frame = ttk.LabelFrame(self.main_container, text="Convertitore AWG / Metrico")
        awg_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(awg_frame, text="Seleziona AWG:").pack(side=tk.LEFT, padx=5, pady=10)
        self.awg_var = tk.IntVar(value=22)
        self.awg_combo = ttk.Combobox(awg_frame, textvariable=self.awg_var, values=list(awg_table.keys()), width=10)
        self.awg_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(awg_frame, text="Mostra Dati", command=self.show_awg_data).pack(side=tk.LEFT, padx=5)
        
        self.awg_result_text = ScrolledText(self.main_container, height=10, width=80)
        self.awg_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_current_divider_view(self):
        div_frame = ttk.LabelFrame(self.main_container, text="Ripartitore di Corrente")
        div_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(div_frame, text="Corrente Totale (A):").pack(side=tk.LEFT, padx=5, pady=10)
        self.div_curr_entry = ttk.Entry(div_frame, width=10)
        self.div_curr_entry.pack(side=tk.LEFT, padx=5)
        self.div_curr_entry.insert(0, "1.0")
        
        ttk.Label(div_frame, text="Resistenze (es: 100, 220):").pack(side=tk.LEFT, padx=5)
        self.div_res_entry = ttk.Entry(div_frame, width=20)
        self.div_res_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(div_frame, text="Calcola Branch", command=self.calculate_divider).pack(side=tk.LEFT, padx=5)
        
        self.div_result_text = ScrolledText(self.main_container, height=15, width=80)
        self.div_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def calculate_divider(self):
        try:
            itot = float(self.div_curr_entry.get())
            ress = [float(r.strip()) for r in self.div_res_entry.get().split(",") if r.strip()]
            res, error = calculate_current_divider_logic(itot, ress)
            if error: messagebox.showerror("Errore", error)
            else:
                self.div_result_text.delete(1.0, tk.END)
                self.div_result_text.insert(1.0, res)
        except ValueError: messagebox.showerror("Errore", "Inserisci numeri validi separati da virgola.")

    def show_awg_data(self):
        res, error = convert_awg_logic(self.awg_var.get())
        self.awg_result_text.delete(1.0, tk.END)
        self.awg_result_text.insert(1.0, res)

    def create_glossary_view(self):
        search_frame = ttk.Frame(self.main_container)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(search_frame, text="Cerca nel Glossario:").pack(side=tk.LEFT, padx=5)
        self.glossary_query = ttk.Entry(search_frame, width=30)
        self.glossary_query.pack(side=tk.LEFT, padx=5)
        self.glossary_query.bind('<KeyRelease>', lambda e: self.search_glossary())
        
        self.glossary_text = ScrolledText(self.main_container, height=25, width=80, wrap=tk.WORD)
        self.glossary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.search_glossary()

    def search_glossary(self):
        query = self.glossary_query.get()
        res = search_glossary_logic(query)
        self.glossary_text.delete(1.0, tk.END)
        self.glossary_text.insert(1.0, res)

    def update_package_info(self):
        pass
