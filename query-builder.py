#!/usr/bin/env python3
import logging
import os
import konstanty as k
from typing import Any, Self
from cteni import Cteni
from zapsani import Zapsani


class Tabulka:

    """
    Třída pro objekt tabulka
    """
    def __init__(self, nazev: str, sloupce: list[str]) -> None:
        self.nazev: str = nazev
        self.sloupce: list[str] = sloupce

class Jadro:

    def __init__(self) -> None:
        
        # Zpracování dat se seznamem sloupců u tabulek
        n = Cteni(os.path.dirname(__file__))
        vs = n.vstupni_soubor('sloupce.txt')
        self.sloupce: list[list[str]] = n.cteni_csv(vs, 'utf8', ';')

        self.seznam_tabulek: list[str] = []
        self.tabulky: list[Tabulka] = []
        self.schema: dict = {}
        self.schema_upravena: dict = {}

    def zpracuje_seznam_tabulek(self) -> Self:
        """
        Získá seznam tabulek z dat o tabulkách a jejich sloupcích
        """
        temp: list[str] = []
        if not self.sloupce:
            return None
    
        # Přidána podmínka na hlavičku
        temp = [radek[0] for radek in self.sloupce if radek[0] != 'tabulka']
        
        # Pouze jedinečné hodnoty
        self.seznam_tabulek = list(set(temp))
        return self
    
    def zpracuj_sloupce_tabulky(self, tabulka: str) -> list[str]:
        """
        Vrací seznam sloupců vybrané tabulky
        """
        temp: list[str] = []

        for i in self.sloupce:
            if i[1] != 'sloupec' and i[0] == tabulka:
                temp.append(i[1])

        return temp
    
    def vytvoreni_objektu_tabulek(self) -> Self:
        """
        Vytvoří seznam objektů tabulek se sloupci
        """
        temp: list[Tabulka] = []

        # Vytvoří jednotlivé tabulky ve třídách
        for i in self.seznam_tabulek:
            temp.append(Tabulka(i, self.zpracuj_sloupce_tabulky(i)))

        self.tabulky = temp
        return self
     
    def vytvoreni_schemat(self) -> Self:
        """
        Vytvoření schémat ze sloupců tabulek
        """
        slovnik: dict = {}

        for i in self.tabulky:
            radek: dict = {}
            for j in i.sloupce:
                radek[j] = 0

            # Vytvoří slovník pro danou tabulku
            slovnik.setdefault(i.nazev, {})
            # Vytvoří slovník pro sloupce 
            slovnik.get(i.nazev).setdefault('sloupce', {})
            # Vytvoří klíč a hodnotu pro alias tabulky
            slovnik.get(i.nazev).setdefault('alias', '')
            # Vloží seznam sloupců do slovníku Sloupce
            slovnik.get(i.nazev).get('sloupce').update(radek)

        self.schema = slovnik
        return self
    
    def ziskat_klic_a_hodnotu(self, slovnik: dict[Any], klic: str) -> dict[Any]:
        """ 
        Funkce pro získání klíče a jeho hodnoty, důvodem je
        aby se zapsaly JSON pro každou tabulku, ty jsou
        předtím ve společném slovníku
        """
        if klic in slovnik:
            return {klic: slovnik[klic]}
        else:
            return None
        
    def zapsani_schemat_do_souboru(self) -> None:
        """
        Metoda projde seznam tabulek a u každé 
        tabulky zapíše JSON schéma do souboru
        """
        n = Zapsani(os.path.dirname(__file__))

        for i in self.seznam_tabulek:
            vys = n.vystupni_soubor(f'{i}.txt')

            # zkontroluje, zda již soubory neexistují 
            if not os.path.exists(vys):
                n.zapsani_json(
                    vys,
                    self.ziskat_klic_a_hodnotu(self.schema, i)
                )
            else:
                logging.info('Soubory již existují, takže se nezapsaly.')

    def nacteni_schemat_ze_souboru(self) -> Self:
        """
        Načti upravená schémata z textových souborů
        """
        n = Cteni(os.path.dirname(__file__))

        for i in self.seznam_tabulek:
            vs = n.vstupni_soubor(f'{i}.txt')

            if os.path.exists(vs):
                data = n.cteni_json(vs)
            else:
                logging.info('Soubory s daty tabulek neexistují!')

            self.schema_upravena.update(data)
        return self
    
    def porovnani(self, generovane, editovane) -> dict[Any]:
        """
        Tato rekurzivní metoda zjišťuje, zda nepřibyly nové klíče
        """

        for key in generovane:
            if key in editovane:
                if isinstance(generovane[key], dict) and isinstance(editovane[key], dict):
                    editovane[key] = self.porovnani(generovane[key], editovane[key])
            else:
                print(f'klíč není: {key}')
                editovane.setdefault(key)
                editovane[key] = 0

        return editovane
    
    def porovna_a_zapise_schema(self) -> Self:
        """
        Tato metoda porovná generované schéma s již editovaným
        """
        if self.schema_upravena is not None:
            self.schema_upravena = self.porovnani(self.schema, self.schema_upravena)
            n = Zapsani(os.path.dirname(__file__))
            for i in self.seznam_tabulek:
                vys = n.vystupni_soubor(f'{i}.txt')

                n.zapsani_json(
                    vys,
                    self.ziskat_klic_a_hodnotu(self.schema_upravena, i)
                )
    

# Hlavní metoda skriptu
def main():

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    print()
    logging.info('Spuštění skriptu')

    jadro = Jadro()
    jadro.zpracuje_seznam_tabulek()
    jadro.vytvoreni_objektu_tabulek()
    jadro.vytvoreni_schemat()
    jadro.zapsani_schemat_do_souboru()
    jadro.nacteni_schemat_ze_souboru()
    jadro.porovna_a_zapise_schema()

    print(jadro.schema)
    print(jadro.schema_upravena)

    logging.info('Ukončení skriptu')
    print()

# Hlavní vlákno skriptu
if __name__ == "__main__":
    main()