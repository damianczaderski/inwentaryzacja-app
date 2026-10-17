import sqlite3
import os
import shutil
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import QLabel
from kivy.utils import platform

from openpyxl import Workbook
from plyer import filechooser

class InwentaryzacjaApp(App):
    def build(self):
        self.title = "System Inwentaryzacji"
        
        # Inicjalizacja bazy danych (jeśli nie istnieje)
        self.inicjalizuj_baze()

        root = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Nagłówek informacyjny
        self.label_info = QLabel(
            text="System Inwentaryzacji - Gotowy do pracy",
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        self.label_info.bind(size=self.label_info.setter('text_size'))
        root.add_widget(self.label_info)

        # Przycisk 1: Generowanie raportu Excel
        btn_raport = Button(
            text="Generuj raport Excel (Zliczone)",
            size_hint_y=None,
            height=60,
            background_color=(0.1, 0.6, 0.2, 1)
        )
        btn_raport.bind(on_press=self.generuj_raport_excel)
        root.add_widget(btn_raport)

        # Przycisk 2: Wgrywanie / Zaczytywanie nowej bazy danych
        btn_baza = Button(
            text="Zaczytaj nową bazę (magazyn.db)",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.4, 0.8, 1)
        )
        btn_baza.bind(on_press=self.wybierz_nowa_baze)
        root.add_widget(btn_baza)

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
        if not os.path.exists('magazyn.db'):
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
            cursor.execute("SELECT id, nazwa, kod, ilosc_poczatkowa, ilosc_zliczona FROM produkty")
            wiersze = cursor.fetchall()
            conn.close()

            wb = Workbook()
            ws = wb.active
            ws.title = "Raport Zliczeń"

            naglowki = ["ID", "Nazwa Produktu", "Kod", "Stan Początkowy", "Stan Zliczony"]
            ws.append(naglowki)

            for wiersz in wiersze:
                ws.append(wiersz)

            if platform == 'android':
                from android.storage import app_storage_path
                katalog = app_storage_path()
            else:
                katalog = "."

            nazwa_pliku = os.path.join(katalog, "raport_zliczen.xlsx")
            wb.save(nazwa_pliku)

            self.label_info.text = f"Sukces! Zapisano raport:\n{nazwa_pliku}"
        except Exception as e:
            self.label_info.text = f"Błąd Excela: {str(e)}"

    def wybierz_nowa_baze(self, instance):
        """Otwiera okno wyboru pliku na urządzeniu."""
        try:
            filechooser.open_file(
                title="Wybierz nowy plik bazy (magazyn.db)",
                filters=[("Bazy danych SQLite", "*.db"), ("Wszystkie pliki", "*.*")],
                on_selection=self.zastosuj_nowa_baze
            )
        except Exception as e:
            self.label_info.text = f"Błąd otwierania pliku: {str(e)}"

    def zastosuj_nowa_baze(self, selection):
        """Kopiuje wybrany plik jako główną bazę danych aplikacji."""
        if not selection:
            return
        
        try:
            sciezka_zrodlowa = selection[0]
            
            if platform == 'android':
                from android.storage import app_storage_path
                katalog_docelowy = app_storage_path()
            else:
                katalog_docelowy = "."

            sciezka_docelowa = os.path.join(katalog_docelowy, "magazyn.db")

            # Kopiujemy wybrany plik w miejsce bazy aplikacji
            shutil.copyfile(sciezka_zrodlowa, sciezka_docelowa)
            self.label_info.text = "Sukces! Zaciągnięto nową bazę danych."
        except Exception as e:
            self.label_info.text = f"Błąd podmiany bazy: {str(e)}"

if __name__ == '__main__':
    InwentaryzacjaApp().run()
