import sqlite3
import os

db_path = 'magazyn.db'
output_file = 'raport_remanent.xls'

if not os.path.exists(db_path):
    print("Błąd: Brak pliku magazyn.db!")
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
        
        html = '<html xmlns:x="urn:schemas-microsoft-com:office:excel"><head><meta charset="UTF-8"></head><body><table border="1">'
        html += '<tr><th>Indeks</th><th>Kod Produktu</th><th>Nazwa Towaru</th><th>Stan Systemowy</th><th>Zliczona Ilość</th><th>Lokalizacja</th></tr>'
        
        for row in rows:
            html += '<tr>'
            for cell in row:
                html += f'<td>{cell}</td>'
            html += '</tr>'
            
        html += '</table></body></html>'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Sukces! Plik Excel zapisany jako: {output_file}")
        
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        conn.close()
