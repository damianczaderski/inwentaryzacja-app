import sqlite3
import csv
import os

db_path = 'magazyn.db'
output_file = 'raport_remanent.csv'

if not os.path.exists(db_path):
    print(f"Błąd: Brak pliku bazy danych {db_path}!")
else:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                r.indeks AS Indeks,
                p.kod_produktu AS Kod_Produktu,
                p.nazwa AS Nazwa_Towaru,
                p.stan_systemowy AS Stan_Systemowy,
                r.ilosc AS Zliczona_Ilosc,
                r.lokalizacja AS Lokalizacja
            FROM remanent r
            JOIN produkty p ON r.indeks = p.indeks
        """)
        rows = cur.fetchall()
        
        # Zapis do pliku CSV (używamy kodowania utf-8-sig, żeby polskie znaki idealnie wyświetlały się w Excelu, a jako separatora średnika)
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            # Nagłówki kolumn
            writer.writerow(['Indeks', 'Kod Produktu', 'Nazwa Towaru', 'Stan Systemowy', 'Zliczona Ilość', 'Lokalizacja'])
            # Wiersze z danymi
            writer.writerows(rows)
            
        print(f"Sukces! Wygenerowano plik: {output_file}")
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        
    finally:
        conn.close()
