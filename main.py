"""

projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Vratislav Peska

email: vpeska@gmail.com

discord: Vratislav Peška vratislavpeska_11865

"""

#importy
# standardni knihovny
import sys
import csv
import re

# knihovny tretich stran
from requests import get 
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs

# Slovnik, ze ktereho se budou generovat hodnoty pro vystupni doubor v csv
obec_statistiky = {"kód obce":'',
    "název obce":'',
    "voliči v seznamu":'',
    "vydané obálky":'',
    "platné hlasy":''}

#funkce jsou razeny podle toho, jak jsou spousteny/volany

def spusteni():
    '''Funkce overuje, ze skript je spousten prave se dvema argumenty.
    Dale uklada argumenty z prikazoveho radku jako globalni promenne.
    Dale vola  fuknci pro overeni 1) url, 2) nazvu (ze obsahuje jen 
    alfanumericke znaky, podtrzitka a pomlcky, a ze tam neni dvakrat .csv.csv)
    '''

    if len(sys.argv) != 3:
        print("Chyba pri zadani: Ke spusteni skriptu musite zadat presne dva argumenty, url a vystup (bez pripony .csv). V prikladu ve spicatych zavorkach")
        print("Priklad pouziti: python3 main.py <URL> <output_file>")
        sys.exit(1)

    # Ziskani 2 argumentu z prikazove radky
    vstupni_url = sys.argv[1]
    vstupni_nazev = sys.argv[2]

    # overovani url zavolanim funkce
    if not overeni_url(vstupni_url):
        print("Chyba pri zadani: Prvni argument neni funkcni URL nebo stranka nereaguje.")
        sys.exit(1)
    
    # overovani nazvu zavolanim funkce
    if not overeni_nazvu(vstupni_nazev):
        print("Chyba pri zadani: Neplatny nazev souboru. Povoleny jsou jen alfanumericke znaky, podtrzitko a pomlcka. Nazev nesmi zahrnovat priponu .csv ani jinou.")
        sys.exit(1)

    print(f"Zacinam stahovat data z {vstupni_url} a ukladam do csv souboru s unicode UTF-8 {vstupni_nazev}.csv")
    return vstupni_url, vstupni_nazev


def overeni_url(url: str):
    '''Funkce overuje zda je zadana url funkcni internetova adresa.
    Parametr url je pri spousteni naplnen stringem ulozenym 
    pod promennou vstupni_url v ramci funkce spusteni().
    '''

    try:
        odpoved = get(url)
        return odpoved.status_code == 200
    except RequestException as e:
        print(f"Error: {e}")
        return False

def overeni_nazvu(nazev: str) -> bool:
    '''Fuknce overuje, zda je nazev souboru platny, t.j. obsahuje 
    jen povolene znaky, podtrzitko a pomlcka, a tim padem neobsahuje 
    priponu .csv ani jinou'''

    if not re.match(r'^[\w\-]+$', nazev):
        return False
    return True

    
def vyber_ucelek(url: str, vystup: str) -> bs: 
    
    '''Uzivatel zadava odkaz na uzemni celek a jmeno vystupniho souboru pri spousteni skriptu.
    Napr.: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5205 a volby_trutnov.
    Funkce uklada obsah stranky jako bs4 objekt a vytvari hlavicku ve vystupnim souboru. Obsah
    je ulozen pri volani funkce do globalni promenne html_obci'''
    
    #funkce analyzuje zadany odkaz
    odpoved = get(url)
    rozdelena_odpoved_ucelku = bs(odpoved.text, features="html.parser")
        
    #vytvari vystup dle zadaneho nazvu s definovanou hlavickou
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
    
    #vraci bs objekt rozdelene odpovedi z webu voleb uzemniho celku
    return rozdelena_odpoved_ucelku #pri volani funkce ukladam jako globalni promenou "html_obci"

def najdi_odkazy_obci(odpoved_s_obcemi: bs) -> list: 
    '''Z rozdelene odpovedi uzemniho celku 
    (bs objekt ulozeny v globalni promenne 
    html_obci) najde odkazy na jednotlive obce
    a ulozi je jako list do globalni promenne odkazy_obci'''

    fragmenty_odkazu = [] #bude obsahovat fragmenty odkazu puvodem z td/a tagu s relativni cestou
    komplet_odkazy = [] #bude obsahovat rekonstruovane cele funkcni odakzy na konkretni obce
    td_tags = odpoved_s_obcemi.find_all("td", {"class": "cislo"}) #tag td s argumentem class o hodnote cislo jako zdroj odkazu
    for a_href in td_tags: #cyklus ktery vyhledava fragmenty
        tag = a_href.find("a")
        fragmenty_odkazu.append(tag.attrs.get("href", "nejsou data")) #najde odkaz nebo vypise, ze odkaz neboli data nejsou
    for odkaz in fragmenty_odkazu: #cyklus, ktery rekonstruuje odkazy
        komplet_odkazy.append(f"https://volby.cz/pls/ps2017nss/{odkaz}")
    return komplet_odkazy #pri volani funkce ukladam jako promenou "odkazy_obci"

def ziskej_data_obci(odkazy_na_obce: list) -> dict:
    '''Tato funkce vyuziva jedinecneho odkazu na kazdou obec v seznamu odkazy_na_obce.
    Jeji telo tvori hlavne cyklus, ktery z tohoto odkazu nebo bs objektu za timto odkazem stahuje
    data pro danou obec. Globalni promenna obec_statistiky, pod kterou je ulozeny slovnik (klic je 
    nazev sloupce, hodnota slovniku je hodnota csv vystupu), je spolecna pro vsechny obce ve 
    vsech uzemnich celcich. Data jsou stahovana pomoci volani prislusnych funkci. Data ohledne
    kandidujicich stran a jejich ziskanych hlasu nejsou soucasti obec_statistiky, protoze se mohou
    mezi obcemi a uzemnimi celky lisit. Proto je jejich stahovani reseno tremi dalsimi funkcemi.'''
    
    # Cyklus, ktery prochazi odkazy obci a data uklada do slovniku obec_statistiky
    for odkaz in odkazy_na_obce:
        
        #volani funkce na odpoved z url pro konkretni obec s vystupem jako prasovany html
        obec = info_obec(odkaz)

        # SPOLECNA obecni statistika pro vsechny obce
        #volani funkci pro extrahovani dat konkretni obce z url odkazu na obec
        obec_statistiky["kód obce"] = najdi_kod_obce(odkaz)
        obec_statistiky["název obce"] = najdi_nazev_obce(obec)
        obec_statistiky["voliči v seznamu"] = volici_v_obci(obec)
        obec_statistiky["vydané obálky"] = obalky_v_obci(obec)
        obec_statistiky["platné hlasy"] = hlasy_v_obci(obec)
        #volani funkce na ulozeni ziskanych dato do csv
        uloz_obec_statistiky()

        # pro obec/uzemni celek SPECIFICKE statistiky: kandidujici strany a jejich volebni vysledek
        #kazda obec/uzemni celek ma jiny seznam kandidujicich stran, proto jsou ulozeny zvlast jako hodnoty v seznamu slovniikuuu
        kand_strany = najdi_kandidujici(obec)
        #aktualizuje data pro vysledne csv
        aktualni_sloupce, aktualni_data = aktualizace_dat(kand_strany, f"{overeny_vystup}.csv")
        #zapise aktualni data do vysledneho csv
        uloz_strany_v_obci(aktualni_sloupce, aktualni_data, f"{overeny_vystup}.csv")

def info_obec(url_obec: str) -> bs:
    '''Funkce ziskava bs odpoved z odkazu konkretni obce'''

    odpoved = get(url_obec)
    obec_odpoved = bs(odpoved.text, features="html.parser")
    return obec_odpoved

def najdi_kod_obce(odkaz_obec: str) -> str:
    '''Funkce hleda kod obce v odkazu na danou obec.'''
    #najde kod obce v samotnem odkazu
    extrahovany_kod = r"obec=(\d+)&xvyber="
    shoda = re.search(extrahovany_kod, odkaz_obec)
    kod_obce = shoda.group(1)
    return kod_obce

def najdi_nazev_obce(bs_obec: str) -> str:
    '''Funkce hleda nazev obce v bs objektu pro danou obec.'''
    h3_tags = bs_obec.find_all("h3") #tagy s h3 argumentem jako zdroj nazvu obce
    for h3 in h3_tags: #cyklus ktery vyhledava jen ty ktere obsahuji uvnitr text "Obec:"
        if "Obec:" in h3.text:
            nazev = h3.text.split("Obec:")[1].strip()
            return nazev
    return nazev

def volici_v_obci(bs_obec: str) -> int:
    '''Funkce hleda pocet volicu v bs objektu pro danou obec.'''
    td_tag = bs_obec.find("td", class_="cislo", headers="sa2") #tagy s td argumentem a spravnou class a sa jako zdroj poctu volicu
    if td_tag:
        volici = int(td_tag.text.replace('\xa0', ''))
        return volici
    return 0  # Vrati 0, pokud nenajde odpovidajici td tag
    
def obalky_v_obci(bs_obec: str) -> int:
    '''Funkce hleda pocet obalek v bs objektu pro danou obec.'''
    td_tag = bs_obec.find("td", class_="cislo", headers="sa3") #tagy s td argumentem a spravnou class a sa jako zdroj poctu obalek
    if td_tag:
        obalky = int(td_tag.text.replace('\xa0', ''))
        return obalky
    return 0  # Vrati 0, pokud nenajde odpovidajici td tag

def hlasy_v_obci(bs_obec: str) -> int:
    '''Funkce hleda pocet hlasu v obci v bs objektu pro danou obec.'''
    td_tag = bs_obec.find("td", class_="cislo", headers="sa6") #tagy s td argumentem a spravnou class a sa jako zdroj poctu hlasu
    if td_tag:
        hlasy = int(td_tag.text.replace('\xa0', ''))
        return hlasy
    return 0  # Vrati 0, pokud nenajde odpovidajici td tag

def uloz_obec_statistiky():       
    '''Uklada slovnik se statistikou dane obce, ktera je SPOLECNA pro vsechny obce do radku csv'''
    with open(f"{overeny_vystup}.csv", mode='r', encoding='utf-8') as csv_s_daty:
        reader = csv.DictReader(csv_s_daty)
        nazvy_sloupcu = reader.fieldnames  # nacte nazvy sloupcu
    with open(f"{overeny_vystup}.csv", mode='a', newline='', encoding='utf-8') as csv_s_daty:
        zapis_do_csv = csv.DictWriter(csv_s_daty, fieldnames=nazvy_sloupcu)
        zapis_do_csv.writerow(obec_statistiky)  # Zapsání nového řádku

def najdi_kandidujici(bs_obec:str) -> list:
    '''Funkce hleda nazev kandidujicich stran a pocet jejich hlasu v obci v bs objektu pro danou obec.
    Vraci seznam slovniku, ktere jsou usporadane tak, ze klice jsou jmena stran a hodnoty jsou
    ziskane pocty hlasu'''

    strany = list()
    for strana in bs_obec.find_all("td", class_="overflow_name"):
        jmeno_strana = strana.get_text(strip=True)
        hlasy_strana = strana.find_next_sibling('td', class_='cislo')
        
        if hlasy_strana:
            hlasy_strana = int(hlasy_strana.get_text(strip=True).replace('\xa0', ''))
            strany.append({jmeno_strana: hlasy_strana})
    return strany

def aktualizace_dat(strany_a_hlasy: list, csv_data:str):
    '''funkce vytvari aktualizovany obsah pro vysledne csv'''
    # nacita stary obsah csv
    with open(csv_data, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        jmena_sloupcu = reader.fieldnames
        data = list(reader)
    
    # sloupce pokud neexistuji
    for strana in strany_a_hlasy:
        for klic in strana.keys():
            if klic not in jmena_sloupcu:
                jmena_sloupcu.append(klic)
    
    # aktualizace sloupcu
    for row in data:
        for strana in strany_a_hlasy:
            for klic, hodnota in strana.items():
                if klic in jmena_sloupcu and row.get(klic) in (None, ''):
                    row[klic] = hodnota
    return jmena_sloupcu, data

def uloz_strany_v_obci(jmena_sloupcu_csv, data_csv, csv_data: str):    
    '''funkce zapisuje aktualizovana data o kandidujicich stranach 
    a jejich poctu hlasu, tj. SPECIFICKE statistiky do csv'''

    # zazpis dat s novymi sloupci
    with open(csv_data, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=jmena_sloupcu_csv)
        
        # Zápis hlavičky (včetně nových sloupců)
        writer.writeheader()

        # Zápis původních dat se zachováním existujících hodnot
        for row in data_csv:
            writer.writerow(row)

# volani funkci a ukladani dat do csv
if __name__ == "__main__":
    
    # Zavolani funkce na spusteni kontroly prikazu atd.
    overena_url, overeny_vystup = spusteni()
    
    # Zavolani funkce s argumenty z prikazove radky a ulozeni rozdelene odpovedy pomoci html.parser do promenne html_obce
    html_obci = vyber_ucelek(overena_url, overeny_vystup)

    # Zavolani funkce na hledani odkazu na jednotlive obce
    odkazy_obci = najdi_odkazy_obci(html_obci)
    
    # Zavolani funkce na hledani dat z jednotlivych obci
    slovnik_s_daty = ziskej_data_obci(odkazy_obci)
     
    print("Program dokoncil stahovani")
