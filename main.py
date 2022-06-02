# Juan Diego Solorzano 18151
# Proyecto 3 generador de analizadores sintacticos

from PySimpleAutomata import automata_IO
import os
import json
from Node import Node
from AFN import AFN
from Subconjuntos import Subconjuntos
from Lector import Lector
from Generador import Generador

print('\nProyecto 2: Diseno de Lenguajes de Programacion')
success = False
while success == False:
    filename = input('\nIngrese el nombre del archivo COCOl: ')
    try:
        archivoCoco = open(filename)
    except IOError:
        print('Error al abrir archivo')
        continue
    
    success = True
    archivoCoco.close()
    lector = Lector(filename)
    tokens = lector.getTokens()
    keywords = lector.getKeywords()
    characters = lector.getCharacters()
    productions = lector.getProductions()
    anons = lector.getTokensAnon()
    for i in productions:
        print(i.id)
        print(i.params)
        print(i.value)
    
    generador = Generador(tokens, keywords, characters, anons, productions)
    generador.analizeGrammar()
