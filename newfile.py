import sqlite3, os, traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard

class ListaPozycjiRow(BoxLayout):
    def __init__(self, indeks, kod_produktu, stan_systemowy, ilosc, lokalizacja, parent_app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        # Zwiększona wysokość wiersza (dp(72)), aby obie linijki opisu mieściły się idealnie
        self.size_hint_y, self.height, self.spacing = None, dp(72), dp(4)
        self.indeks, self.lokalizacja, self.parent_app = indeks, lokalizacja, parent_app
        
        opis_text = f"{indeks} | {kod_produktu}\nStan: {int(stan_systemowy)}"
        # Przywrócona optymalna szerokość opisu (0.52), żeby tekst nie był śśiśnięty
        self.opis_label = Label(text=opis_text, font_size=sp(11), halign='left', valign='middle', size_hint_x=0.52)
        self.opis_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        self.add_widget(self.opis_label)
        
        btn_kopiuj = Button(text="KOPY", font_size=sp(11), bold=True, background_color=(0.3, 0.3, 0.6, 1), size_hint_x=0.15)
        btn_kopiuj.bind(on_press=lambda inst: Clipboard.copy(str(indeks)))
        self.add_widget(btn_kopiuj)
        
        # Wygodne pole ilości z czytelną czcionką
        self.ilosc_input = TextInput(text=ilosc, multiline=False, input_filter='float', font_size=sp(16), halign='center', size_hint_x=0.18)
        self.add_widget(self.ilosc_input)
        
        btn_zmien = Button(text="Z", font_size=sp(12), background_color=(0.1, 0.5, 0.1, 1), size_hint_x=0.08)
        btn_zmien.bind(on_press=self.potwierdz_zczytaj_zmiane)
        self.add_widget(btn_zmien)
        
        btn_usun = Button(text="X", font_size=sp(15), bold=True, background_color=(0.7, 0.1, 0.1, 1), size_hint_x=0.07)
        btn_usun.bind(on_press=self.potwierdz_usun)
        self.add_widget(btn_usun)

    def potwierdz_zczytaj_zmiane(self, instance):
        try: nw = float(self.ilosc_input.text.strip())
        except ValueError: return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        popup = Popup(title='Potwierdź zmianę', content=content, size_hint=(0.85, 0.45))
        
        ilosc_fmt = int(nw) if nw.is_integer() else nw
        msg = f"Czy na pewno chcesz zmienić ilość?\n\nIndeks: {self.indeks}\nNowa ilość: {ilosc_fmt}\nLokalizacja: {self.lokalizacja}"
        content.add_widget(Label(text=msg, font_size=sp(14), halign='center', valign='middle'))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        btn_ok = Button(text="OK", background_color=(0.1, 0.5, 0.1, 1), bold=True)
        btn_cofnij = Button(text="COFAJ", background_color=(0.5, 0.1, 0.1, 1), bold=True)
        
        btn_ok.bind(on_press=lambda inst: [popup.dismiss(), self.wykonaj_zmien_ilosc(nw)])
        btn_cofnij.bind(on_press=popup.dismiss)
        
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cofnij)
        content.add_widget(btn_box)
        popup.open()

    def wykonaj_zmien_ilosc(self, nw):
        conn = sqlite3.connect(self.parent_app.db_path)
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM remanent WHERE indeks=? AND lokalizacja=?", (self.indeks, self.lokalizacja))
            cur.execute("INSERT INTO remanent (indeks, ilosc, lokalizacja) VALUES (?, ?, ?)", (self.indeks, nw, self.lokalizacja))
            conn.commit()
        finally: conn.close()
        self.parent_app.odswiez_liste_edycji(self.lokalizacja)

    def potwierdz_usun(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        popup = Popup(title='Potwierdź usunięcie', content=content, size_hint=(0.85, 0.45))
        
        msg = f"Czy na pewno usunąć tę pozycję?\n\nIndeks: {self.indeks}\nLokalizacja: {self.lokalizacja}"
        content.add_widget(Label(text=msg, font_size=sp(14), halign='center', valign='middle'))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        btn_ok = Button(text="OK", background_color=(0.7, 0.1, 0.1, 1), bold=True)
        btn_cofnij = Button(text="COFAJ", background_color=(0.3, 0.3, 0.3, 1), bold=True)
        
        btn_ok.bind(on_press=lambda inst: [popup.dismiss(), self.wykonaj_usun()])
        btn_cofnij.bind(on_press=popup.dismiss)
        
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cofnij)
        content.add_widget(btn_box)
        popup.open()

    def wykonaj_usun(self):
        conn = sqlite3.connect(self.parent_app.db_path)
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM remanent WHERE indeks=? AND lokalizacja=?", (self.indeks, self.lokalizacja))
            conn.commit()
        finally: conn.close()
        self.parent_app.odswiez_liste_edycji(self.lokalizacja)

class InwentaryzacjaApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding, self.spacing = dp(8), dp(6)
        
        base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.'
        self.db_path = os.path.join(base_dir, 'magazyn.db')
        self.inicjalizuj_baze()

        self.aktualny_indeks, self.aktualna_nazwa, self.stan_systemowy, self.kod_produktu = "", "", 0.0, ""

        self.add_widget(Label(text="LOKALIZACJA:", font_size=sp(14), bold=True, size_hint_y=None, height=dp(20)))
        self.lokalizacja_input = TextInput(multiline=False, font_size=sp(18), size_hint_y=None, height=dp(40), halign='center')
        self.add_widget(self.lokalizacja_input)

        self.add_widget(Label(text="SKANUJ / WPISZ KOD LUB INDEKS:", font_size=sp(14), bold=True, size_hint_y=None, height=dp(20)))
        self.kod_input = TextInput(multiline=False, font_size=sp(20), size_hint_y=None, height=dp(45))
        self.kod_input.bind(on_text_validate=self.wyszukaj_produkt)
        self.add_widget(self.kod_input)

        self.info_label = Label(text="OCZEKIWANIE NA KOD...", font_size=sp(15), halign='center', valign='middle', size_hint_y=1, color=(0.7, 0.7, 0.7, 1))
        self.info_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - dp(20), None)))
        self.add_widget(self.info_label)

        self.kopuj_glowny_btn = Button(text="SKOPIUJ INDEKS (KOPY)", font_size=sp(14), bold=True, background_color=(0.3, 0.3, 0.6, 1), size_hint_y=None, height=dp(40))
        self.kopuj_glowny_btn.bind(on_press=lambda inst: Clipboard.copy(str(self.aktualny_indeks)) if self.aktualny_indeks else None)
        self.add_widget(self.kopuj_glowny_btn)

        self.add_widget(Label(text="PODAJ ILOŚĆ:", font_size=sp(14), bold=True, size_hint_y=None, height=dp(20)))
        self.ilosc_input = TextInput(text="1", multiline=False, input_filter='float', font_size=sp(20), halign='center', size_hint_y=None, height=dp(45))
        self.ilosc_input.bind(on_text_validate=self.potwierdz_zapisz_do_bazy)
        self.add_widget(self.ilosc_input)

        self.zapisz_btn = Button(text="ZAPISZ POZYCJĘ (ENTER)", font_size=sp(16), bold=True, background_color=(0.1, 0.4, 0.1, 1), size_hint_y=None, height=dp(50), disabled=True)
        self.zapisz_btn.bind(on_press=self.potwierdz_zapisz_do_bazy)
        self.add_widget(self.zapisz_btn)

        edycja_btn = Button(text="PRZEGLĄDAJ / EDYTUJ LOKALIZACJĘ", font_size=sp(14), bold=True, background_color=(0.2, 0.2, 0.4, 1), size_hint_y=None, height=dp(40))
        edycja_btn.bind(on_press=self.otworz_panel_edycji)
        self.add_widget(edycja_btn)

        towar_btn = Button(text="PRZEGLĄDAJ STAN TOWARU", font_size=sp(14), bold=True, background_color=(0.4, 0.2, 0.4, 1), size_hint_y=None, height=dp(40))
        towar_btn.bind(on_press=self.otworz_panel_towaru)
        self.add_widget(towar_btn)

    def inicjalizuj_baze(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS produkty (indeks TEXT, kod_produktu TEXT, kod_kreskowy TEXT, nazwa TEXT, stan_systemowy INTEGER)")
            cur.execute("CREATE TABLE IF NOT EXISTS remanent (indeks TEXT, ilosc REAL, lokalizacja TEXT)")
            conn.commit()
        finally:
            conn.close()
    def wyszukaj_produkt(self, instance):
        szukany = self.kod_input.text.strip()
        if not szukany: return
        fraza = f"%{szukany}%"
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT indeks, nazwa, stan_systemowy, kod_produktu 
                FROM produkty 
                WHERE LOWER(kod_kreskowy) LIKE LOWER(?) 
                   OR LOWER(indeks) LIKE LOWER(?) 
                   OR LOWER(kod_produktu) LIKE LOWER(?) 
                   OR LOWER(nazwa) LIKE LOWER(?)
                ORDER BY stan_systemowy DESC
            """, (fraza, fraza, fraza, fraza))
            wyniki = cur.fetchall()
        finally: 
            conn.close()
            
        if not wyniki:
            self.info_label.text = f"[b]BŁĄD: Brak pasujących rekordów[/b]"
            self.aktualny_indeks = ""
            self.zapisz_btn.disabled = True
            return
            
        self.otworz_okno_duplikatow(wyniki)

    def zaladuj_produkt_do_interfejsu(self, p):
        self.aktualny_indeks, self.aktualna_nazwa, self.stan_systemowy, self.kod_produktu = p
        self.zapisz_btn.disabled = False
        self.odswiez_wyswietlacz()
        self.ilosc_input.focus = True
        self.ilosc_input.select_all()

    def odswiez_wyswietlacz(self):
        lok = self.lokalizacja_input.text.strip() or "[NIE PODANO]"
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT SUM(ilosc) FROM remanent WHERE indeks=? AND lokalizacja=?", (self.aktualny_indeks, lok))
            r_lok = cur.fetchone()[0] or 0.0
            cur.execute("SELECT SUM(ilosc) FROM remanent WHERE indeks=?", (self.aktualny_indeks,))
            r_mag = cur.fetchone()[0] or 0.0
        finally: conn.close()
        
        r_lok_fmt = int(r_lok) if r_lok.is_integer() else r_lok
        r_mag_fmt = int(r_mag) if r_mag.is_integer() else r_mag
        stan_sys_fmt = int(self.stan_systemowy)
        
        st = f"Zliczono: {r_mag_fmt} z {stan_sys_fmt}"
        col = f"[color=#00FF00]{st} (ZGODNY)[/color]" if r_mag == self.stan_systemowy else (f"[color=#FF3333]{st} (NADWYŻKA!)[/color]" if r_mag > self.stan_systemowy else f"[color=#AAAAAA]{st} (W TRAKCIE)[/color]")
        self.info_label.markup = True
        self.info_label.text = f"[b][color=#55FFFF]>> ZNALEZIONO <<[/color][/b]\n\nIndeks: {self.aktualny_indeks}\nKod: {self.kod_produktu}\nNazwa: {self.aktualna_nazwa}\nLokalizacja {lok}: {r_lok_fmt}\nStan ogólny: {col}"

    def potwierdz_zapisz_do_bazy(self, instance):
        if self.zapisz_btn.disabled or not self.aktualny_indeks: return
        lok = self.lokalizacja_input.text.strip()
        if not lok:
            self.info_label.text = "[b][color=#FF3333]BŁĄD: Podaj lokalizację![/color][/b]"
            return
        try: ilosc = float(self.ilosc_input.text.strip())
        except ValueError: return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        popup = Popup(title='Potwierdź zapis pozycji', content=content, size_hint=(0.85, 0.45))
        
        ilosc_fmt = int(ilosc) if ilosc.is_integer() else ilosc
        msg = f"Zapisać pozycję?\n\nIndeks: {self.aktualny_indeks}\nIlość: {ilosc_fmt}\nLokalizacja: {lok}"
        content.add_widget(Label(text=msg, font_size=sp(14), halign='center', valign='middle'))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        btn_ok = Button(text="OK", background_color=(0.1, 0.5, 0.1, 1), bold=True)
        btn_cofnij = Button(text="COFAJ", background_color=(0.5, 0.1, 0.1, 1), bold=True)
        
        btn_ok.bind(on_press=lambda inst: [popup.dismiss(), self.wykonaj_zapisz_do_bazy(ilosc, lok)])
        btn_cofnij.bind(on_press=popup.dismiss)
        
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cofnij)
        content.add_widget(btn_box)
        popup.open()

    def wykonaj_zapisz_do_bazy(self, ilosc, lok):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO remanent (indeks, ilosc, lokalizacja) VALUES (?, ?, ?)", (self.aktualny_indeks, ilosc, lok))
            conn.commit()
        finally: conn.close()
        self.odswiez_wyswietlacz()
        self.kod_input.text, self.ilosc_input.text = "", "1"
        self.kod_input.focus = True

    def otworz_okno_duplikatow(self, wyniki):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        popup = Popup(title='Wybierz towar z listy (wg stanu):', content=content, size_hint=(0.98, 0.85))
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        content.add_widget(scroll)

        for p in wyniki:
            ind, naz, stan, kod_p = p
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(65), spacing=dp(5))
            
            opis_label = Label(text=f"{ind} | {kod_p}\nStan: {int(stan)}", font_size=sp(11), halign='left', valign='middle', size_hint_x=0.55)
            opis_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
            row.add_widget(opis_label)
            
            btn_kopiuj = Button(text="KOPY", font_size=sp(11), bold=True, background_color=(0.3, 0.3, 0.6, 1), size_hint_x=0.17)
            btn_kopiuj.bind(on_press=lambda inst, i=ind: Clipboard.copy(str(i)))
            row.add_widget(btn_kopiuj)
            
            btn_wybierz = Button(text="WYB.", font_size=sp(11), bold=True, background_color=(0.1, 0.4, 0.1, 1), size_hint_x=0.28)
            btn_wybierz.bind(on_press=lambda inst, prod=p: [self.zaladuj_produkt_do_interfejsu(prod), popup.dismiss()])
            row.add_widget(btn_wybierz)
            
            layout.add_widget(row)
            
        zam = Button(text="ANULUJ", size_hint_y=None, height=dp(45), background_color=(0.5, 0.1, 0.1, 1))
        zam.bind(on_press=popup.dismiss)
        content.add_widget(zam)
        popup.open()

    def otworz_panel_edycji(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text="Wyszukaj lokalizację:", size_hint_y=None, height=dp(25)))
        lok_input = TextInput(multiline=False, font_size=sp(18), size_hint_y=None, height=dp(45), halign='center')
        content.add_widget(lok_input)
        
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        content.add_widget(scroll)
        
        popup = Popup(title='Wybierz lokalizację', content=content, size_hint=(0.95, 0.85))
        
        def zal_lok(filtr=""):
            layout.clear_widgets()
            conn = sqlite3.connect(self.db_path)
            try:
                cur = conn.cursor()
                if filtr: 
                    cur.execute("SELECT DISTINCT lokalizacja FROM remanent WHERE lokalizacja LIKE ? ORDER BY lokalizacja", (f"%{filtr}%",))
                else: 
                    cur.execute("SELECT DISTINCT lokalizacja FROM remanent ORDER BY lokalizacja")
                lokacje = cur.fetchall()
            finally: 
                conn.close()
            
            for (lok,) in lokacje:
                btn = Button(text=lok, size_hint_y=None, height=dp(50), background_color=(0.2, 0.3, 0.4, 1))
                btn.bind(on_press=lambda inst, l=lok: [popup.dismiss(), self.pokaz_edycje_dla_lokalizacji(l)])
                layout.add_widget(btn)

        lok_input.bind(on_text_validate=lambda inst: zal_lok(lok_input.text.strip()))
        sz_btn = Button(text="SZUKAJ", size_hint_y=None, height=dp(40), background_color=(0.1, 0.4, 0.6, 1))
        sz_btn.bind(on_press=lambda inst: zal_lok(lok_input.text.strip()))
        content.add_widget(sz_btn)
        
        zam = Button(text="ANULUJ", size_hint_y=None, height=dp(45), background_color=(0.5, 0.1, 0.1, 1))
        zam.bind(on_press=popup.dismiss)
        content.add_widget(zam)
        
        zal_lok()
        popup.open()

    def pokaz_edycje_dla_lokalizacji(self, lok):
        self.lokalizacja_input.text = lok
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        self.lista_view = ScrollView(size_hint=(1, 1))
        self.lista_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.lista_view.add_widget(self.lista_layout)
        content.add_widget(Label(text=f"Lokalizacja: {lok}", font_size=sp(18), size_hint_y=None, height=dp(25)))
        content.add_widget(self.lista_view)
        popup = Popup(title=f'Edycja: {lok}', content=content, size_hint=(0.98, 0.95))
        self.odswiez_liste_edycji(lok)
        pow = Button(text="POWRÓT", size_hint_y=None, height=dp(50), background_color=(0.3, 0.3, 0.3, 1))
        pow.bind(on_press=lambda inst: [popup.dismiss(), self.odswiez_wyswietlacz() if self.aktualny_indeks else None])
        content.add_widget(pow)
        popup.open()

    def odswiez_liste_edycji(self, lok):
        self.lista_layout.clear_widgets()
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.indeks, p.kod_produktu, p.stan_systemowy, SUM(r.ilosc) 
                FROM remanent r JOIN produkty p ON r.indeks=p.indeks 
                WHERE r.lokalizacja=? GROUP BY r.indeks
            """, (lok,))
            wpisy = cur.fetchall()
        finally: conn.close()
        for ind, kod_p, stan_sys, il in wpisy:
            il_val = int(il) if il.is_integer() else il
            self.lista_layout.add_widget(ListaPozycjiRow(indeks=ind, kod_produktu=kod_p, stan_systemowy=stan_sys, ilosc=str(il_val), lokalizacja=lok, parent_app=self))

    def otworz_panel_towaru(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text="Szukaj towaru:", size_hint_y=None, height=dp(25)))
        sz_input = TextInput(multiline=False, font_size=sp(18), size_hint_y=None, height=dp(45), halign='center')
        content.add_widget(sz_input)
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        content.add_widget(scroll)
        popup = Popup(title='Stan towaru', content=content, size_hint=(0.95, 0.85))
        
        def szukaj_prod(inst):
            layout.clear_widgets()
            fraza = sz_input.text.strip()
            if not fraza: return
            f_like = f"%{fraza}%"
            conn = sqlite3.connect(self.db_path)
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT indeks, nazwa, stan_systemowy, kod_produktu 
                    FROM produkty 
                    WHERE indeks LIKE ? OR nazwa LIKE ? OR kod_kreskowy LIKE ? OR kod_produktu LIKE ?
                    ORDER BY stan_systemowy DESC
                """, (f_like, f_like, f_like, f_like))
                wyniki = cur.fetchall()
            finally: conn.close()
            for p in wyniki:
                ind, naz, stan, kod_p = p
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(65), spacing=dp(5))
                
                opis_label = Label(text=f"{ind} | {kod_p}\nStan: {int(stan)}", font_size=sp(11), halign='left', valign='middle', size_hint_x=0.55)
                opis_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
                row.add_widget(opis_label)
                
                btn_kopiuj = Button(text="KOPY", font_size=sp(11), bold=True, background_color=(0.3, 0.3, 0.6, 1), size_hint_x=0.17)
                btn_kopiuj.bind(on_press=lambda inst, i=ind: Clipboard.copy(str(i)))
                row.add_widget(btn_kopiuj)
                
                btn_wybierz = Button(text="WYB.", font_size=sp(11), bold=True, background_color=(0.1, 0.4, 0.1, 1), size_hint_x=0.28)
                btn_wybierz.bind(on_press=lambda inst, prod=p: [popup.dismiss(), self.pokaz_szczegoly_towaru(prod)])
                row.add_widget(btn_wybierz)
                
                layout.add_widget(row)

        sz_input.bind(on_text_validate=szukaj_prod)
        sz_btn = Button(text="SZUKAJ", size_hint_y=None, height=dp(40), background_color=(0.1, 0.4, 0.6, 1))
        sz_btn.bind(on_press=szukaj_prod)
        content.add_widget(sz_btn)
        zam = Button(text="ANULUJ", size_hint_y=None, height=dp(45), background_color=(0.5, 0.1, 0.1, 1))
        zam.bind(on_press=popup.dismiss)
        content.add_widget(zam)
        popup.open()

    def pokaz_szczegoly_towaru(self, p):
        ind, naz, stan_sys, kod_p = p
        self.zaladuj_produkt_do_interfejsu(p)
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT SUM(ilosc) FROM remanent WHERE indeks=?", (ind,))
            w_mag = cur.fetchone()[0] or 0.0
            cur.execute("SELECT lokalizacja, SUM(ilosc) FROM remanent WHERE indeks=? GROUP BY lokalizacja", (ind,))
            lokalizacje = cur.fetchall()
        finally: conn.close()

        w_mag_fmt = int(w_mag) if w_mag.is_integer() else w_mag
        st = f"Zliczono ogółem: {w_mag_fmt} z {int(stan_sys)}"
        col = f"[color=#00FF00]{st} (ZGODNY)[/color]" if w_mag == stan_sys else (f"[color=#FF3333]{st} (NADWYŻKA!)[/color]" if w_mag > stan_sys else f"[color=#AAAAAA]{st} (W TRAKCIE)[/color]")

        content.add_widget(Label(text=f"[b]Indeks:[/b] {ind}\n[b]Kod:[/b] {kod_p}\n[b]Nazwa:[/b] {naz}\n{col}", font_size=sp(15), markup=True, size_hint_y=None, height=dp(95), halign='center'))
        content.add_widget(Label(text="--- Rozbicie na lokalizacje ---", size_hint_y=None, height=dp(25), color=(0.8, 0.8, 0.8, 1)))
        
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        content.add_widget(scroll)
        
        for lok, il in lokalizacje:
            il_lok_fmt = int(il) if il.is_integer() else il
            rb = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
            rb.add_widget(Label(text=f"Regał: {lok}", halign='left'))
            rb.add_widget(Label(text=f"Ilość: {il_lok_fmt}", halign='right'))
            layout.add_widget(rb)
            
        popup = Popup(title='Stan towaru', content=content, size_hint=(0.95, 0.85))
        pow = Button(text="POWRÓT", size_hint_y=None, height=dp(45), background_color=(0.3, 0.3, 0.3, 1))
        pow.bind(on_press=popup.dismiss)
        content.add_widget(pow)
        popup.open()

class MagazynApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.05, 1)
        self.title = "System Inwentaryzacji"
        try:
            return InwentaryzacjaApp()
        except Exception as e:
            err_msg = traceback.format_exc()
            layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            layout.add_widget(Label(text="[b][color=#FF3333]BŁĄD KRYTYCZNY:[/color][/b]", markup=True, font_size=sp(16), size_hint_y=None, height=dp(40)))
            scroll = ScrollView()
            lbl = Label(text=err_msg, font_size=sp(12), halign='left', valign='top')
            lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
            scroll.add_widget(lbl)
            layout.add_widget(scroll)
            return layout

if __name__ == '__main__':
    MagazynApp().run()
