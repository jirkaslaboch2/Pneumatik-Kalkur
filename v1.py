from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import math
import random

app = QtWidgets.QApplication([]) 

# FUNKCE PRO VÝPOČET A ZOBRAZENÍ VÝSLEDKŮ
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

        #pocitaní
        def vyskapocitat(sirka,profil):
            vyska = sirka*profil*0.01
            return vyska

        def vypocetplomerasi(R,vyska):
            celpolomevmm = 12.7*R +vyska
            return celpolomevmm

        def vypocetobvod(celpolomevmm):
            obvod = celpolomevmm*2*math.pi
            return obvod

        #print(vypocetobvod(5))

        def vypocetoteceknakm(obvod):

            try:
                oteceknakm = 1000000/obvod
            except:
                oteceknakm = 0
            return oteceknakm

        #print(vypocetoteceknakm(5))
        def porovnatpolomer(celpolomevmm1,celpolomevmm2):
            rozpolemer = celpolomevmm1 - celpolomevmm2
            rozpolemervpercet = (rozpolemer/celpolomevmm1)*100
            return rozpolemer,rozpolemervpercet
        #print(porovnatpolomer(2,1))
        def porovnatobvod(obvod1,obvod2):
            rozobvod = obvod1-obvod2
            rozobvodvpercet = (rozobvod/obvod1)*100
            return rozobvod,rozobvodvpercet


        #print(porovnatobvod(79.81,319.19))
        def vypocetodchylkarzch (otecknakm1,otecknakm2):
            odchyl = otecknakm1/otecknakm2
            odchylpercet = odchyl*100
            km50 = 50* odchyl
            km100 = 100* odchyl
            km130 = 130*odchyl
            return odchylpercet,km50,km100,km130
        # Spočítáme to pro obě kola
        v1 = vyskapocitat(s1, p1)
        v2 = vyskapocitat(s2, p2)
        pol1 = vypocetplomerasi(r1,v1)
        pol2 = vypocetplomerasi(r2,v2)
        o1 = vypocetobvod(pol1)
        o2 = vypocetobvod(pol2)
        ot1 = vypocetoteceknakm(o1)
        ot2 = vypocetoteceknakm(o2)
        

        # Rozdíly, co chceme vidět v porovnání
        rozdil_polomer,rozdil_polomer_percent = porovnatpolomer(pol2, pol1)
        rozdil_obvod,rozdil_obvod_percent = porovnatobvod(o2, o1)
        # Procentuální rozdíl, aby člověk věděl, o kolik mu kecá tachometr
        odchylka_procenta,odchylka_km50,odchylka_km100,odchylka_km130 = vypocetodchylkarzch(ot1,ot2)

        # Dynamicky přepíšeme hlavičky v tabulce, aby tam byly ty rozměry co uživatel zadal
        tabulka.setHorizontalHeaderLabels([
            "Metrika", 
            f"{int(s1)}/{int(p1)} R{int(r1)}", 
            f"{int(s2)}/{int(p2)} R{int(r2)}"
        ])

        # Seznam dat, co budeme sázet do řádků tabulky
        data = [
            (f"{v1:.2f} mm", f"{v2:.2f} mm"), # Výška
            (f"{pol1:.2f} mm", f"{pol2:.2f} mm"), # Poloměr
            ("-", f"{rozdil_polomer:+.2f} mm({rozdil_polomer_percent:+.2f}%)"), # Rozdíl poloměru
            (f"{o1:.2f} mm", f"{o2:.2f} mm"), # Obvod
            ("-", f"{rozdil_obvod:+.2f} mm({rozdil_obvod_percent:+.2f}%)"), # Rozdíl obvodu
            (f"{ot1:.0f}", f"{ot2:.0f}"), # Otáčky
            ("-", f"{odchylka_procenta:+.2f} %") # Odchylka v %
        ]

        # Cyklus, co projde data a nahází je do buněk v tabulce
        for i, (val1, val2) in enumerate(data):
            tabulka.setItem(i, 1, QTableWidgetItem(val1))
            tabulka.setItem(i, 2, QTableWidgetItem(val2))

        # Ukážeme okno s výsledkem
        druheokno.show()

    except ValueError:
        # Kdyby někdo nechal prázdno, hodí to chybu
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Vyplňte prosím všechna pole číselnými hodnotami.")
        msg.setWindowTitle("Chyba zadání")
        msg.exec_()

# --- FUNKCE PRO HLEDÁNÍ ALTERNATIVY ---

def pridat_radu():
    try:
        # 1. Načtení vstupů z GUI (původní pneumatika)
        s1 = float(inputs_l[0].text().replace(',', '.'))
        p1 = float(inputs_l[1].text().replace(',', '.'))
        r1 = float(inputs_l[2].text().replace(',', '.'))

        # Výpočet původního poloměru a obvodu
        pol1 = (s1 * (p1 / 100)) + (r1 * 25.4 / 2)
        obvod1 = 2 * math.pi * pol1

        # 2. Seznamy běžných rozměrů
        sirky = [185, 195, 205, 215, 225, 235, 245]
        profily = [40, 45, 50, 55, 60, 65]
        rafky = [r1 - 1, r1, r1 + 1]  # Zkusíme stejný ráfek, o palec menší i větší

        # 3. Logika hledání nejlepší alternativy
        nejlepsi_shoda = None
        min_rozdil = float('inf')

        for s_alt in sirky:
            for p_alt in profily:
                for r_alt in rafky:
                    # Výpočet poloměru zkoušené alternativy
                    v_alt_mm = s_alt * (p_alt / 100)
                    pol_alt = v_alt_mm + (r_alt * 25.4 / 2)
                    o_alt = 2 * math.pi * pol_alt
                    
                    rozdil = abs(o_alt - obvod1)

                    # Chceme jiný rozměr než ten původní, ale co nejbližší obvodem
                    if rozdil < min_rozdil and (s_alt != s1 or p_alt != p1 or r_alt != r1):
                        min_rozdil = rozdil
                        nejlepsi_shoda = (s_alt, p_alt, r_alt, v_alt_mm, pol_alt, o_alt)

        # Pokud jsme našli shodu, vypíšeme ji
        if nejlepsi_shoda:
            s_alt, p_alt, r_alt, v_alt_mm, pol_alt, o_alt = nejlepsi_shoda
            
            ot_alt = 1000000 / o_alt
            odchylka_alt = ((o_alt - obvod1) / obvod1) * 100

            # 4. Zápis do tabulky
            if tabulka.columnCount() == 3:
                tabulka.insertColumn(3)
                tabulka.setHorizontalHeaderItem(3, QTableWidgetItem(f"Alt: {int(s_alt)}/{int(p_alt)} R{int(r_alt)}"))
                
                # Naplnění daty
                data = [
                    f"{v_alt_mm:.2f} mm",
                    f"{pol_alt:.2f} mm",
                    f"{pol_alt - pol1:+.2f} mm",
                    f"{o_alt:.2f} mm",
                    f"{o_alt - obvod1:+.2f} mm",
                    f"{ot_alt:.0f}",
                    f"{odchylka_alt:+.2f} %"
                ]

                for i, hodnota in enumerate(data):
                    tabulka.setItem(i, 3, QTableWidgetItem(hodnota))

                tabulka.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                tlacitko2.setEnabled(False)

    except Exception as e:
        print(f"Chyba při výpočtu alternativy: {e}")

# Hlavní okno
layout = QVBoxLayout() 

# Omezení celých čísel
validator_celych_cisel = QtGui.QIntValidator() 

hlavniokno = QtWidgets.QWidget() 
hlavniokno.setWindowTitle("Pneumatik Kalkur") 

# Hlavní nadpis aplikace
H1 = QLabel("KALKULAČKA\nROZMĚRŮ PNEUMATIK") 
H1.setAlignment(Qt.AlignHCenter) 
layout.addWidget(H1, alignment=Qt.AlignCenter) 

# Přidání grid layoutu
grid = QGridLayout() 
layout.addLayout(grid) 

font1 = QFont("Arial", 16)
font1.setBold(True)

nazev1 = QLabel("Původní Rozměr:")
nazev1.setAlignment(Qt.AlignCenter)
nazev1.setFont(font1)
grid.addWidget(nazev1, 2, 1, 1, 1)

nazev2 = QLabel("Nový Rozměr:")
nazev2.setAlignment(Qt.AlignCenter)
nazev2.setFont(font1)
grid.addWidget(nazev2, 2, 3, 1, 8)

# přidání popisků do listu
popisky = ["Šířka (mm)", "Profil (%)", "Průměr Ráfku (palce )"] 

inputs_l = [] # Seznam objektů pro levou stranu
inputs_p = [] # Seznam objektů pro pravou stranu

hodnoty1 = ["např. 195", "např. 65", "např. 15"]
hodnoty2 = ["např. 200", "např. 65", "např. 15"]

for i, text in enumerate(popisky):  

    aktualni_hodnota1 = hodnoty1[i]
    aktualni_hodnota2 = hodnoty2[i]

    # Levá strana
    popisek_l = QLabel(f"{text} :") # vytvoři se textový popisek podle naseho seznamu popisky
    grid.addWidget(popisek_l, i + 3, 1, alignment=Qt.AlignLeft)  # vloží popisek do řádku podle i

    l_text = QLineEdit() # vytvori se textovy radek
    l_text.setPlaceholderText(aktualni_hodnota1)
    l_text.setValidator(validator_celych_cisel) # do pole budeme moct psat jen cele cisla
    l_text.setFixedWidth(200) # priradi se sirka
    l_text.setFixedHeight(35) # priradi se vyska
    inputs_l.append(l_text) # Uložíme odkaz na políčko

    grid.addWidget(l_text, i + 3, 2, alignment=Qt.AlignLeft) # textovy radek se da vedle popisku

    # Pravá strana
    popisek_p = QLabel(f"{text} :") # vytvoři se textový popisek podle naseho seznamu popisky
    grid.addWidget(popisek_p, i + 3, 7, alignment=Qt.AlignRight)# pravý popisek bude ve stejném řádku jako levý

    p_text = QLineEdit() # vytvori se textovy radek
    p_text.setPlaceholderText(aktualni_hodnota2)
    p_text.setValidator(validator_celych_cisel) # do pole budeme moct psat jen cele cisla
    p_text.setFixedWidth(200) # priradi se sirka
    p_text.setFixedHeight(35) # priradi se vyska
    inputs_p.append(p_text) # Uložíme odkaz na políčko

    grid.addWidget(p_text, i + 3, 8, alignment=Qt.AlignLeft) # pravé vstupní pole

# Font pro hlavní nadpis a velikost okna
font2 = QFont("Arial", 28)
font2.setBold(True)
H1.setFont(font2) 
hlavniokno.setLayout(layout)
hlavniokno.setFixedSize(800,500) 

# Hlavní tlačítko "Porovnat"
tlacitko = QtWidgets.QPushButton('Porovnat')
tlacitko.setMinimumSize(100,50)
grid.addWidget(tlacitko,5,3,20,4,)
layout.addStretch()

# Druhé okno
druheokno = QWidget()
druheokno.setWindowTitle("Výsledek porovnání")
druheokno.setFixedSize(800, 600)

layout2 = QVBoxLayout()
H2 = QLabel("Tady se zobrazí výsledek porovnání")
H2.setAlignment(Qt.AlignHCenter)
H2.setFont(font2)
layout2.addWidget(H2)

# Tlačítko "alternativní rozměry"
tlacitko2 = QPushButton("Zobrazit Alternativní Rozměry")
tlacitko2.setMinimumHeight(30)
layout2.addWidget(tlacitko2)

font3 = QFont("Arial", 14)
tlacitko2.setFont(font3)
layout2.setAlignment(tlacitko2, Qt.AlignCenter)

# Nastavení tabulky s výsledky
tabulka = QTableWidget()
tabulka.setRowCount(7)
tabulka.setColumnCount(3)
tabulka.setHorizontalHeaderLabels(["Metrika", "Původní", "Nový"])

# Vyplnění prvního sloupce názvy metrik
tabulka.setItem(0, 0, QTableWidgetItem("výška pneu"))
tabulka.setItem(1, 0, QTableWidgetItem("poloměr (kolo+pneu)"))
tabulka.setItem(2, 0, QTableWidgetItem("rozdíl v poloměru"))
tabulka.setItem(3, 0, QTableWidgetItem("obvod"))
tabulka.setItem(4, 0, QTableWidgetItem("rozdíl v obvodu"))
tabulka.setItem(5, 0, QTableWidgetItem("otočení pneu/km"))
tabulka.setItem(6, 0, QTableWidgetItem("odchylka - rychlost"))

# Tabulka se roztáhne na celou šířku a nepůjde v ní přepisovat text
tabulka.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
layout2.addWidget(tabulka)
tabulka.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

druheokno.setLayout(layout2)
layout2.addStretch()

# Propojení tlačítek s funkcemi (aby to něco dělalo)
tlacitko.clicked.connect(vypocitej_a_zobraz)
tlacitko2.clicked.connect(pridat_radu)

hlavniokno.setStyleSheet("""
    QWidget { background-color: #f0f2f5; font-family: 'Segoe UI', Arial; }
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

# Spuštění
hlavniokno.show()
app.exec()