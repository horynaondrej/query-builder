#!/usr/bin/env python3
import logging
import os
import csv
import json
from typing import Any


class Cteni:

    def __init__(self, cesta: str) -> None:
        self.cesta = cesta

    def vstupni_soubor(self, nazev: str) -> str:
        """ 
        Funkce vrací cestu ke vstupnímu souboru
        """
        return os.path.join(self.cesta, nazev)
    
    def cteni_csv(
            self, 
            vstup: str,
            kodovani: str,
            oddelovac: str,
            uvozovky: str = None
        ) -> list[list[str]]:
        """ 
        Otevření vstupního souboru s daty a jeho načtení 
        do seznamu s celými řádky

        Args:
            vystup: url s názvem vstupního souboru k načtení

        Return:
            seznam s celými řádky načteného souboru, bez hlavičky
        """
        obsah = []

        if not os.path.exists(vstup):
            logging.info('Soubor s daty neexistuje.')
            return None

        try:
            with open(vstup, 'r', encoding=kodovani) as f:
                reader = csv.reader(f, delimiter=oddelovac, quotechar=uvozovky)
                obsah = list(reader)
                print('Data načtená')
        except IOError:
            print('Nepodařilo se číst ze souboru s daty')
        finally:
            return obsah

    def cteni_seznamu(self, 
            vstup: str, 
            kodovani: str = 'utf8',
            ukonceni: str = None,
            uvozovky: str = None
        ) -> list[str]:
        """
        Metoda přečte soubor s jednoduchým sezname řádek po řádku
        """
        data = []

        if not os.path.exists(vstup):
            logging.info('Soubor s daty neexistuje.')
            return None

        try:
            with open(vstup, 'r', encoding=kodovani) as s:
                data = [line.rstrip() for line in s]
                if ukonceni is not None:
                    data = [line.replace(ukonceni, '') for line in data]
                if uvozovky is not None:
                    data = [line.replace(uvozovky, '') for line in data]
                s.close()
                logging.info('Data načtená v pořádku')
        except IOError:
            logging.info('Nepodařilo se číst ze souboru s daty')
        finally:
            return data
        
    def cteni_json(self, vstup: str) -> Any:
        """
        Metoda načte JSON z textového souboru a vrátí 
        JSON objekt

        Args:
            vstup: cesta k souboru i s názvem a typem

        Returns:
            JSON objekt
        """
        with open(vstup, 'r', encoding='utf8') as file:
            data = file.read()

        # Převod textu na Python objekt
        js = json.loads(data)

        logging.info('Data JSON úspěšně načtená a zpracovaná.')
        return js

