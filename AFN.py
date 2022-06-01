from Node import Node
class AFN(object):
    # Clase para construir AFN

    def __init__(self, arr, alphabet):
        self.arr = arr
        self.nodes = []
        self.alphabet = alphabet
        self.state = 1
        self.skip = 0
        self.orAccepted = False
        self.operaciones = ['(', ')', '|', '{', '}', '[', ']']
        self.lastOrOrigin = 0
        self.lastOrUnion = 0
        self.lastState = 0
        self.klposAccepted = False

    def changeState(self, state):
        self.state = state

    def changeLastState(self, state):
        self.lastState = state

    def orOp(self, state, position, accepted):
        self.nodes.append(Node(str(state), [[str(state-1), 'epsilon']], False))
        self.lastOrOrigin = state

        self.nodes.append(Node(str(state+1), [[str(state), 'epsilon']], False))
        self.nodes.append(Node(str(state+2), [[str(state+1), self.arr[position-1]]], False))

        self.nodes.append(Node(str(state+3), [[str(state), 'epsilon']], False))
        self.nodes.append(Node(str(state+4), [[str(state+3), self.arr[position+1]]], False))

        self.nodes.append(Node(str(state+5), [[str(state+2), 'epsilon'], [state+4, 'epsilon']], False))
        self.lastOrUnion = state+5
        self.lastState = self.lastOrUnion + 1
        self.nodes.append(Node(str(state+6), [[str(state+5), 'epsilon']], accepted))

    def concatOp(self, state, accepted, i):
        self.nodes.append(Node(str(state), [[str(self.lastState), i]], accepted))
        self.lastState = state

    def kleeneOp(self, first, orUnion = False):        
        beforeFirst = -1
        for i in self.nodes:
            if i.state == str(first) or i.state == first:    
                i.transitions.append([str(self.lastState), 'epsilon'])
                beforeFirst = i.transitions[0][0]

        if beforeFirst == -1:
            self.nodes[-1].transitions.append([str(first-1), 'epsilon'])
        else:
            self.nodes[-1].transitions.append([str(beforeFirst), 'epsilon'])

    def newKleene(self, position, accepted, inOr=False, posOp=False):
        op = '}'
        if posOp:
            op = ']'
        operacionP = []
        searching = True
        fOr = False
        start = self.state
        endPosition = 0
        self.nodes.append(Node(str(self.state), [[str(self.lastState), 'epsilon']], False))
        self.lastState = self.state
        self.state +=1
        
        #self.skip +=1
        while searching and position <= len(self.arr):
            
            if self.arr[position] == op:
                endPosition = position
                if position+1 == len(self.arr):
                    if inOr == False:
                        accepted = True
                    else:
                        self.orAccepted = True
                elif self.arr[position+1] == '|':
                    if position+3 == len(self.arr):
                        accepted = True
                    fOr = True
                    self.skip +=1
                searching = False

            else:
                operacionP.append(self.arr[position])
            position += 1
        if searching == True:
            print('No se encontro el final del  bracket')
            return
        if fOr:
            self.nodes.append(Node(str(self.state), [[str(self.state-1), 'epsilon']], False))
            self.nodes.append(Node(str(self.state+1), [[str(self.state), 'epsilon']], False))
            self.lastState = self.state+1
            orNodeOrigin = self.state
            self.lastOrOrigin = self.state
            self.state += 2

            tempAFN = AFN(operacionP, self.alphabet)
            tempAFN.changeState(self.state)
            tempAFN.changeLastState(self.state-1)
            pNodes = tempAFN.generateAFN()
            pNodes[-1].accepted = False
            self.state = tempAFN.state
            self.skip += len(operacionP)+1

            for j in pNodes:
                self.nodes.append(j)

            orNode1 = self.state - 1
            self.nodes.append(Node(str(self.state), [[str(orNodeOrigin), 'epsilon']], False))
            self.lastState = self.state
            self.state += 1
            if self.arr[endPosition+2] == '(':
                self.parenthesisOp(self.state, endPosition+3, False, True)
                self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon']], False))
            elif self.arr[endPosition+2] == '{':
                self.newKleene(endPosition+3, False, True)
                self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon']], False))
            elif self.arr[endPosition+2] == '[':
                self.newKleene(endPosition+3, False, True, True)
                self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon']], False))
            else:
                if endPosition+3 == len(self.arr):
                    self.orAccepted = True
                self.nodes.append(Node(str(self.state), [[str(self.state-1), self.arr[endPosition+2]]], False))
                self.state += 1
                self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon'], [self.state-1, 'epsilon']], False))
            
            self.lastOrUnion = self.state
            self.nodes.append(Node(str(self.state+1), [[str(self.state), 'epsilon']], self.orAccepted))
            self.state += 2
            self.orAccepted = False
            self.lastState = self.state - 1

        else:
            tempAFN = AFN(operacionP, self.alphabet)
            tempAFN.changeState(self.state)
            tempAFN.changeLastState(self.state-1)
            pNodes = tempAFN.generateAFN()
            for i in tempAFN.nodes:
                if i.state == str(tempAFN.lastState) or i.state == tempAFN.lastState:    
                    i.accepted = False
            self.state = tempAFN.state
            self.lastOrUnion = tempAFN.lastOrUnion
            self.lastOrOrigin = tempAFN.lastOrOrigin
            self.skip += len(operacionP)+1
            self.lastState = tempAFN.lastState
                    
            for j in pNodes:
                self.nodes.append(j)

            self.nodes.append(Node(str(self.state), [[str(self.lastState), 'epsilon']], accepted))
            if posOp:
                self.positiveOp(start)
            else:
                self.kleeneOp(start)
            self.lastState = self.state
            self.state += 1
    
    def positiveOp(self, first):
        for i in self.nodes:
            if i.state == str(first) or i.state == first:    
                i.transitions.append([str(self.lastState), 'epsilon'])
        
    def parenthesisOp(self, state, position, accepted, inOr=False):
        operacionP = []
        searching = True
        fOr = False
        endPosition = 0
        pCount = 0
        for i in self.arr[position:]:
            if i == '(':
                pCount +=1
            elif i == ')':
                break
        while searching and position <= len(self.arr):
            if self.arr[position] == ')':
                if pCount == 0:
                    endPosition = position
                    if position+1 == len(self.arr):
                        if inOr == False:
                            accepted = True
                        else:
                            self.orAccepted = True
                    elif self.arr[position+1] == '|':
                        if position+3 == len(self.arr):
                            accepted = True
                        fOr = True
                        self.skip +=1
                    searching = False
                else:
                    operacionP.append(self.arr[position])
                pCount -= 1

            else:
                operacionP.append(self.arr[position])
            position += 1
        if searching == True:
            print('No se encontro el final del parentesis')
            return
        if fOr:
            self.nodes.append(Node(str(self.state), [[str(self.state-1), 'epsilon']], False))
            self.nodes.append(Node(str(self.state+1), [[str(self.state), 'epsilon']], False))
            self.lastState = self.state+1
            orNodeOrigin = self.state
            self.lastOrOrigin = self.state
            self.state += 2

            tempAFN = AFN(operacionP, self.alphabet)
            tempAFN.changeState(self.state)
            tempAFN.changeLastState(self.state-1)
            pNodes = tempAFN.generateAFN()
            pNodes[-1].accepted = False
            self.state = tempAFN.state
            self.skip += len(operacionP)+1

            for j in pNodes:
                self.nodes.append(j)

            orNode1 = self.state - 1
            self.nodes.append(Node(str(self.state), [[str(orNodeOrigin), 'epsilon']], False))
            self.lastState = self.state
            self.state += 1
            if self.arr[endPosition+2] != '(':
                if endPosition+3 == len(self.arr):
                    self.orAccepted = True
                self.nodes.append(Node(str(self.state), [[str(self.state-1), self.arr[endPosition+2]]], False))
                self.state += 1

                self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon'], [self.state-1, 'epsilon']], False))
            else:
                self.parenthesisOp(self.state, endPosition+3, False, True)
                self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon']], False))
            #self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon'], [self.state-1, 'epsilon']], False))
            #self.nodes.append(Node(str(self.state), [[str(orNode1), 'epsilon']], False))
            self.lastOrUnion = self.state
            self.nodes.append(Node(str(self.state+1), [[str(self.state), 'epsilon']], self.orAccepted))
            self.state += 2
            self.orAccepted = False
            self.lastState = self.state - 1

        else:
            tempAFN = AFN(operacionP, self.alphabet)
            tempAFN.changeState(self.state)
            tempAFN.changeLastState(self.state-1)
            pNodes = tempAFN.generateAFN()
            pNodes[-1].accepted = False
            self.state = tempAFN.state
            self.lastOrUnion = tempAFN.lastOrUnion
            self.lastOrOrigin = tempAFN.lastOrOrigin
            self.skip += len(operacionP)+1    
            self.lastState = tempAFN.lastState
                    
            for j in pNodes:
                self.nodes.append(j)

            self.nodes.append(Node(str(self.state), [[str(self.lastState), 'epsilon']], accepted or self.orAccepted))
            self.lastState = self.state
            self.state += 1

    def generateAFN(self):
        # Crear nodos
        position = 1
        accepted = False
        self.nodes.append(Node(0, [], False))
        self.skip = 0
        for i in self.arr:
            
            if self.skip > 0:
                self.skip -= 1
                position += 1
                continue
            if i in self.alphabet:
                # Es el ultimo char?
                if position == len(self.arr):
                    accepted = True
                    if self.arr[position-2] != '|':
                        self.concatOp(self.state, accepted, i)
                        self.state += 1
                else:
                    # Siguiente posicion
                    next = self.arr[position]
                    if next == '|' and self.arr[position+1] in self.alphabet:
                        # Seguido por Or
                        if position+2 == len(self.arr):
                            accepted = True
                        self.orOp(self.state, position, accepted)
                        self.state += 7
                        self.lastState = self.state - 1
                        self.skip += 2
                    # Concatenacion 
                    elif self.arr[position-2] != '|': 
                        self.concatOp(self.state, accepted, i)
                        self.state += 1
            # Parentesis
            elif i == '(' and self.arr[position] in self.alphabet:
                self.parenthesisOp(self.state, position, accepted)
            elif i == '|': 
                self.nodes.append(Node(str(self.state), [[self.lastOrOrigin , 'epsilon']], False))
                self.state += 1
                if (self.arr[position] in self.alphabet):
                    self.nodes.append(Node(str(self.state), [[str(self.state-1), self.arr[position]]], False))
                    if position+2 == len(self.arr):
                        accepted = True
                    for j in self.nodes:
                        if str(j.state) == str(self.lastOrUnion):
                            j.transitions.append([self.state , 'epsilon'])
                        if accepted and str(j.state) == str(self.lastOrUnion+1):
                            j.accepted = True
                    self.skip += 1
                    self.state += 1
                    self.lastState = self.lastOrUnion + 1

                elif self.arr[position] == '(':
                    currentLastUnion = self.lastOrUnion
                    self.parenthesisOp(self.state, position+1, False, True)
                    node1a = False
                    node2a = False
                    for j in self.nodes:
                        for j in self.nodes:
                            if str(j.state) == str(currentLastUnion+1):
                                node2a = j.accepted
                            if str(j.state) == str(self.lastState):
                                node2a = j.accepted
                            if self.orAccepted and str(j.state) == str(currentLastUnion+1):
                                j.accepted = True
                                self.orAccepted = False
                    
                    self.nodes.append(Node(str(self.state), [[self.lastState, 'epsilon'], [currentLastUnion+1, 'epsilon']], node1a or node2a))
                    self.lastState = self.state
                    self.state +=1

                    #self.lastState = currentLastUnion + 1

            #Kleene
            elif i == '{':
                self.newKleene(position, accepted)
            #Positiva
            elif i == '[':
                self.newKleene(position, accepted, False, True)
            elif i not in self.operaciones:
                print('Hay un error en la expresion (' + i + ')')
                break
            position += 1
        #Regresar nodos generados
        return self.nodes