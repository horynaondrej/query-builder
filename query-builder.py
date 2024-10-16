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

        self.mezera = '    '
        
        # Zpracování dat se seznamem sloupců u tabulek
        n = Cteni(os.path.dirname(__file__))
        vs = n.vstupni_soubor('sloupce.txt')
        self.sloupce: list[list[str]] = n.cteni_csv(vs, 'utf8', ';')

        self.seznam_tabulek: list[str] = []
        self.tabulky: list[Tabulka] = []
        self.schema: dict = {}
        self.schema_upravena: dict = {}
        self.schema_vysledne: dict = {}
        self.schema_pro_sql: dict = {}
        
        self.joiny: dict = {}
        self.joiny_vysledne: dict = {}

        self.vychozi_tabulka: str = ''

        self.priznak_group_by = False
        self.priznak_joinu = False

        self._from = []
        self._aggs = []
        # sloupce a group by je nutné dělat zvlášť, protože
        # sloupce můžou mít aliasy 
        self._gb = []
        self._where = []
        self._sloupce = []
        self._joiny = []

        self.prikaz = ''

    def naformatuje_zdrojovy_soubor(self) -> Self:
        """
        Zmenší písmo ve zdrojovm soubory s tabulkami a sloupci
        """
        self.sloupce = [[j.lower() for j in i] for i in self.sloupce]
        return self

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
        return self

    def filtruj_sloupce(self) -> Self:
        """
        Když je u sloupce uvedená 1, metoda zpracuje
        sloupec do výsledného SQL příkazu
        """
        vysledne = {}

        for kategorie, obsah in self.schema_upravena.items():
            vysledne[kategorie] = {'sloupce': {}, 'alias': obsah['alias']}
            
            for sloupec, hodnota in obsah['sloupce'].items():
                if hodnota == 1:
                    vysledne[kategorie]['sloupce'][f'{kategorie}.{sloupec}'] = hodnota

        self.schema_vysledne = vysledne
        return self
    
    def filtruj_nepouzite_tabulky(self) -> Self:
        """
        Když není některé z tabulek použitá, odebere
        ji z výsledného schéma
        """
        vysledne = {}

        for i, ihod in self.schema_vysledne.items():
            if ihod.get('sloupce'):
                vysledne[i] = ihod
        
        self.schema_vysledne = vysledne
        return self

    def doplneni_atributu(self) -> Self:
        """
        Doplní atributy ke sloupcům jako agregace, alias sloupce
        """
        # projdi tabulky
        for i, ihod in self.schema_vysledne.items():
            # projdi sloupce tabulky
            for j, jhod in ihod['sloupce'].items():
                # u každého sloupce přidej následující atributy
                ihod['sloupce'][j] = {'agg': '', 'alias': '', 'podminky': [['', '']]}

    def zapsani_celkoveho_schema_do_souboru(self) -> None:
        """
        Metoda projde seznam tabulek a u každé 
        tabulky zapíše JSON schéma do souboru
        """
        n = Zapsani(os.path.dirname(__file__))

        vys = n.vystupni_soubor(f'celkove.txt')
        
        # zkontroluje, zda již soubory neexistují 
        if not os.path.exists(vys):
            n.zapsani_json(
                vys,
                self.schema_vysledne
            )
    
    def nacteni_celkoveho_schema_ze_souboru(self) -> dict[Any]:
        """
        Načti upravené celkové schéma ze souboru
        """
        n = Cteni(os.path.dirname(__file__))

        vs = n.vstupni_soubor(f'celkove.txt')
        
        if os.path.exists(vs):
            data = n.cteni_json(vs)
        else:
            logging.info('Celkový soubor s daty tabulek neexistuje!')
        self.schema_pro_sql.update(data)

    def doplneni_atributu_do_clk_schema(self) -> Self:
        """
        Protože se u již vytvořených částí celkového schéma 
        nedoplňují klíče jako AGG nebo ALIAS, 
        musí se doplnit expost
        """
        for i, ihod in self.schema_pro_sql.items():
            # projdi sloupce tabulky
            for j, jhod in ihod['sloupce'].items():
                # když sloupec nemá slovník s atributy
                # musí se přidat
                if jhod == 0:
                    ihod['sloupce'][j] = {'agg': '', 'alias': '', 'podminky': [['', '']]}
                if jhod['podminky'] == 0:
                    jhod['podminky'] = [['', '']]
        return self

    def porovna_a_zapise_celkove_schema(self) -> Self:
        """
        Tato metoda porovná generované schéma s již editovaným
        """
        if self.schema_pro_sql is not None:
            self.schema_pro_sql = self.porovnani(self.schema_vysledne, self.schema_pro_sql)

            # kontrola atributů sloupce
            self.doplneni_atributu_do_clk_schema()

            n = Zapsani(os.path.dirname(__file__))
            vys = n.vystupni_soubor(f'celkove.txt')

            n.zapsani_json(
                vys,
                self.schema_pro_sql
            )
        return self

    def kontrola_2d_pole(self, arr: list[Any]) -> bool:
        """
        Kontrola 2d pole, které se používá například 
        u JOINů nebo podmínek WHERE
        """
        res = False
        for radek in arr:
            for clen in radek:
                if clen != '':
                    res = True
        return res
    
    def priprava_pro_sql(self) -> Self:
        """
        Zpracuje výsledný JSON pro sestavení SQL dotazu
        """
        # projdi celkové schéma
        for i, ihod in self.schema_pro_sql.items():
            # do klauzule FROM přidej všechny tabulky
            self._from.append(i)
            # projdi část schéma se sloupci
            for j, jhod in ihod['sloupce'].items():
                # kontrola, zda se jedná o sloupce
                if isinstance(jhod, dict):
                    _temp = ''
                    _func = ''
                    _agg = ''
                    _whe = ''
                    # když je hodnota agregace prázdná
                    if jhod.get('agg') == '':
                        # přidej do výsledku jen čistý sloupec
                        _func += j
                        self._gb.append(j)
                    # když je nastavená agregace
                    if jhod.get('agg') != '':
                        self.priznak_group_by = True
                        # přidej tyto sloupce s agregací do seznamu
                        # tak obal sloupec agregační funkcí
                        _agg += jhod.get('agg')
                        _agg += f'({j})'
                        # a nastav příznak agregace na True
                    if jhod.get('alias') != '':
                        # když není alias sloupce prázdný, 
                        # tak přidej alias sloupce
                        _temp += ' as '
                        _temp += jhod.get('alias')
                    # plus ještě kontrola aliasu 
                    # i pro agregované sloupce
                    # když je agregace
                    if jhod.get('agg') != '':
                        # tak přidej její alias
                        _agg += _temp
                    else:
                        # jinak přidej alias jen ke sloupci
                        _func += _temp
                    podminky = jhod.get('podminky')
                    b = 1
                    if self.kontrola_2d_pole(podminky):
                        for p in podminky:
                            # sloupec, operátor, hodnota
                            _whe += f'{j} {p[0]} {p[1]}'
                            # dokud je b menší než délka podmínek
                            # přidávej operátor AND
                            if b < len(podminky):
                                _whe += ' and '
                            b += 1
                    if _agg:
                        self._aggs.append(_agg)
                    if _func:
                        self._sloupce.append(_func)
                    if _whe:
                        self._where.append(_whe)
        return self
    
    def priprava_joinu_pro_sql(self) -> Self:
        """
        Metoda pro sestavení Joinů
        """
        res: dict = {}
        for i in self.seznam_tabulek:
            res[i] = {
                'vychozi': 0, 
                # typ vazby, vazba
                'vazba': [
                    ['', '']
                ]
            }

        self.joiny = res
        return self
    
    def zapsani_join_schema_do_souboru(self) -> None:
        """
        Metoda projde seznam tabulek a u každé 
        tabulky zapíše JSON schéma do souboru
        """
        n = Zapsani(os.path.dirname(__file__))

        vys = n.vystupni_soubor(f'joiny.txt')

        # zkontroluje, zda již soubory neexistují 
        if not os.path.exists(vys):
            n.zapsani_json(
                vys,
                self.joiny
            )

    def nacteni_join_schema_ze_souboru(self) -> dict[Any]:
        """
        Načti upravené celkové schéma ze souboru
        """
        n = Cteni(os.path.dirname(__file__))

        vs = n.vstupni_soubor(f'joiny.txt')
        
        if os.path.exists(vs):
            data = n.cteni_json(vs)
        else:
            logging.info('Celkový soubor s daty tabulek neexistuje!')
        self.joiny_vysledne.update(data)

    def porovna_a_zapise_join_schema(self) -> Self:
        """
        Tato metoda porovná generované schéma s již editovaným
        """
        if self.joiny_vysledne is not None:
            self.joiny_vysledne = self.porovnani(self.joiny, self.joiny_vysledne)
            n = Zapsani(os.path.dirname(__file__))
            vys = n.vystupni_soubor(f'joiny.txt')

            n.zapsani_json(
                vys,
                self.joiny_vysledne
            )
        return self

    def zpracovani_joinu(self) -> Self:
        """
        Zpracuje definované joiny a přidá je do sql dotazu
        """
        res: list = []

        for i, ihod in self.joiny_vysledne.items():
            vz: str = ''
            if ihod.get('vychozi') == 1:
                self.vychozi_tabulka = i

            vazby = ihod.get('vazba')
            if isinstance(vazby, list):
                # vrací boolean
                if self.kontrola_2d_pole(vazby):
                     for i in vazby:
                        vz += i[0]
                        vz += ' '
                        vz += i[1]
                        res.append(vz)

        # ještě ověř, zda zde vůbec nějaké joiny jsou
        if len(res) > 0:
            self.priznak_joinu = True

        self._joiny = res
        return self
    
    def zretezeni_casti_prikazu(self, arg: list[Any], carka: bool) -> str:
        """
        Pomocná funkce pro zřetězení seznamu hodnot do 
        výsledného řetězce
        """
        res = f'{self.mezera}'
        res += f',\n{self.mezera}'.join(arg)

        if carka:
            res += ',\n'
        else:
            res += '\n'
        return res
    
    def sestaveni_sql(self) -> Self:
        """
        Sestavení SQL příkazu

        """

        prikaz = 'select\n'
        if self.priznak_group_by:
            prikaz += self.zretezeni_casti_prikazu(self._sloupce, True)
        else:
            prikaz += self.zretezeni_casti_prikazu(self._sloupce, False)

        if self.priznak_group_by:
            prikaz += self.zretezeni_casti_prikazu(self._aggs, False)

        prikaz += 'from '
        prikaz += self.vychozi_tabulka + '\n'
        if self.priznak_joinu:
            prikaz += "\n".join(self._joiny) + '\n'

        if len(self._where) > 0:
            prikaz += 'where '
            prikaz += "\nand ".join(self._where) + '\n'
            
        if self.priznak_group_by:
            prikaz += self.zretezeni_casti_prikazu(self._gb, False)

        self.prikaz = prikaz
        return self

# Hlavní metoda skriptu
def main():

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    print()
    logging.info('Spuštění skriptu')

    jadro = Jadro()
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

    # print(jadro.sloupce)
    # print(jadro.seznam_tabulek)
    # print(jadro.tabulky)
    # print(jadro.schema)
    # print(jadro.schema_upravena)
    # print(jadro.schema_vysledne)
    # print(jadro.schema_pro_sql)
    # print(jadro.joiny)
    # print(jadro.joiny_vysledne)
    # print(jadro._aggs)
    # print(jadro._sloupce)
    # print(jadro._joiny)
    print(jadro._where)
    print()
    print(jadro.prikaz)

    logging.info('Ukončení skriptu')
    print()

# Hlavní vlákno skriptu
if __name__ == "__main__":
    main()