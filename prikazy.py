#!/usr/bin/env python3
import logging
import os
from query_builder import Schema


# Hlavní metoda skriptu
def main():

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    print()
    logging.info('Spuštění skriptu')


    schema = Schema(os.path.dirname(__file__))
    schema.vytvoreni_slozky_se_soubory()
    schema.nacteni_seznamu_tabulek()
    schema.vytvoreni_prikazu()


    logging.info('Ukončení skriptu')
    print()

# Hlavní vlákno skriptu
if __name__ == "__main__":
    main()