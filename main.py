import sqlite3
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import QLabel
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from openpyxl import Workbook

class InwentaryzacjaApp(App):
    def build(self):
        self.title = "System Inwentaryzacji"
        
        # Inicjalizacja bazy danych (jeśli nie istnieje)
        self.inicjalizuj_baze()

        root = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Nagłówek
        self.label_info = QLabel(
            text="System Inwentaryzacji - Gotowy do pracy",
            size_hint_y=None,
            height=50
        )
        root.add_widget(self.label_info)

        # Przycisk generowania raportu Excel z zliczonych pozycji
        btn_raport = Button(
            text="Generuj raport Excel (Zliczone)",
            size_hint_y=None,
            height=60,
            background_color=(0.1, 0.6, 0.2, 1)
        )
        btn_raport.bind(on_press=self.generuj_raport_excel)
        root.add_widget(btn_raport)

        # Przycisk wyjścia
        btn_exit = Button(
            text="Wyjdź",
            size_hint_y=None,
            height=60,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        btn_exit.bind(on_press=lambda x: App.get_running_app().stop())
        root.add_widget(btn_exit)

        return root

    def inicjalizuj_baze(self):
        """Tworzy podstawową strukturę bazy, jeśli plik jeszcze nie istnieje."""
        conn = sqlite3.connect('magazyn.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produkty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT NOT NULL,
                kod TEXT,
                ilosc_poczatkowa INTEGER DEFAULT 0,
                ilosc_zliczona INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    def generuj_raport_excel(self, instance):
        """Pobiera dane z bazy i tworzy plik Excel z zliczonymi pozycjami."""
        try:
            conn = sqlite3.connect('magazyn.db')
            cursor = conn.cursor()
            
            # Pobieramy dane produktów
            cursor.execute("SELECT id, nazwa, kod, ilosc_poczatkowa, ilosc_zliczona FROM produkty")
            wiersze = cursor.fetchall()
            conn.close()

            # Tworzenie arkusza Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Raport Zliczeń"

            # Nagłówki kolumn
            naglowki = ["ID", "Nazwa Produktu", "Kod", "Stan Początkowy", "Stan Zliczony"]
            ws.append(naglowki)

            # Dodawanie danych
            for wiersz in wiersze:
                ws.append(wiersz)

            # Ustalenie ścieżki zapisu w zależności od systemu
            if platform == 'android':
                from android.storage import app_storage_path
                katalog = app_storage_path()
            else:
                katalog = "."

            nazwa_pliku = os.path.join(katalog, "raport_zliczen.xlsx")
            wb.save(nazwa_pliku)

            self.label_info.text = f"Sukces! Zapisano:\n{nazwa_pliku}"
        except Exception as e:
            self.label_info.text = f"Błąd Excela: {str(e)}"

if __name__ == '__main__':
    InwentaryzacjaApp().run()
