
# Electronic Tool — Analisi e Didattica sulle Resistenze

Questo software è uno strumento multifunzione progettato per studenti, hobbisti e professionisti dell'elettronica. Il suo scopo è duplice:

1.  **Fornire Calcoli Rapidi e Affidabili**: Esegue calcoli comuni legati ai resistori, come la decodifica dei codici a colori, il calcolo di reti serie/parallelo e l'analisi di potenza.
2.  **Essere uno Strumento Didattico**: Ogni funzionalità è progettata non solo per dare un risultato, ma per *spiegare* i concetti sottostanti, le formule utilizzate e le considerazioni pratiche del mondo reale.

L'applicazione si basa sugli standard internazionali **IEC 60062** (codici a colori) e **IEC 60063** (serie di valori standard E).

---

## Funzionalità Principali

L'interfaccia è suddivisa in quattro schede, ognuna dedicata a un'area specifica dell'analisi dei resistori.

### 1. Codice Colori

Questa scheda permette di esplorare la relazione tra i valori di resistenza e il codice a bande colorate.

-   **Decodifica da Colori a Valore**: Seleziona i colori delle bande di un resistore (a 4 o 5 bande) per calcolarne il valore nominale, la tolleranza e il range di funzionamento (min/max).
-   **Ricerca da Valore a Colori**: Inserisci un valore di resistenza teorico e lo strumento troverà il **valore commerciale più vicino** disponibile nelle serie standard (da E3 a E192), mostrando il codice a colori corrispondente e l'errore percentuale introdotto.

### 2. Serie/Parallelo

Questa sezione aiuta a progettare e analizzare reti di resistori.

-   **Calcolo Equivalente Teorico**: Inserisci una lista di resistori con le loro tolleranze e calcola la resistenza totale per una connessione in serie o in parallelo.
-   **Ottimizzazione con Valori Commerciali**: Lo strumento sostituisce ogni resistore teorico con il valore standard più vicino della serie E selezionata (E3-E192), calcolando la nuova resistenza equivalente e mostrando l'errore totale rispetto al progetto ideale. Questo illustra una delle sfide più comuni nella progettazione elettronica.

### 3. Analisi Monte Carlo

Questa è una potente funzionalità didattica che mostra perché i circuiti reali non si comportano sempre come previsto sulla carta.

-   **Simulazione di un Partitore di Tensione**: Imposta i valori nominali di R1 e R2, la tensione di ingresso (Vin) e la tolleranza dei componenti.
-   **Analisi Statistica**: Il software esegue migliaia di simulazioni, variando casualmente i valori dei resistori all'interno della loro tolleranza. Il risultato è un'analisi statistica della tensione di uscita (Vout), che include:
    -   Valore medio, minimo e massimo.
    -   Deviazione standard (σ).
    -   Un istogramma che visualizza la distribuzione dei possibili valori di Vout.

Questo dimostra in modo pratico come la tolleranza dei componenti influenzi l'affidabilità e la precisione di un circuito.

### 4. Potenza e Derating

Questa scheda affronta un aspetto critico della progettazione: la gestione della potenza per evitare guasti.

-   **Calcolo della Potenza Dissipata**: Inserendo due tra Tensione, Corrente e Resistenza, il tool calcola la potenza (in Watt) che il resistore dissiperà, mostrando le formule della legge di Ohm utilizzate.
-   **Analisi del Package e Derating**: Selezionando un package SMD o through-hole, lo strumento confronta la potenza dissipata con la potenza massima del componente e fornisce una raccomandazione basata su un **fattore di sicurezza**.
-   **Spiegazione del Derating**: Una sezione didattica spiega perché è fondamentale scegliere componenti con una potenza nominale superiore a quella richiesta (es. il doppio), una pratica nota come *derating*, essenziale per garantire l'affidabilità a lungo termine, specialmente in applicazioni professionali (es. **AEC-Q200** per l'automotive).

---

## Struttura del Progetto

Il codice è stato modularizzato per chiarezza e manutenibilità:

-   `main.py`: Punto di ingresso dell'applicazione. Avvia l'interfaccia grafica.
-   `gui.py`: Contiene la classe `ElectronicTool` che costruisce e gestisce l'intera interfaccia utente (finestre, tab, pulsanti) usando Tkinter.
-   `logic.py`: È il "cervello" del software. Contiene tutte le funzioni di calcolo e, soprattutto, la logica che genera le **spiegazioni didattiche**.
-   `utils.py`: Funzioni di utilità, come la formattazione dei valori (es. da 1000 a 1 kΩ), la creazione del menu e le finestre di dialogo "Informazioni" e "Guida Rapida".
-   `resistor_lib.py`: Una libreria di costanti che contiene i dati di base:
    -   I valori per le serie **E3, E6, E12, E24, E48, E96, E192** (IEC 60063).
    -   I codici colore per valori e tolleranze (IEC 60062).
    -   Le potenze nominali indicative per i package più comuni.

---

## Come Avviare il Software

1.  Assicurati di avere Python installato sul tuo sistema.
2.  Installa le dipendenze necessarie:
    ```
    pip install numpy matplotlib
    ```
3.  Esegui il programma dal terminale, posizionandoti nella cartella principale del progetto:
    ```
    python main.py
    ```

---

## Disclaimer

Questo strumento è stato creato per scopi didattici e di prototipazione rapida. Sebbene i calcoli siano basati su standard industriali, i valori (specialmente quelli di potenza) sono indicativi. Per progetti professionali, critici o destinati alla produzione, è **obbligatorio** consultare i datasheet ufficiali dei produttori e applicare rigorosamente le normative di settore (AEC, MIL, RoHS, ecc.). L'autore non si assume alcuna responsabilità per danni o guasti derivanti da un uso improprio del software.
