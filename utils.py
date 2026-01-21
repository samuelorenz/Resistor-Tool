
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
try:
    import pandas as pd
except ImportError:
    pd = None

def normalize_resistor_value(val_str):
    """Converte stringhe come '4,7Kohm', '1k2', '10ohm' in float (Ohm)."""
    if pd.isna(val_str) or not str(val_str).strip():
        return None
    s = str(val_str).lower().replace(',', '.').replace('ohm', '').strip()
    
    multiplier = 1.0
    if 'k' in s:
        multiplier = 1e3
        parts = s.split('k')
        if parts[0] and parts[1]: # 1k2 case -> 1.2k
            try:
                dec_val = float(parts[1])
                return (float(parts[0]) + dec_val / (10**len(parts[1]))) * multiplier
            except ValueError: pass
        s = s.replace('k', '')
    elif 'm' in s and 'meg' not in s: # handle M or Meg
        multiplier = 1e6
        s = s.replace('m', '')
    elif 'meg' in s:
        multiplier = 1e6
        s = s.replace('meg', '')
    
    try:
        return float(s) * multiplier
    except ValueError:
        return None

def parse_bom_excel(file_path):
    """Legge un file Excel e restituisce un set di valori Ohm unici per i resistori."""
    if not pd:
        return None, "Libreria pandas non trovata."
    try:
        # Trova header automaticamente
        df_raw = pd.read_excel(file_path, header=None, nrows=20)
        header_row = -1
        for i, row in df_raw.iterrows():
            row_values = [str(x).strip().lower() for x in row.values]
            if 'value' in row_values and 'refdes' in row_values:
                header_row = i
                break
        
        if header_row == -1:
            return None, "Formato BOM non riconosciuto (colonne 'VALUE' e 'REFDES' non trovate)."
        
        df = pd.read_excel(file_path, header=header_row)
        # Normalizziamo i nomi delle colonne per sicurezza (tutti in minuscolo)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Filtra resistori: Reference che inizia con 'r' (case-insensitive)
        res_df = df[df['refdes'].astype(str).str.upper().str.startswith('R', na=False)]
        
        values = set()
        for v in res_df['value']:
            norm_v = normalize_resistor_value(v)
            if norm_v is not None:
                values.add(norm_v)
        
        return sorted(list(values)), None
    except Exception as e:
        return None, str(e)

def import_bom(app):
    path = filedialog.askopenfilename(filetypes=[('Excel', '*.xlsx *.xls')])
    if path:
        values, error = parse_bom_excel(path)
        if error:
            messagebox.showerror("Errore BOM", error)
        else:
            app.bom_values = values
            app.bom_path.set(os.path.basename(path))
            messagebox.showinfo("BOM Caricata", f"Caricati {len(values)} valori univoci di resistenze dalla BOM.")
            if hasattr(app, 'update_bom_status'):
                app.update_bom_status()


def format_value(value, unit='Ω'):
    """Formatta il valore con il prefisso appropriato (da Giga a Micro)"""
    abs_val = abs(value)
    if abs_val >= 1e9:
        return f"{value / 1e9:.3f} G{unit}"
    if abs_val >= 1e6:
        return f"{value / 1e6:.3f} M{unit}"
    elif abs_val >= 1e3:
        return f"{value / 1e3:.3f} k{unit}"
    elif abs_val >= 1 or abs_val == 0:
        return f"{value:.3f} {unit}"
    elif abs_val >= 1e-3:
        return f"{value * 1e3:.3f} m{unit}"
    else:
        return f"{value * 1e6:.3f} µ{unit}"

def export_results(app):
    try:
        content = ''
        # raccoglie contenuti visibili
        for widget in (app.color_result_text, app.series_result_text, app.mc_result_text, app.power_result_text):
            try:
                content += widget.get(1.0, tk.END).strip() + '''\n\n'''
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
            app.status.set(f'Risultati esportati: {path}')

    except Exception as e:
        messagebox.showerror('Errore export', str(e))

def show_quick_help():
    help_text = (
        "Guida all'Apprendimento:\n\n"
        "Questo tool è progettato per essere anche uno strumento didattico. Ogni scheda ti guida attraverso un concetto chiave:\n\n"
        "- Codice Colori: Impara a decodificare le bande colorate dei resistori (IEC 60062) e a trovare i valori commerciali più vicini nelle serie standard (IEC 60063).\n\n"
        "- Serie/Parallelo: Scopri come calcolare la resistenza equivalente e come il mondo reale ti costringe a ottimizzare i tuoi progetti usando valori standard, analizzando l'impatto dell'errore introdotto.\n\n"
        "- Analisi Monte Carlo: Comprendi perché i circuiti reali non si comportano sempre come previsto. Questa simulazione ti mostra l'impatto statistico della tolleranza dei componenti sul risultato finale.\n\n"
        "- Potenza e Derating: Impara a non bruciare i tuoi componenti! Calcola la potenza dissipata e scopri perché scegliere un package adeguato, applicando un margine di sicurezza (derating), è fondamentale per l'affidabilità."
    )
    messagebox.showinfo('Guida Rapida all\'Apprendimento', help_text)

def show_about():
    about = '''Electronic Tool — v1.2 (Educational & Standard-Aware)
Autore: Samu

Questo strumento è inteso per uso didattico e di prototipazione rapida.
I calcoli si basano sui seguenti standard di riferimento:
- IEC 60062: Codici a colori e marcatura.
- IEC 60063: Serie di numeri preferiti (E-series).

Disclaimer:
I valori di potenza e le tolleranze sono indicativi. Per progetti professionali, critici o di produzione, è OBBLIGATORIO consultare i datasheet dei componenti specifici e applicare le normative di settore (es. AEC-Q200 per automotive, MIL-PRF per applicazioni militari, RoHS/REACH per i materiali). L'autore non si assume responsabilità per errori derivanti da un uso improprio dello strumento.'''
    messagebox.showinfo('Informazioni e Disclaimer', about)

def create_menu(app):
    menubar = tk.Menu(app.root)

    # File
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label='🏠 Home Dashboard', command=app.show_dashboard)
    file_menu.add_separator()
    file_menu.add_command(label='💾 Salva Progetto...', command=lambda: save_project(app))
    file_menu.add_command(label='📂 Carica Progetto...', command=lambda: load_project(app))
    file_menu.add_separator()
    file_menu.add_command(label='📥 Esporta Risultati Testo...', command=lambda: export_results(app))
    file_menu.add_separator()
    file_menu.add_command(label='❌ Esci', command=app.root.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # BOM
    bom_menu = tk.Menu(menubar, tearoff=0)
    bom_menu.add_command(label='Importa BOM Excel...', command=lambda: import_bom(app))
    bom_menu.add_checkbutton(label='Attiva Modalità BOM', variable=app.use_bom)
    bom_menu.add_separator()
    bom_menu.add_command(label='Rimuovi BOM', command=app.clear_bom)
    menubar.add_cascade(label='BOM', menu=bom_menu)

    # Calcolatori Base
    base_menu = tk.Menu(menubar, tearoff=0)
    base_menu.add_command(label='Codice Colori Resistori', command=lambda: app.show_tool("color"))
    base_menu.add_command(label='Decodifica Codici SMD', command=lambda: app.show_tool("smd"))
    menubar.add_cascade(label='Base', menu=base_menu)

    # Analisi Circuitale
    analysis_menu = tk.Menu(menubar, tearoff=0)
    analysis_menu.add_command(label='Serie e Parallelo', command=lambda: app.show_tool("series_parallel"))
    analysis_menu.add_command(label='Analisi Monte Carlo', command=lambda: app.show_tool("monte_carlo"))
    analysis_menu.add_command(label='Potenza e Derating', command=lambda: app.show_tool("power"))
    menubar.add_cascade(label='Analisi', menu=analysis_menu)

    # Progettazione
    design_menu = tk.Menu(menubar, tearoff=0)
    design_menu.add_command(label='Partitore di Tensione', command=lambda: app.show_tool("divider"))
    design_menu.add_command(label='Regolatori (LM317...)', command=lambda: app.show_tool("regulator"))
    design_menu.add_command(label='Filtri RC Passivi', command=lambda: app.show_tool("filter"))
    design_menu.add_command(label='Resistore per LED', command=lambda: app.show_tool("led"))
    menubar.add_cascade(label='Progettazione', menu=design_menu)

    # Utility
    util_menu = tk.Menu(menubar, tearoff=0)
    util_menu.add_command(label='Tabella Cavi AWG', command=lambda: app.show_tool("awg"))
    util_menu.add_command(label='Ripartitore Corrente', command=lambda: app.show_tool("curr_div"))
    util_menu.add_command(label='Glossario Tecnico', command=lambda: app.show_tool("glossary"))
    menubar.add_cascade(label='Utility', menu=util_menu)

    # Aiuto
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label='Guida Apprendimento', command=show_quick_help)
    help_menu.add_command(label='Informazioni', command=show_about)
    menubar.add_cascade(label='Aiuto', menu=help_menu)

    app.root.config(menu=menubar)

def save_project(app):
    """Salva lo stato corrente dell'applicazione in un file JSON."""
    data = {
        "color": {
            "num_bands": app.num_bands.get(),
            "band1": app.band1_var.get(),
            "band2": app.band2_var.get(),
            "multiplier": app.multiplier_var.get(),
            "tolerance": app.tolerance_var.get(),
            "target_value": app.value_entry.get()
        }
    }
    path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
    if path:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo('Salva', f'Progetto salvato in {path}')
        except Exception as e:
            messagebox.showerror('Errore Salva', str(e))

def load_project(app):
    """Carica lo stato dell'applicazione da un file JSON."""
    path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
    if not path: return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "color" in data:
            c = data["color"]
            app.num_bands.set(c.get("num_bands", 4))
            app.band1_var.set(c.get("band1", "marrone"))
            app.band2_var.set(c.get("band2", "nero"))
            app.multiplier_var.set(c.get("multiplier", "rosso"))
            app.tolerance_var.set(c.get("tolerance", "oro"))
            app.value_entry.delete(0, tk.END)
            app.value_entry.insert(0, c.get("target_value", "1000"))
            app.update_resistor_drawing()
        messagebox.showinfo('Carica', 'Progetto caricato con successo')
    except Exception as e:
        messagebox.showerror('Errore Carica', str(e))
