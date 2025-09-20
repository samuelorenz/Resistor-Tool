
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
    file_menu.add_command(label='Esporta Risultati...', command=lambda: export_results(app))
    file_menu.add_separator()
    file_menu.add_command(label='Esci', command=app.root.quit)
    menubar.add_cascade(label='File', menu=file_menu)

    # Aiuto
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label='Guida all\'Apprendimento', command=show_quick_help)
    help_menu.add_command(label='Informazioni e Disclaimer', command=show_about)
    menubar.add_cascade(label='Aiuto', menu=help_menu)

    app.root.config(menu=menubar)
