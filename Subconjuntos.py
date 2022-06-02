from AFN import AFN
from Node import Node

class Subconjuntos(object):
    def __init__(self, states, transitions, alphabet, accepted, tokens):
        self.states = states
        self.transitions = transitions
        self.alphabet = alphabet
        self.table = [['Conjunto de estados'],['Estado del AFD']]
        self.state = 0
        self.accepted = accepted
        self.newAccepted = []
        self.nodes = []
        self.tokens = tokens
        self.tokensAccepted = []
        for i in alphabet:
            self.table.append([i])

    def getTokensAccepted(self):
        return self.tokensAccepted

    def cerraduraEpsilon(self, states):
        # Buscar a que estados se puede llegar con epsilon
        conjunto = []
        for s in states:
            if s not in conjunto:
                conjunto.append(s)
        for i in self.transitions:
            if i[2] not in conjunto and i[0] in states and i[1] == 'epsilon':
                conjunto.append(i[2])        
        return conjunto

    def mover(self, states, value):
        # Buscar a que estados se puede llegar con value
        conjunto = []
        for i in self.transitions:
            if i[2] not in conjunto and i[0] in states and i[1] == value:
                conjunto.append(i[2])        
        return conjunto

    def addState(self, conj):
        # Agregar nuevo estado a la tabla
        self.table[0].append(conj)
        self.table[1].append('s'+str(self.state))

    def getNodes(self):
        # Genera los nodos del AFD
        num = 0
        for i in self.table[1]:
            if i[0] == 's':
                accepted = i in self.newAccepted
                self.nodes.append(Node(i, [], accepted))
                letter = 2
                for a in self.alphabet:
                    state = -1
                    for j in self.table[letter]:
                        if j == i:
                            self.nodes[num].transitions.append(['s'+str(state), a])
                        state+=1
                    letter += 1
                num += 1

    def generateAFD(self):
        # Genera el AFD
        building = True
        currentC = '0'
        cIndex = 1
        while building:
            conj = self.cerraduraEpsilon(currentC)
            searching = True
            while searching:
                # Cerradura de epsilon
                nConjunto = self.cerraduraEpsilon(conj)
                if nConjunto == conj:
                    searching = False
                else:
                    conj = nConjunto
            conj.sort()
            if len(conj) > 0:
                if conj not in self.table[0]:
                    # Agregar nuevo estado
                    self.addState(conj)
                    for i in self.accepted:
                        if i in conj:
                            self.newAccepted.append('s'+str(self.state))
                    self.state += 1
            nChar = 2
            for i in self.alphabet:
                # Buscar transiciones del estado
                trans = self.mover(conj, i)
                trans.sort()

                conj2 = self.cerraduraEpsilon(trans)
                searching = True
                while searching:
                    nConjunto = self.cerraduraEpsilon(conj2)
                    if nConjunto == conj2:
                        searching = False
                    else:
                        conj2 = nConjunto
                conj2.sort()
                if len(conj2) > 0:
                    if conj2 not in self.table[0]:
                        # Si no esta en la tabla, agregar estado
                        self.addState(conj2)
                        self.table[nChar].append('s'+str(self.state))
                        # Agregar estado aceptado junto con su token
                        for i in self.accepted:
                            if i in conj2:
                                for j in self.tokens:
                                    if j[0] == i:
                                        self.tokensAccepted.append(['s'+str(self.state), j[1]])
                                self.newAccepted.append('s'+str(self.state))
                        self.state += 1
                    else:
                        # Agregar transicion
                        indx = self.table[0].index(conj2)
                        self.table[nChar].append('s'+str(indx-1))
                else:
                    # No tiene transicion
                    self.table[nChar].append('none')
                nChar += 1
            cIndex += 1
            if len(self.table[0]) == len(self.table[-1]):
                # Se lleno la tabla
                building = False
            else:
                # Siguiente estado
                currentC = self.table[0][cIndex]
  
        self.getNodes()
        #print(self.table)

        return self.nodes