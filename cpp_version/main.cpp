
#include "gui.hpp"

/*
 * Punto di ingresso principale dell'applicazione C++.
 *
 * Il suo ruolo è:
 * 1. Inizializzare la libreria della GUI (es. QApplication per Qt).
 * 2. Creare un'istanza della classe principale della GUI (es. ElectronicToolGUI).
 * 3. Mostrare la finestra principale.
 * 4. Eseguire il loop degli eventi dell'applicazione.
 */

int main(int argc, char *argv[]) {
    // Esempio con Qt:
    // QApplication app(argc, argv);
    // ElectronicToolGUI window;
    // window.show();
    // return app.exec();

    // Esecuzione del segnaposto attuale:
    PlaceholderGUI gui;
    gui.run();

    return 0;
}
