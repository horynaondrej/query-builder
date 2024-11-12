#!/usr/bin/env python3
import logging
import os
from query_builder import Jadro


# Hlavní metoda skriptu
def main():

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    print()
    logging.info('Spuštění skriptu')

    jadro = Jadro(os.path.dirname(__file__))
    jadro.naformatuje_zdrojovy_soubor()
    jadro.zpracuje_seznam_tabulek()
    jadro.vytvoreni_objektu_tabulek()
    jadro.vytvoreni_schemat()
    jadro.zapsani_schemat_do_souboru()
    jadro.nacteni_schemat_ze_souboru()
    jadro.porovna_a_zapise_schema()

    jadro.nacteni_schemat_ze_souboru()
    jadro.filtruj_sloupce()
    jadro.filtruj_nepouzite_tabulky()
    jadro.doplneni_atributu()
    jadro.zapsani_celkoveho_schema_do_souboru()
    jadro.nacteni_celkoveho_schema_ze_souboru()
    jadro.porovna_a_zapise_celkove_schema()

    jadro.priprava_pro_sql()
    jadro.priprava_joinu_pro_sql()
    jadro.zapsani_join_schema_do_souboru()
    jadro.nacteni_join_schema_ze_souboru()
    jadro.porovna_a_zapise_join_schema()
    jadro.zpracovani_joinu()
    jadro.sestaveni_sql()
    jadro.ulozeni_vysledneho_sql()

    logging.info('Ukončení skriptu')
    print()

# Hlavní vlákno skriptu
if __name__ == "__main__":
    main()
