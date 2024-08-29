"""

projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Vratislav Peska

email: vpeska@gmail.com

discord: Vratislav Peška vratislavpeska_11865

"""

#importy
from requests import get 
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs
import sys
import csv
import re

#funkce
def over_url(url: str):
    try:
        odpoved = get(url)
        return odpoved.status_code == 200
    except RequestException as e:
        print(f"Error: {e}")
        return False

def spusteni():
    if len(sys.argv) != 3:
        print("Chyba pri zadani: Ke spusteni skriptu musite zadata presne dva argumenty. V prikladu ve spicatych zavorkach")
        print("Priklad pouziti: python3 main.py <URL> <output_file>")
        sys.exit(1)

    # Ziskani argumentu z prikazove radky
    zadana_url = sys.argv[1]
    zadany_vystup = sys.argv[2]

    if not over_url(zadana_url):
        print("Chyba pri zadani: Prvni argument neni funkcni URL nebo stranka nereaguje.")
        sys.exit(1)

    print(f"Zacinam stahovat data z {zadana_url} a ukladam do csv souboru s unicode UTF-8 {zadany_vystup}.csv")
    return zadana_url, zadany_vystup
    
def vyber_ucelek(url: str, vystup: str) -> 'bs4.BeautifulSoup': # uzivatel zadava odkaz na uzemni celek a jmeno vystupniho souboru pri spousteni skriptu
                                            # napr. https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5205 a volby_trutnov.csv
    #funkce analyzuje zadany odkaz
    odpoved = get(url)
    rozdelena_odpoved_ucelku = bs(odpoved.text, features="html.parser")
    
    #vytvari vystup dle zadaneho nazvu
    hlavicka = [
        "kód obce",
        "název obce",
        "voliči v seznamu",
        "vydané obálky",
        "platné hlasy"
    ]
    with open(f"{vystup}.csv", 'w', newline='', encoding='utf-8') as csv_prazdny:
        zapis = csv.writer(csv_prazdny)
        zapis.writerow(hlavicka)
    
    #vraci hodnotu rozdelen odpovedi z webu voleb uzemniho celku
    return rozdelena_odpoved_ucelku #pri volani funkce ukladam jako promenou "html_obci"


def najdi_odkazy_obci(odpoved_s_obcemi: str) -> list: # z rozdelene odpovedi uzemniho celku najde odkazy na jednotlive obce
    odkazy_na_obce = [] #bude obsahovat fragmenty odkazu puvodem z td/a tagu
    komplet_odkazy = [] #bude obsahovat rekonstruovane cele funkcni odakzy na konkretni obce
    td_tags = odpoved_s_obcemi.find_all("td", {"class": "cislo"}) #tag td s argumentem class o hodnote cislo jako zdroj odkazu
    for a_href in td_tags: #cyklus ktery vyhledava fragmenty
        tag = a_href.find("a")
        odkazy_na_obce.append(tag.attrs.get("href", "nejsou data"))
    for odkaz in odkazy_na_obce: #cyklus ktery rekonstruuje odkazy
        komplet_odkazy.append(f"https://volby.cz/pls/ps2017nss/{odkaz}")
    return komplet_odkazy #pri volani funkce ukladam jako promenou "odkazy_obci"


def najdi_kod_obce(odkaz_obec: str, vystup_csv: str):
    
    #najde kod obce
    extrahovany_kod = r"obec=(\d+)&xvyber="
    shoda = re.search(extrahovany_kod, odkaz_obec)
    kod_obce = shoda.group(1)
    return kod_obce

def info_obec(url_obec: str) -> 'bs4.BeautifulSoup': # 
    #analyzuje zadany odkaz konkretni obce
    odpoved = get(url_obec)
    obec_odpoved = bs(odpoved.text, features="html.parser")
    return obec_odpoved

def najdi_nazev_obce(obec: str) -> str:
    h3_tags = obec.find_all("h3") #tagy s h3 argumentem jako zdroj nazvu obce
    for h3 in h3_tags: #cyklus ktery vyhledava jen ty ktere obsahuji uvnitr text "Obec:"
        if "Obec:" in h3.text:
            nazev = h3.text.split("Obec:")[1].strip()
            return nazev
    return nazev

def volici_v_obci(obec: str) -> int:
    td_tag = obec.find("td", class_="cislo", headers="sa2") #tagy s td argumentem a spravnou class a sa jako zdroj poctu volicu
    if td_tag:
        volici = int(td_tag.text.replace('\xa0', ''))
        return volici
    return 0  # Vrati 0, pokud nenajde odpovidajici td tag
    
def obalky_v_obci(obec: str) -> int:
    td_tag = obec.find("td", class_="cislo", headers="sa3") #tagy s td argumentem a spravnou class a sa jako zdroj poctu obalek
    if td_tag:
        obalky = int(td_tag.text.replace('\xa0', ''))
        return obalky
    return 0  # Vrati 0, pokud nenajde odpovidajici td tag

def hlasy_v_obci(obec: str) -> int:
    td_tag = obec.find("td", class_="cislo", headers="sa6") #tagy s td argumentem a spravnou class a sa jako zdroj poctu hlasu
    if td_tag:
        hlasy = int(td_tag.text.replace('\xa0', ''))
        return hlasy
    return 0  # Vrati 0, pokud nenajde odpovidajici td tag


def najdi_kandidujici(obec:str) -> str:
    strany = list()
    for strana in obec.find_all("td", class_="overflow_name"):
        jmeno_strana = strana.get_text(strip=True)
        hlasy_strana = strana.find_next_sibling('td', class_='cislo')
        
        if hlasy_strana:
            hlasy_strana = int(hlasy_strana.get_text(strip=True).replace('\xa0', ''))
            strany.append({jmeno_strana: hlasy_strana})
    return strany
    
def hlasy_v_obci_do_csv(list_vysledky: list, csv_data: str):    
    with open(csv_data, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        jmena_sloupcu = reader.fieldnames
        data = list(reader)
    
    # sloupce pokud neexistuji
    
    for strana in list_vysledky:
        for klic in strana.keys():
            if klic not in jmena_sloupcu:
                jmena_sloupcu.append(klic)
    
    # aktualizace sloupcu
    for row in data:
        for strana in list_vysledky:
            for klic, hodnota in strana.items():
                if klic in jmena_sloupcu and row.get(klic) in (None, ''):
                    row[klic] = hodnota
    
    # zazpis dat s novymi sloupci
    with open(csv_data, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=jmena_sloupcu)
        
        # Zápis hlavičky (včetně nových sloupců)
        writer.writeheader()

        # Zápis původních dat se zachováním existujících hodnot
        for row in data:
            writer.writerow(row)

# volani funkci a ukladani dat do csv
if __name__ == "__main__":
    
    # Zavolani funkce na spusteni kontroly prikazu atd.
    zadana_url, zadany_vystup = spusteni()
    
    # Zavolani funkce s argumenty z prikazove radky a ulozeni rozdelene odpovedy pomoci html.parser do promenne html_obce
    html_obci = vyber_ucelek(zadana_url, zadany_vystup)

    # Zavolani funkce na hledani odkazu na jednotlive obce
    odkazy_obci = najdi_odkazy_obci(html_obci)
    
    # Vytvarim slovnik, ze ktereho se budou generovat hodnoty csv
    obec_statistiky = {"kód obce":'',
        "název obce":'',
        "voliči v seznamu":'',
        "vydané obálky":'',
        "platné hlasy":''}
    # Cyklus, ktery prochazi odkazy obci
    for odkaz in odkazy_obci:
        #volani funkce pro extrahovani kodu konkretni obce z url odkazu na obec a rovnou kod zapisuje prvniho sloupce csv - plus ulozeni kodu do slovniku
        obec_statistiky["kód obce"] = najdi_kod_obce(odkaz, f"{zadany_vystup}.csv")
        #volani funkce na odpoved z url pro konkretni obec s vystupem jako prasovany html
        obec = info_obec(odkaz)

        #najdou statistiky konkretni obce a ulozi je do slovniku
        obec_statistiky["název obce"] = najdi_nazev_obce(obec)
        obec_statistiky["voliči v seznamu"] = volici_v_obci(obec)
        obec_statistiky["vydané obálky"] = obalky_v_obci(obec)
        obec_statistiky["platné hlasy"] = hlasy_v_obci(obec)

        #ulozit slovnik se statistikou obce do odpovidajiciho radku csv
        # Nacte se csv
        with open(f"{zadany_vystup}.csv", mode='r', encoding='utf-8') as csv_s_daty:
            reader = csv.DictReader(csv_s_daty)
            nazvy_sloupcu = reader.fieldnames  # nacte nazvy sloupcu
        with open(f"{zadany_vystup}.csv", mode='a', newline='', encoding='utf-8') as csv_s_daty:
            zapis_do_csv = csv.DictWriter(csv_s_daty, fieldnames=nazvy_sloupcu)
            zapis_do_csv.writerow(obec_statistiky)  # Zapsání nového řádku
        #ulozit pocty hlasu pro jednotlive kandidujici strany v dane obci jako seznam slovniku
        kand_strany = najdi_kandidujici(obec)
        #zapise hlasy do vysledneho csv
        hlasy_v_obci_do_csv(kand_strany, f"{zadany_vystup}.csv")

    print("Program dokoncil stahovani")
