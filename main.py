
import tkinter as tk
import traceback
from gui import ElectronicTool

def main():
    """
    Main function to initialize and run the Electronic Tool application.
    """
    try:
        root = tk.Tk()
        app = ElectronicTool(root)
        root.mainloop()
    except Exception:
        # Log any unhandled exceptions to a file for debugging
        with open('error.log', 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
        # Re-raise the exception to make it visible in the console as well
        raise

if __name__ == "__main__":
    main()