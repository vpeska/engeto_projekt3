Pro spusteni skriptu je vhodne vytvorit nove virtualni prostredi a aktivovat ho:

>python -m venv venv

>source venv/bin/activate

(windows) >venv\Scripts\activate

Potrebne knihovny je mozne instalovat v tomto prostredi pomoci prilozeneho souboru requirements.txt:

>pip install -r requirements.txt

Skript main.py pak stahuje statistiky z voleb ze stranek na teto adrese:

https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ

Funguje tak, ze se v terminalu spousti jako skript se dvema argumenty.
Prvnim argumentem je URL odkaz (ohraniceny uvozovkami) na uzemni celek, pro ktery se maji statistiky stahovat. Tento odkaz se ziska pod X ve sloupci "Vyber obce". Napriklad "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2105" pro uzemni celek Kutna Hora. Druhy argument je nazev csv souboru (bez pripony), do ktereho se maji statistiky ukladat, napriklad "statistiky_kutna_hora".

Ukazka spousteni:

>python3 main.py 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2105' statistiky_kutna_hora

Pri uspesnem spusteni:
Zacinam stahovat data z https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2105 a ukladam do csv souboru s unicode UTF-8 statistiky_kutna_hora.csv
Program dokoncil stahovani

Pri neexistujici nebo nereagujici URL napriklad:

Error: HTTPSConnectionPool(host='voby.cz', port=443): Max retries exceeded with url: /pls/ps2017nss/ps32?xjazyk=CZ&xkraj=8&xnumnuts=5205 (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x0000025A869799D0>, 'Connection to voby.cz timed out. (connect timeout=None)'))
Chyba pri zadani: Prvni argument neni funkcni URL nebo stranka nereaguje.

Pri spatne zadanem nazvu csv souboru, napriklad pri zadavani kutna_hora.csv:
Chyba pri zadani: Neplatny nazev souboru. Povoleny jsou jen alfanumericke znaky, podtrzitko a pomlcka. Nazev nesmi zahrnovat priponu .csv ani jinou.

Pokud se zada funkcni URL ale nespravna adresa nez jsou odkazy popsane na zacatku, tak skript probehne bez hlaseni chyb, ale vysledna tabulka csv neobsahuje relevantni data voleb.
