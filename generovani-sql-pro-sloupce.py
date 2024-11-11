#!/usr/bin/env python3
import logging
import os
from cteni import Cteni
from zapsani import Zapsani


@staticmethod
def vytvoreni_prikazu(obsah: list[str]) -> str:
    """
    Sestaví příkaz pro získání seznamu sloupců u tabulek
    """
    res = ''
    t = ''
    a = 0
    for i in obsah:

        match i:
            case 'tractions_tr' | 'tractions_th':
                t = 'tractions'
            case _:
                t = i

        i = i.upper()
        t = t.upper()
        res += f"SELECT '{i}' AS TABULKA, COLUMN_NAME, COLUMN_ID FROM ALL_TAB_COLUMNS WHERE TABLE_NAME='{t}' AND OWNER='CDC_ICAR_L2'\n"
        if a != len(obsah) - 1:
            res += f"UNION ALL\n"
        a += 1

    res += f"ORDER BY TB, COLUMN_ID;\n"
    return res


# Hlavní metoda skriptu
def main():

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    print()
    logging.info('Spuštění skriptu')

    slozka = 'src'

    n = Cteni(os.path.dirname(__file__))
    vs = n.vstupni_soubor(os.path.join(slozka, 'tabulky.txt'))
    data = n.cteni_seznamu(vs)

    prikaz = vytvoreni_prikazu(data)

    n = Zapsani(os.path.dirname(__file__))
    vys = n.vystupni_soubor(os.path.join(slozka, 'sql-sloupce.sql'))
    n.zapsani_textu(
        vys,
        prikaz
    )

    logging.info('Ukončení skriptu')
    print()

# Hlavní vlákno skriptu
if __name__ == "__main__":
    main()