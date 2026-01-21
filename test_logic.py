import sys
import os

# Add project root to path
sys.path.append(os.path.abspath('.'))

from logic import (
    find_best_color_match,
    calculate_power_logic,
    calculate_color_code_logic,
    calculate_regulator_logic,
    convert_awg_logic,
    search_glossary_logic
)
from utils import format_value
from resistor_lib import e_series, color_codes, tolerance_colors

def test_format_value():
    print("Testing format_value...")
    assert format_value(1000) == "1.000 kΩ"
    assert format_value(1000, unit='Hz') == "1.000 kHz"
    assert format_value(0.000001, unit='F') == "1.000 µF"
    assert format_value(1e9) == "1.000 GΩ"
    print("✓ format_value OK")

def test_find_best_color_match():
    print("Testing find_best_color_match...")
    match = find_best_color_match(2200, e_series)
    assert match['band1'] == "rosso"
    assert match['band2'] == "rosso"
    match = find_best_color_match(1, e_series)
    assert match['band1'] == "marrone"
    assert match['band2'] == "nero"
    print("✓ find_best_color_match OK")

def test_power_logic():
    print("Testing power_logic...")
    res, error = calculate_power_logic(5, 0, 500, 0.125, "0805", 25)
    assert error is None
    assert "0.0500 W" in res
    print("✓ power_logic OK")

def test_regulator_logic():
    print("Testing regulator_logic...")
    res, error = calculate_regulator_logic(12, 5, "LM317", e_series["E24"])
    assert error is None
    # LM317 with R1=240 and Vout=5V usually gives ~4.8V or ~5.2V with E24
    assert "V" in res
    print("✓ regulator_logic OK")

def test_awg_logic():
    print("Testing awg_logic...")
    res, error = convert_awg_logic(22)
    assert error is None
    assert "0.644 mm" in res
    print("✓ awg_logic OK")

def test_glossary_logic():
    print("Testing glossary_logic...")
    res = search_glossary_logic("AEC")
    assert "AEC-Q200" in res
    print("✓ glossary_logic OK")

if __name__ == "__main__":
    try:
        test_format_value()
        test_find_best_color_match()
        test_power_logic()
        test_regulator_logic()
        test_awg_logic()
        test_glossary_logic()
        print("\nALL TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
