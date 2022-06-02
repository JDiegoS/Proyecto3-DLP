class GeneradorSintactico(object):
    # Clase para construir el analizador sintactico

    def __init__(self, tokens, keywords, productions, anons, scannedTokens):
        self.tokens = tokens
        self.keywords = keywords
        self.operaciones = ['(', ')', '|', '{', '}', '[', ']']
        self.anons = anons
        self.productions = productions
        self.scannedTokens = scannedTokens
        self.currentToken = 0
        self.productionsIDs = []
        self.tokensIDs = []
        self.tabs = 0

        index = 0
        for i in self.productions:
            self.primero(index, i.value)
            index+=1
            self.productionsIDs.append(i.id)
        
        for i in self.tokens:
            self.tokensIDs.append(i.id)

        cambio = True
        while cambio == True:
            cambio = False
            for i in self.productions:
                for j in i.primeros:
                    if j in self.productionsIDs:
                        i.primeros.remove(j)
                        for k in self.productions:
                            if k.id == j:
                                i.primeros += k.primeros
                                cambio = True

        f = open("parser.py", "w")
        self.analizeProductions(f)


    def analizeExpression(self, file, expression):
        position = 0
        print('\nNUEVOOOOOOOO')
        inOr = ''
        while position < len(expression):
            print('\n ITEEEEEEE')
            print(expression[position:])
            
            # Verificar que se cierren los operadores
            if expression.count('(') != expression.count(')') or expression.count('<') != expression.count('>') or expression.count('[') != expression.count(']') or expression.count('{') != expression.count('}') or expression.count('(.') != expression.count('.)'):
                print('Error: No se cerro un operador en producciones')
                quit()

            if expression[position] == '(':
                # Semantica
                if expression[position+1] == '.':
                    closeSemantic = expression[position:].find('.)')
                    file.write('\n'+'\t'*self.tabs +expression[position+2:position+closeSemantic])
                    position += closeSemantic
                    continue
                else:
                    exp = self.getSubs(expression[position:], '(', ')')
                    subs = exp.split('|')
                    print('ESTAAAA (((')
                    print(exp)
                    print(subs)
                    print(expression[position:])
                    for s in subs:
                        self.analizeExpression(file, s)
                        #self.tabs -=1
                        position += len(s)
            elif expression[position] == '{':
                primeros = ''
                exp = self.getSubs(expression[position:], '{', '}')
                subs = exp.split('|')
                for i in subs:
                    primeros += "'" + self.primero(0, i, True) + "',"
                primeros = primeros[:-1]
                print('ESTAAAA {')
                print(exp)
                print(subs)
                print(primeros)
                file.write('\n'+'\t'*self.tabs +'while self.currentToken in ['+primeros+']:')
                self.tabs += 1
                position+=1
                continue
            elif expression[position] == '[':
                exp = self.getSubs(expression[position:], '[', ']')
                subs = exp.split('|')
                print('ESTAAAA [[')
                print(exp)
                print(subs)
                for s in subs:
                    self.analizeExpression(file, s)
                    position += len(s)

            elif expression[position] == '|':
                inOr = 'el'
                self.tabs -= 1
                position +=1
                continue
            else:
                found = False
                positioned = False
                for i in self.productions:
                    if expression[position:].find(i.id) == 0:
                        params = ''
                        code = '\n'+'\t'*self.tabs
                        print('PARAMS')
                        print(expression[position + len(i.id)])
                        if expression[position + len(i.id)] == '<':
                            print(expression[position + len(i.id):])
                            params = self.getSubs(expression[position + len(i.id):],'<', '>')
                            print(params)
                            
                            code += params+ ' = '
                            print(position)
                            positioned = True
                            position += expression[position:].find('<') + len(params)+1
                            print(position)
                            print(expression[position])
                            
                        code += 'self.' + i.id + '(' + params + ')'
                        file.write(code)
                        if positioned == False:
                            position += len(i.id)-1
                        found = True
                        break
                if found == False:
                    if expression[position] == '"':
                        anonCLose = expression[position+1:].find('"')
                        anonym = expression[position+1:position+1+anonCLose]
                        print('ANOOOOOOOON')
                        print(expression[position+1:])
                        print(anonCLose)
                        print(anonym)
                        for i in self.anons:
                            if i.id == anonym:
                                code = '\n'+'\t'*self.tabs + inOr +"if self.currentToken == '" + anonym + "':"
                                file.write(code)
                                self.tabs+=1
                                position += len(anonym) + 2
            if inOr != '':
                inOr = ''
            position+=1


    
    def analizeProductions(self, file):
        for i in self.productions:
            self.tabs = 0
            parameters = ''
            if len(i.params) > 0:
                parameters += ', ' + i.params
            file.write('\n\ndef '+ i.id + '(self'+ parameters +'):')
            self.tabs += 1
            self.analizeExpression(file, i.value)

            
    def primero(self, index, production, search = False):
        semCount = production.count('(.')
        while semCount > 0:
            semStart = production.find('(.')
            semEnd = production.find('.)')
            semantic = production[semStart:semEnd+2]
            production = production.replace(semantic, '')
            semCount -= 1
        
        production = production.replace('(', ' (')
        production = production.replace('{', ' {')
        production = production.replace('[', ' [')
        production = production.replace('" ', '"')
        
        subs = production.split(' ')
        subs = [x for x in subs if x]
        prodFirst = False
        if subs[0][0] != '{' and subs[0][0] != '[':
            prodFirst = True
        subProd = []
        sub = ''
        for i in subs:
            if i[0] == '(':
                sub = self.getSubs(i, '(', ')')
            elif i[0] == '{':
                sub = self.getSubs(i, '{', '}')
            elif i[0] == '[':
                sub = self.getSubs(i, '[', ']')
            else:
                sub = i
            subProd += sub.split('|')

        for sub in subProd:
            
            found = False
            for i in self.tokens:
                if sub.find(i.id) == 0:
                    if search == False:
                        self.productions[index].primeros.append(i.id)
                    else:
                        return i.id
                    found = True
                    break
            if found == True:
                if prodFirst:
                    break
                continue
            if sub[0] == '"':
                for i in self.anons:
                    if sub[1:].find(i.id) == 0:
                        if search == False:
                            self.productions[index].primeros.append(i.id)
                        else:
                            return i.id
                        found = True
                        break
            if found == True:
                if prodFirst:
                    break
                continue
            for i in self.productions:
                if sub.find(i.id) == 0:
                    if search == False:
                        self.productions[index].primeros.append(i.id)
                    else:
                        return i.id
                    found = True
                    break
            if found == True:
                if prodFirst:
                    break
                continue
            

            

    def getSubs(self, exp, op, closeOp):
        expression = ''
        pCount = 1
        lastFound = 1
        done = False
        while done == False:
            closeP = exp.find(closeOp, lastFound)
            parens = exp[:closeP].count(op)
            print('SUBSSSSSSSSSSSSSS')
            print(parens)
            print(pCount)
            if parens > pCount:
                pCount = parens
                lastFound = exp.find(closeOp, closeP+1)
            else:
                expression = exp[1:closeP]
                print(exp.count(')'))
                print(expression)
                done = True
        return expression

