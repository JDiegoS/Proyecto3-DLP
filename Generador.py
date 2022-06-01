# Juan Diego Solorzano 18151
# Proyecto 1 Automatas

from PySimpleAutomata import automata_IO
import os
import json
from Node import Node
from AFN import AFN
from Subconjuntos import Subconjuntos

from Node import Node
class Generador(object):
    # Clase para construir AFN

    def __init__(self, tokens, keywords, characters):
        self.tokens = tokens
        self.keywords = keywords
        self.characters = characters
        self.operaciones = ['(', ')', '|', '{', '}', '[', ']']
        self.expressions = []
        self.tokensAccepted = []
        self.tokenStates = []

        os.environ["PATH"] += os.pathsep + 'C:/Program Files/graphviz/bin'

        print("Analizando la gramatica...")
        self.analizeGrammar()

        # Verificar que se cierren los parentesis y kleene
        for i in self.expressions:
            arr = list(i)
            if arr.count('(') != arr.count(')') or arr.count('{') != arr.count('}') or arr.count('[') != arr.count(']'):
                print('\nError. No se cerro un (, { o [\n')
                quit()

        # Construir AFN
        alphabetfinal = []
        graph = {
            "alphabet": alphabetfinal,
            "states": [],
            "initial_states": "0",
            "accepting_states": [],
            "transitions": [],
        }

        index = 0
        for i in self.expressions:
            currentAlphabet = []
            for j in i:
                if j not in self.operaciones:
                    currentAlphabet.append(j)
                    if j not in alphabetfinal:
                        alphabetfinal.append(j)
            self.generateAFN(list(i), currentAlphabet, graph, self.tokens[index].id)
            index += 1

        print("Generando AFN (Thompson)...")
        self.graphAFN(graph)
        afd = self.generateAFD(graph, alphabetfinal)

        #self.simulateA(afd)
        #self.simulateFile(afd)
        self.generateFile(afd)


    def analizeGrammar(self):
        # En cada token, convertir ids de caracteres a sus alfabetos
        finalExpression = []
        for i in self.tokens:
            currentToken = i.value
            currentToken = currentToken.replace('"', '')
            nextIndex = 0
            for j in self.characters:
                nextIndex +=1
                goNext = False
                # Buscar si el id del caracter se encuentra en el token
                character = currentToken.find(j.id)
                if character != -1:
                    for c in self.characters[nextIndex:]:
                        # Verificar que se este usando el caracter correcto (problemas como digito y digitoHex)
                        if currentToken.find(c.id) == character:
                            goNext = True
                    if goNext:
                        goNext = False
                        continue
                    currentAlphabet = '('
                    if len(j.alphabet) == 1:
                        currentAlphabet = j.alphabet[0]
                    else:
                        currentAlphabet = (currentAlphabet * (len(j.alphabet)-1)) + j.alphabet[0]
                        for a in j.alphabet[1:]:
                            # Agregar OR para cada valor del alfabeto
                            currentAlphabet += '|' + a + ')'
                    # Reemplazar el id del caracter por su alfabeto
                    currentToken = currentToken.replace(j.id, currentAlphabet)
                
            # Agregar expresion al arreglo final
            finalExpression.append(currentToken)
        self.expressions = finalExpression
            

    def generateAFN(self, arr, alphabet, graph, tokens):
        # Crear AFN en base al alfabeto
        afn = AFN(arr, alphabet)
        afn_nodes = afn.generateAFN()

        newAccepted = []
        if graph['states'] == []:
            nextIndex = 1
        else:
            nextIndex = int(graph['states'][-1]) + 1
        graph['transitions'].append(['0', 'epsilon', str(int(afn_nodes[0].state) + nextIndex)])
        for i in afn_nodes:
            if str(int(i.state) + nextIndex) not in graph['states']:
                graph['states'].append(str(int(i.state) + nextIndex))
                if i.accepted == True:
                    newAccepted.append(str(int(i.state) + nextIndex))
                    graph['accepting_states'].append(str(int(i.state) + nextIndex))
                for t in i.transitions:
                    graph['transitions'].append([str(int(t[0]) + nextIndex), t[1], str(int(i.state) + nextIndex)])

        for i in newAccepted:
            self.tokensAccepted.append([i, tokens])

    
    def graphAFN(self, graph):
        # Crear grafica del AFN
        with open('digraph.json', 'w') as outfile:
            json.dump(graph, outfile)
        dfa_example = automata_IO.nfa_json_importer('./digraph.json')
        automata_IO.nfa_to_dot(dfa_example, 'thompsonAFN', './')

    def generateAFD(self, graph, alphabet):
        # Crear y graficar AFD
        print("Generando AFD (Construccion de subconjuntos)...")
        afd_sub = Subconjuntos(graph['states'], graph['transitions'], alphabet, graph['accepting_states'], self.tokensAccepted)
        afd_snodes = afd_sub.generateAFD()
        graph2 = {
            "alphabet": alphabet,
            "states": [],
            "initial_state": "s0",
            "accepting_states": [],
            "transitions": [],
        }

        for i in afd_snodes:
            if i.state not in graph2['states']:
                graph2['states'].append(str(i.state))
                if i.accepted == True:
                    graph2['accepting_states'].append(str(i.state))
                for t in i.transitions:
                    graph2['transitions'].append([str(t[0]), t[1], str(i.state)])

        self.tokenStates = afd_sub.getTokensAccepted()
        # Graficar tarda mucho
        '''
        with open('digraph2.json', 'w') as outfile:
            json.dump(graph2, outfile)
        dfa_example = automata_IO.dfa_json_importer('./digraph2.json')
        automata_IO.dfa_to_dot(dfa_example, 'subconjuntosAFD', './')
        '''
        return graph2

    def generateFile(self, graph):
        f = open("generado.py", "w")
        f.write("graph = " + str(graph))
        keys = []
        for i in self.keywords:
            keys.append([i.id, i.value])
        f.write("\nkeywords = " + str(keys))
        f.write("\ntokenStates = " + str(self.tokenStates))
        f.write('''

enter = chr(92) + chr(110)
def simulateFile(graph, keywords, tokenStates):
    #Simular archivo txt
    success = False
    while success == False:
        print()
        filename = input('Ingrese el nombre del archivo: ')
        if filename[-4:] != '.txt':
            print('Formato invalido')
            continue
        try:
            archivoTexto = open(filename)
        except IOError:
            print('Error al abrir archivo')
            continue
        success = True
    fileLines = archivoTexto.readlines()
    tokens = []
    for i in fileLines:
        i = i.replace(enter, '')
        cadena = list(i)
        cadena.append('e')
        done = False
        index = 0
        while done == False:
            #Probar caracter por carcter hasta encontrar el token mas grande
            i = index
            passedAccepted = []
            
            currentChain = ''
            lastAccepted = 0
            lastToken = ''
            empty = False
            maybeKeyword = False
            while (i != len(cadena)-1):
                currentChain += cadena[i]
                currentToken = simulateWord(graph, currentChain, keywords, tokenStates)
                passedAccepted.append([currentToken[0], currentChain])
                if(currentToken[0] != "NO ES ACEPTADO POR LA GRAMATICA"):
                    lastAccepted = i
                    lastToken = currentToken[0]
                elif currentToken[1] == 's0':
                    
                    for k in keywords:
                        if k[1].find(currentChain) != -1:
                            maybeKeyword = True
                            break
                    if maybeKeyword == False:
                        empty = True
                        break
                i+=1
                if i == len(cadena)-1 and lastToken == '':
                    #No se acepta en el analizador
                    tokens.append('NO SE ACEPTA')
                    empty = True
            if empty == False:
                index = lastAccepted + 1
                tokens.append(lastToken)
                
            else:
                index += 1
            if index == len(cadena)-1:
                break
            
    print()
    print('Resultado: ')
    res = ''
    for i in tokens:
        res += i + ' '
    print(res)
    print()


def simulateWord(graph, opc, keywords, tokenStates):
    # Simular una palabra
    found = False
    for i in keywords:
        if opc == i[1]:
            return [i[0], 's1']

    if found != True:
        cadena = list(opc)
        if len(cadena) == 0:
            if 's0' in graph['accepting_states']:
                for i in tokenStates:
                    if i[0] == 's0':
                        return [i[1], 's1']
            else:
                return ["NO ES ACEPTADO POR LA GRAMATICA", 's0']
        else:
            s = 's0'
            c = cadena[0]
            i = 0
            cadena.append('eof')
            while (c != 'eof'):
                cambio = False
                # Mover(s,c)
                for j in graph['transitions']:
                    if j[0] == s and j[1] == c:
                        s = j[2]
                        cambio = True
                        break
                if cambio == False:
                    break
                # Siguiente caracter
                i+=1
                c = cadena[i]
            if (s in graph['accepting_states'] and cambio):
                for i in tokenStates:
                    if i[0] == s:
                        return [i[1], s]
            else:
                return ["NO ES ACEPTADO POR LA GRAMATICA", s]

simulateFile(graph, keywords, tokenStates)
            ''')
    
    def simulateA(self, graph):
        # Simular AFD
        opc = input('\nIngrese una cadena para evaluar (q para salir): ')
        while opc != 'q':
            found = False
            for i in self.keywords:
                if opc == i.value:
                    print(i.id)
                    found = True
                    break

            if found != True:
                cadena = list(opc)
                if len(cadena) == 0:
                    if 's0' in graph['accepting_states']:
                        print('SI CON SUBCONJUNTOS')
                    else:
                        print("NO CON SUBCONJUNTOS")
                else:
                    s = 's0'
                    c = cadena[0]
                    i = 0
                    cadena.append('eof')
                    while (c != 'eof'):
                        cambio = False
                        # Mover(s,c)
                        for j in graph['transitions']:
                            if j[0] == s and j[1] == c:
                                s = j[2]
                                cambio = True
                                print(s)
                                break
                        if cambio == False:
                            break
                        # Siguiente caracter
                        i+=1
                        c = cadena[i]
                    if (s in graph['accepting_states'] and cambio):
                        #print('SI CON SUBCONJUNTOS')
                        for i in self.tokenStates:
                            if i[0] == s:
                                print(i[1])
                                break
                    else:
                        print("NO ES ACEPTADO POR LA GRAMATICA")
            
            opc = input('\nIngrese una cadena para evaluar (q para salir): ')
            

