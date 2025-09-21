
#pragma once

#include <string>
#include <vector>

// Dichiarazioni delle funzioni di logica che verranno implementate in logic.cpp

namespace Logic {

    // Calcola il valore di un resistore dal suo codice colori
    std::string calculate_color_code_logic(
        const std::string& band1, 
        const std::string& band2, 
        const std::string& multiplier, 
        const std::string& tolerance
    );

    // Trova il valore commerciale più vicino e restituisce la spiegazione
    std::string find_color_code_logic(double target_value);

    // Calcola la resistenza equivalente per connessioni in serie o parallelo
    std::string calculate_series_parallel_logic(
        const std::vector<double>& resistances,
        const std::vector<double>& tolerances,
        const std::string& conn_type
    );

    // Ottimizza una lista di resistori con la serie commerciale specificata
    std::string optimize_with_commercial_logic(
        const std::vector<double>& resistances,
        const std::string& conn_type,
        const std::string& series_name
    );

    // Esegue una simulazione Monte Carlo su un partitore di tensione
    std::string run_monte_carlo_logic(
        double vin,
        int iterations,
        double r1_nominal,
        double tol1_percent,
        double r2_nominal,
        double tol2_percent,
        std::vector<double>& vout_values // Parametro di output per i dati del grafico
    );

    // Calcola la potenza dissipata e valuta il package
    std::string calculate_power_logic(
        double voltage,
        double current,
        double resistance,
        const std::string& package_name
    );

} // namespace Logic
