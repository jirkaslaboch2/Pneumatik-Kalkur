from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QIcon, QPixmap, QFont, QIntValidator
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import sys
import os
import math
 
app = QtWidgets.QApplication(sys.argv)
 
# --- FUNKCE PRO VÝPOČET A ZOBRAZENÍ VÝSLEDKŮ ---
def vypocitej_a_zobraz():
    try:
        # Vytáhneme si čísla z levých políček
        s1 = float(inputs_l[0].text())
        p1 = float(inputs_l[1].text())
        r1 = float(inputs_l[2].text())
 
        # Vytáhneme si čísla z pravých políček
        s2 = float(inputs_p[0].text())
        p2 = float(inputs_p[1].text())
        r2 = float(inputs_p[2].text())
 
        # pomocné funkce pro výpočet
        def vyskapocitat(sirka, profil):
            return sirka * profil * 0.01
 
        def vypocetplomerasi(R, vyska):
            return 12.7 * R + vyska
 
        def vypocetobvod(celpolomevmm):
            return celpolomevmm * 2 * math.pi
 
        def vypocetoteceknakm(obvod):
            try:
                if obvod == 0: return 0
                return 1000000 / obvod
            except:
                return 0
 
        def porovnatpolomer(celpolomevmm1, celpolomevmm2):
            rozpolemer = celpolomevmm1 - celpolomevmm2
            rozpolemervpercet = (rozpolemer / celpolomevmm1) * 100
            return rozpolemer, rozpolemervpercet
 
        def porovnatobvod(obvod1, obvod2):
            rozobvod = obvod1 - obvod2
            rozobvodvpercet = (rozobvod / obvod1) * 100
            return rozobvod, rozobvodvpercet
 
        def vypocetodchylkarzch(otecknakm1, otecknakm2):
            if otecknakm2 == 0: return 0, 0, 0, 0
            odchyl = otecknakm1 / otecknakm2
            odchylpercet = (odchyl - 1) * 100
            return odchylpercet, 50 * odchyl, 100 * odchyl, 130 * odchyl
 
        # Spočítáme to pro obě kola
        v1 = vyskapocitat(s1, p1)
        v2 = vyskapocitat(s2, p2)
        pol1 = vypocetplomerasi(r1, v1)
        pol2 = vypocetplomerasi(r2, v2)
        o1 = vypocetobvod(pol1)
        o2 = vypocetobvod(pol2)
        ot1 = vypocetoteceknakm(o1)
        ot2 = vypocetoteceknakm(o2)
       
        # Rozdíly
        rozdil_polomer, rozdil_polomer_percent = porovnatpolomer(pol2, pol1)
        rozdil_obvod, rozdil_obvod_percent = porovnatobvod(o2, o1)
        # Odchylka tachometru
        odchylka_procenta, odchylka_km50, odchylka_km100, odchylka_km130 = vypocetodchylkarzch(ot1, ot2)
 
        # Dynamicky přepíšeme hlavičky v tabulce
        tabulka.setHorizontalHeaderLabels([
            "Metrika",
            f"{int(s1)}/{int(p1)} R{int(r1)}",
            f"{int(s2)}/{int(p2)} R{int(r2)}"
        ])
 
        # Data pro tabulku
        data = [
            (f"{v1:.2f} mm", f"{v2:.2f} mm"), # Výška
            (f"{pol1:.2f} mm", f"{pol2:.2f} mm"), # Poloměr
            ("-", f"{rozdil_polomer:+.2f} mm({rozdil_polomer_percent:+.2f}%)"), # Rozdíl poloměru
            (f"{o1:.2f} mm", f"{o2:.2f} mm"), # Obvod
            ("-", f"{rozdil_obvod:+.2f} mm({rozdil_obvod_percent:+.2f}%)"), # Rozdíl obvodu
            (f"{ot1:.0f}", f"{ot2:.0f}"), # Otáčky
            ("-", f"{odchylka_procenta:+.2f} %") # Odchylka v %
        ]
 
        # Vložení dat do tabulky
        for i, (val1, val2) in enumerate(data):
            tabulka.setItem(i, 1, QTableWidgetItem(val1))
            tabulka.setItem(i, 2, QTableWidgetItem(val2))
 
        druheokno.show()
 
    except ValueError:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Vyplňte prosím všechna pole číselnými hodnotami.")
        msg.setWindowTitle("Chyba zadání")
        msg.exec_()
 
# --- FUNKCE PRO HLEDÁNÍ ALTERNATIVY ---
def pridat_radu():
    try:
        # Načtení vstupů
        s1_text = inputs_l[0].text().replace(',', '.')
        p1_text = inputs_l[1].text().replace(',', '.')
        r1_text = inputs_l[2].text().replace(',', '.')
 
        if not s1_text or not p1_text or not r1_text: return
 
        s1 = float(s1_text)
        p1 = float(p1_text)
        r1 = float(r1_text)
 
        pol1 = (s1 * (p1 / 100)) + (r1 * 25.4 / 2)
        obvod1 = 2 * math.pi * pol1
 
        # Rozšířené seznamy rozměrů
        sirky = [175, 185, 195, 205, 215, 225, 235, 245, 255]
        profily = [35, 40, 45, 50, 55, 60, 65, 70]
        rafky = [r1 - 1, r1, r1 + 1]
 
        vsechny_moznosti = []
 
        for s_alt in sirky:
            for p_alt in profily:
                for r_alt in rafky:
                    v_alt_mm = s_alt * (p_alt / 100)
                    pol_alt = v_alt_mm + (r_alt * 25.4 / 2)
                    o_alt = 2 * math.pi * pol_alt
                   
                    rozdil = abs(o_alt - obvod1)
 
                    if (s_alt != s1 or p_alt != p1 or r_alt != r1):
                        vsechny_moznosti.append({
                            'rozdil': rozdil,
                            'data': (s_alt, p_alt, r_alt, v_alt_mm, pol_alt, o_alt)
                        })
 
        vsechny_moznosti.sort(key=lambda x: x['rozdil'])
        top_3 = vsechny_moznosti[:3]
 
        # Zápis do tabulky
        for index, shoda in enumerate(top_3):
            s_alt, p_alt, r_alt, v_alt_mm, pol_alt, o_alt = shoda['data']
           
            if o_alt == 0: continue
            ot_alt = 1000000 / o_alt
            if obvod1 == 0: continue
            odchylka_alt = ((o_alt - obvod1) / obvod1) * 100
 
            col_idx = 3 + index
           
            if tabulka.columnCount() <= col_idx:
                tabulka.insertColumn(col_idx)
           
            header_text = f"Alt {index+1}: {int(s_alt)}/{int(p_alt)} R{int(r_alt)}"
            tabulka.setHorizontalHeaderItem(col_idx, QTableWidgetItem(header_text))
           
            vysledky_data = [
                f"{v_alt_mm:.2f} mm",
                f"{pol_alt:.2f} mm",
                f"{pol_alt - pol1:+.2f} mm",
                f"{o_alt:.2f} mm",
                f"{o_alt - obvod1:+.2f} mm",
                f"{ot_alt:.0f}",
                f"{odchylka_alt:+.2f} %"
            ]
 
            for row_idx, hodnota in enumerate(vysledky_data):
                item = QTableWidgetItem(hodnota)
                tabulka.setItem(row_idx, col_idx, item)
 
        # Úpravy vzhledu
        tabulka.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tlacitko2.setEnabled(False)
 
    except Exception as e:
        print(f"Chyba: {e}")
 
def zpet():
    druheokno.close()
 
def alter_napis():
    napis_alt = QLabel("alternativy jsou k druhé pneumatice")
    font_alt =QFont("Arial", 16)
    napis_alt.setFont(font_alt)
    layout2.addWidget(napis_alt, alignment=Qt.AlignCenter)
 
# --- HLAVNÍ OKNO A OBRAZEK ---
 
validator_celych_cisel = QIntValidator()
 
hlavniokno = QtWidgets.QWidget()
hlavniokno.setWindowTitle("Pneumatik Kalkur")
hlavniokno.setStyleSheet("""
    QWidget { background-color: #ffffff; font-family: 'Segoe UI', Arial; }
    QLabel { color: #333; }
    QLineEdit {
        border: 2px solid #ccc;
        border-radius: 6px;
        padding: 5px;
        background: white;
    }
    QLineEdit:focus { border: 2px solid #2ecc71; }
    QPushButton {
        background-color: #2ecc71;
        color: black;
        border-radius: 8px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #27ae60; }
""")
 
layout = QVBoxLayout()
layout.setContentsMargins(20, 20, 20, 20)
 
# Cesta k souboru
adresar = os.path.dirname(os.path.abspath(__file__))
cesta_k_fotce = os.path.join(adresar, "logo.jpg")
 
# Label pro obrázek s ohraničením a efektem
label_obrazek = QLabel()
label_obrazek.setStyleSheet("""
    QLabel {
        background-color: black;
        border: 4px solid #00FF00;
        border-radius: 10px;
        padding: 10px;
    }
""")
label_obrazek.setAlignment(Qt.AlignCenter)
 
# Načtení a vložení obrázku (OPRAVENÝ BLOK)
if os.path.exists(cesta_k_fotce):
    pixmap = QPixmap(cesta_k_fotce)
    # Změna velikosti, aby vypadal v okně dobře
    label_obrazek.setPixmap(pixmap.scaled(300, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
else:
    label_obrazek.setText("Logo: logo.png nebylo nalezeno v adresáři!")
    label_obrazek.setStyleSheet("QLabel { color: white; background-color: black; border: 4px solid red; border-radius: 10px; padding: 10px; }")
 
layout.addWidget(label_obrazek, alignment=Qt.AlignCenter)
layout.addSpacing(10) # Mezera pod logem
 
# Hlavní nadpis aplikace
H1 = QLabel("KALKULAČKA\nROZMĚRŮ PNEUMATIK")
font2 = QFont("Arial", 28, QFont.Bold)
H1.setFont(font2)
H1.setAlignment(Qt.AlignCenter)
layout.addWidget(H1)
 
# Přidání grid layoutu pro vstupy
grid = QGridLayout()
layout.addLayout(grid)
 
font1 = QFont("Arial", 16, QFont.Bold)
 
nazev1 = QLabel("Původní Rozměr:")
nazev1.setAlignment(Qt.AlignCenter)
nazev1.setFont(font1)
grid.addWidget(nazev1, 2, 1)
 
nazev2 = QLabel("Nový Rozměr:")
nazev2.setAlignment(Qt.AlignCenter)
nazev2.setFont(font1)
grid.addWidget(nazev2, 2, 3)
 
popisky = ["Šířka (mm)", "Profil (%)", "Průměr Ráfku (palce)"]
inputs_l = []
inputs_p = []
 
hodnoty1 = ["např. 195", "např. 65", "např. 15"]
hodnoty2 = ["např. 200", "např. 65", "např. 15"]
 
for i, text in enumerate(popisky):  
    # Levá strana
    popisek_l = QLabel(f"{text} :")
    grid.addWidget(popisek_l, i + 3, 0, alignment=Qt.AlignLeft)
 
    l_text = QLineEdit()
    l_text.setPlaceholderText(hodnoty1[i])
    l_text.setValidator(validator_celych_cisel)
    l_text.setFixedWidth(200)
    l_text.setFixedHeight(35)
    inputs_l.append(l_text)
    grid.addWidget(l_text, i + 3, 1, alignment=Qt.AlignLeft)
 
    # Pravá strana
    popisek_p = QLabel(f"{text} :")
    grid.addWidget(popisek_p, i + 3, 2, alignment=Qt.AlignRight)
 
    p_text = QLineEdit()
    p_text.setPlaceholderText(hodnoty2[i])
    p_text.setValidator(validator_celych_cisel)
    p_text.setFixedWidth(200)
    p_text.setFixedHeight(35)
    inputs_p.append(p_text)
    grid.addWidget(p_text, i + 3, 3, alignment=Qt.AlignLeft)
 
# Hlavní tlačítko "Porovnat"
tlacitko = QtWidgets.QPushButton('Porovnat')
tlacitko.setMinimumSize(150, 60)
tlacitko.setFont(QFont("Arial", 18, QFont.Bold))
grid.addWidget(tlacitko, i+4, 1, 1, 2, alignment=Qt.AlignCenter)
 
layout.addStretch()
hlavniokno.setLayout(layout)
hlavniokno.setFixedSize(850, 700)
 
# --- DRUHÉ OKNO (VÝSLEDEK POROVNÁNÍ) ---
druheokno = QWidget()
druheokno.setWindowTitle("Výsledek porovnání")
druheokno.setFixedSize(900, 650)
druheokno.setStyleSheet("""
    QWidget { background-color: #ffffff; }
    QTableWidget {
        gridline-color: #ecf0f1;
        border: 1px solid #dcdde1;
    }
    QHeaderView::section {
        background-color: #34495e;
        color: white;
        font-weight: bold;
        border: 1px solid #2c3e50;
    }
    QPushButton {
        background-color: #2ecc71;
        color: black;
        border-radius: 8px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #27ae60; }
    QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }
""")
 
layout2 = QVBoxLayout()
H2 = QLabel("Tady se zobrazí výsledek porovnání")
H2.setAlignment(Qt.AlignCenter)
H2.setFont(font2)
layout2.addWidget(H2)
 
# Tlačítko "alternativní rozměry"
tlacitko2 = QPushButton("Zobrazit Alternativní Rozměry")
tlacitko2.setMinimumHeight(40)
tlacitko2.setFont(QFont("Arial", 14))
layout2.addWidget(tlacitko2, alignment=Qt.AlignCenter)
 
# Nastavení tabulky s výsledky
tabulka = QTableWidget()
tabulka.setRowCount(7)
tabulka.setColumnCount(3)
tabulka.setHorizontalHeaderLabels(["Metrika", "Původní", "Nový"])
 
metriky = ["výška pneu", "poloměr (kolo+pneu)", "rozdíl v poloměru", "obvod", "rozdíl v obvodu", "otočení pneu/km", "odchylka - rychlost"]
for i, m in enumerate(metriky):
    tabulka.setItem(i, 0, QTableWidgetItem(m))
 
tabulka.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
tabulka.setFixedHeight(300)
tabulka.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
layout2.addWidget(tabulka)
 
# Tlačítko "Zpět"
tlacitko3 = QPushButton("Zpět")
tlacitko3.setMinimumHeight(40)
tlacitko3.setFont(QFont("Arial", 14))
tlacitko3.setStyleSheet("""
    QPushButton {
        background-color: #FF0000;
        color: white; /* Černý text na červeném pozadí? To je blbě čitelné. Měním na bílý. */
        border-radius: 8px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #c0392b; }
""")
tlacitko3.clicked.connect(zpet)
layout2.addWidget(tlacitko3, alignment=Qt.AlignCenter | Qt.AlignBottom)
 
druheokno.setLayout(layout2)
layout2.addStretch()
 
# Propojení tlačítek s funkcemi
tlacitko.clicked.connect(vypocitej_a_zobraz)
tlacitko2.clicked.connect(pridat_radu)
tlacitko2.clicked.connect(alter_napis)
 
# Spuštění
hlavniokno.show()
sys.exit(app.exec_())
 