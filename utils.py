
import tkinter as tk
from tkinter import messagebox, filedialog

def format_value(value):
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
        'Guida rapida:\n\n'
        '- Codice Colori: ricava valore dalla combinazione di bande.\n'
        '- Serie/Parallelo: calcola resistenza totale e ottimizza con serie commerciali.\n'

        '- Monte Carlo: simula variazioni dovute a tolleranza componenti.\n'
        '- Potenza: valuta potenza dissipata e confronto con package.'
    )
    messagebox.showinfo('Guida rapida', help_text)

def show_about():
    about = '''Electronic Tool — v1.1 (Standard-Aware)
Autore: (tuo nome)

Questo strumento è inteso per uso didattico e di prototipazione rapida.
I calcoli si basano sui seguenti standard di riferimento:
- IEC 60062: Codici a colori e marcatura.
- IEC 60063: Serie di numeri preferiti (E-series).

Disclaimer:
I valori di potenza e le tolleranze sono indicativi. Per progetti professionali, critici o di produzione, è OBBLIGATORIO consultare i datasheet dei componenti specifici e applicare le normative di settore (es. AEC-Q200 per automotive, MIL-PRF per applicazioni militari, RoHS/REACH per i materiali). L'autore non si assume responsabilità per errori derivanti da un uso improprio dello strumento.'''
    messagebox.showinfo('Informazioni', about)

def create_menu(app):
    menubar = tk.Menu(app.root)

    # File
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label='Esporta risultato...', command=lambda: export_results(app))
    file_menu.add_separator()
    file_menu.add_command(label='Esci', command=app.root.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # Aiuto
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label='Guida rapida', command=show_quick_help)
    help_menu.add_command(label='Informazioni', command=show_about)
    menubar.add_cascade(label='Aiuto', menu=help_menu)

    app.root.config(menu=menubar)
