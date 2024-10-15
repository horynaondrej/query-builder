#!/usr/bin/env python3
import logging
import os
import csv
import json
from typing import Any
from openpyxl import Workbook


class Zapsani:

    def __init__(self, cesta: str) -> None:
        self.cesta = cesta

    def vystupni_soubor(self, nazev: str) -> str:
        """ 
        Funkce vrací cestu ke vstupnímu souboru
        """
        return os.path.join(self.cesta, nazev)
    
    def zapsani_csv(self, 
            vystup: str, 
            data: list[Any],
            oddelovac: str,
            uvozovky: str = None
        ) -> None:
        """ Metoda uloží 2D seznam do CSV souboru
        
        Args:
            hlavicka: list
            data: list
            vystup: str - cesta k souboru
        
        Return:
            None
        """
        if len(data) > 0:
            try:
                with open(vystup, 'w', encoding='utf-8') as soubor:
                    w = csv.writer(
                        soubor,
                        delimiter=oddelovac,
                        quotechar=uvozovky,
                        lineterminator='\n'
                        )
                    for ity in data:
                        w.writerow(ity)
            except IOError:
                logging.info('Nezdařilo se zapsat do souboru')
        else:
            logging.info('Data pro zápis neexistují')
    
    def zapsani_seznamu(self, vystup: str, obsah: list) -> None:
        """ 
        Zápis dat do souboru s omezením na počet řádek

        Args:
            vystup: cesta k výstupnímu souboru
            obsah: data k zapsání
        """
        try:
            with open(vystup, 'w+', encoding='utf8') as soubor_vystup:
                for ity in obsah:
                    soubor_vystup.write(f'{ity}\n')
                soubor_vystup.close()
                logging.info('Upravená data zapsaná')
        except IOError:
            logging.info('Nezdařilo se zapsat do souboru')

    def zapsani_textu(self, vystup: str, obsah: str) -> None:
        """ 
        Zápis dat do souboru s omezením na počet řádek

        Args:
            vystup: cesta k výstupnímu souboru
            obsah: data k zapsání
        """
        try:
            with open(vystup, 'w+', encoding='utf8') as soubor:
                soubor.write(f'{obsah}')
                soubor.close()
                logging.info('Upravená data zapsaná')
        except IOError:
            logging.info('Nezdařilo se zapsat do souboru')  

    def zapsani_textu_do_excelu(self, vystup: str, obsah: list[Any]) -> None:
        # Vytvoření nového Excel souboru
        wb = Workbook()
        ws = wb.active

        # Zápis dat do Excelu
        for row in obsah:
            ws.append(row)

        # Uložení souboru
        wb.save(vystup)
        logging.info('Data do excelu zapsaná v pořádku.')

    def zapsani_json(self, vystup: str, slovnik: dict[Any]) -> None:
        """
        Zápis slovníku do JSON souboru
        """
        with open(vystup, 'w', encoding='utf-8') as file:
            json.dump(slovnik, file, ensure_ascii=False, indent=4)

        logging.info(f"Data byla úspěšně zapsána do souboru {vystup}")