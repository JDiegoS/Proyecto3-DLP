
class GeneradorSintactico(object):
    # Clase para construir el analizador sintactico

    def __init__(self, tokens, keywords, productions, anons, scannedTokens):
        self.tokens = tokens
        self.keywords = keywords
        self.anons = anons
        self.productions = productions
        self.scannedTokens = scannedTokens
        self.productionsIDs = []
        self.tokensIDs = []
        self.tabs = 0
        self.firstIfLoop = False

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


    def analizeExpression(self, file, expression, orOps, firstIf=False, inLoop=False):
        position = 0
        inOr = ''
        while position < len(expression):
            
            # Verificar que se cierren los operadores
            if expression.count('(') != expression.count(')') or expression.count('<') != expression.count('>') or expression.count('[') != expression.count(']') or expression.count('{') != expression.count('}') or expression.count('(.') != expression.count('.)'):
                print('Error: No se cerro un operador en producciones')
                quit()

            if expression[position] == '(':
                
                # Semantica
                if expression[position+1] == '.':
                    
                    closeSemantic = expression[position:].find('.)')
                    
                    if closeSemantic + position == len(expression)-2 and inLoop == False:
                        self.tabs = 2
                        if firstIf or self.firstIfLoop:
                            file.write('\n'+'\t\telse:\n\t'+'\t\tprint("Error sintactico")\n\t'+'\t\tquit()')
                            firstIf = False
                            self.firstIfLoop = False
                        semantics = expression[position+2:position+closeSemantic].split(chr(92) + chr(110))
                        for sem in semantics:
                            file.write('\n'+'\t'*self.tabs +sem)
                        position += closeSemantic + 2
                        continue
                    else:
                        semantics = expression[position+2:position+closeSemantic].split(chr(92) + chr(110))
                        for sem in semantics:
                            file.write('\n'+'\t'*self.tabs +sem)
                        position += closeSemantic + 2

                        continue
                else:
                    orOps = 0
                    exp = self.getSubs(expression[position:], '(', ')')
                    self.analizeExpression(file, exp, orOps,firstIf, True)
                    position += len(exp)
                    subs = exp.split('|')
                    
            elif expression[position] == '{':
                orOps = 0
                primeros = ''
                exp = self.getSubs(expression[position:], '{', '}')
                subs = exp.split('|')
                hasProd = False
                for i in subs:
                    prim = self.primero(0, i, True) 
                    for j in self.productions:
                        if prim.find(j.id) != -1:
                            firsts = ''
                            for k in j.primeros:
                                firsts += "'" + k + "',"
                            firsts = firsts[:-1]
                            prim = prim.replace(j.id, firsts)
                            hasProd = True
                            break
                    if hasProd:
                        primeros += prim
                    else:
                        primeros += "'" + prim + "',"
                        
                if hasProd == False:
                    primeros = primeros[:-1]
                file.write('\n'+'\t'*self.tabs +'while self.currentToken in ['+primeros+']:')
                self.tabs += 1
                position+=1
                continue
            elif expression[position] == '[':
                orOps = 0
                exp = self.getSubs(expression[position:], '[', ']')
                self.analizeExpression(file, exp, orOps,firstIf, True)
                position += len(exp)
                subs = exp.split('|')


            elif expression[position] == '|':
                inOr = 'el'
                self.tabs -= orOps
                orOps = 0
                position +=1
                continue
            elif expression[position] in [')', '}', ']']:
                self.tabs -= 1
                if expression[position] != ']':
                    file.write('\n'+'\t'*self.tabs +'else:\n\t'+'\t'*self.tabs+'print("Error sintactico")\n\t'+'\t'*self.tabs+'quit()')
                self.orOps = 0
                position +=1
                continue
            else:
                found = False
                positioned = False
                for i in self.productions:
                    if expression[position:].find(i.id) == 0:
                        primeros = ''
                        for j in i.primeros:
                            primeros += "'" + j + "',"
                        primeros = primeros[:-1]

                        file.write('\n'+'\t'*self.tabs +'if self.currentToken in ['+primeros+']:')
                        if self.tabs == 2:
                            firstIf = True
                            if inLoop:
                                self.firstIfLoop = True
                        self.tabs += 1
                        orOps+=1
                        params = ''
                        code = '\n'+'\t'*self.tabs
                        if expression[position + len(i.id)] == '<':
                            params = self.getSubs(expression[position + len(i.id):],'<', '>')
                            code += params+ ' = '
                            positioned = True
                            position += expression[position:].find('<') + len(params)+1
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
                        for i in self.anons:
                            if i.id == anonym:
                                code = '\n'+'\t'*self.tabs + inOr +"if self.currentToken == '" + anonym + "':"
                                file.write(code)
                                if self.tabs == 2:
                                    firstIf = True
                                    if inLoop:
                                        self.firstIfLoop = True
                                self.tabs+=1
                                orOps+=1
                                file.write('\n'+'\t'*self.tabs + 'self.getNext()')
                                
                                position += len(anonym) + 1
                    
                    else:
                        for i in self.tokens:
                            if expression[position:].find(i.id) == 0:
                                file.write('\n'+'\t'*self.tabs + 'self.getNext()')
            if inOr != '':
                inOr = ''
            position+=1

    
    def analizeProductions(self, file):
        file.write('''
class Parser(object):

	def __init__(self, tokens, tokenValues):
		self.tokens = tokens
		self.tokenValues = tokenValues
		self.currentToken = tokens[0]
		self.lastToken = tokens[0]
		self.currentTokenValue = tokenValues[0]
		self.lastTokenValue = tokenValues[0]
		self.index = 0

		self.tokens.pop()
		self.tokenValues.pop()''')
        file.write('\n\t\tself.' + self.productions[0].id + '()')
        file.write('''

	def getNext(self):
		self.index += 1
		if (self.index < len(self.tokens)):
			self.lastToken = self.currentToken
			self.lastTokenValue = self.currentTokenValue
			self.currentToken = self.tokens[self.index]
			self.currentTokenValue = self.tokenValues[self.index]
		else:
			quit()
        
        ''')
        for i in self.productions:
            self.tabs = 1
            parameters = ''
            if len(i.params) > 0:
                parameters += ', ' + i.params
            file.write('\n\n\tdef '+ i.id + '(self'+ parameters +'):')
            self.tabs += 1
            self.analizeExpression(file, i.value, 0)
            file.write('\n\t\treturn '+ (parameters.replace(', ', '')))
        
        file.write('''

result = open('scannedTokens.txt')
line = result.readlines()
tokens = line[0].split(' ')
result.close()
vals = open('scannedValues.txt')
line = vals.readlines()
values = line[0].split(' ')
parser = Parser(tokens, values)
        
        ''')

            
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
            if parens > pCount:
                pCount = parens
                lastFound = exp.find(closeOp, closeP+1)
            else:
                expression = exp[1:closeP]
                done = True
        return expression

