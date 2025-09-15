import traceback
try:
    import main
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    app = main.ElectronicTool(root)
    root.update()
    root.destroy()

    with open('diagnostic.log', 'w', encoding='utf-8') as f:
        f.write('DIAGNOSTIC: OK\n')
except Exception:
    with open('diagnostic.log', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    raise
