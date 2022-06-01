from Characters import Characters
from Keywords import Keywords
from Token import Token

class Lector(object):
    def __init__(self, filename):
        # Abrir y leer archivo COCO
        archivoCoco = open(filename)
        self.lines = archivoCoco.readlines()
        
        self.reservedCoco = ['COMPILER', 'CHARACTERS', 'KEYWORDS', 'TOKENS', 'END', 'EXCEPT', 'PRODUCTIONS']
        self.leftReserved = 'COMPILER CHARACTERS KEYWORDS TOKENS PRODUCTIONS END'
        self.compiler = ''
        self.characters = []
        self.keywords = []
        self.tokens = []
        self.productions = []
        self.currentType = ''
        self.reservedCount = 0
        self.finishedLine = True

        for i in self.lines:
            self.processLine(i.replace('\n', ''))
        if self.reservedCount < 6:
            print('\nError al analizar palabras reservadas. No se encontro ' + self.leftReserved + '\n')
            quit()
            
    def processLine(self, line):
        letters = line.replace(' ', '')
        # Linea vacia
        if line == '':
            return
        
        # Es palabra reservada de COCO
        if line[0:9] == 'COMPILER ':
            self.compiler = line.split(' ')[1]
            self.leftReserved = self.leftReserved.replace('COMPILER ', '')
            self.reservedCount +=1
            return
        elif line[0:4] == 'END ':
            self.reservedCount +=1
            self.leftReserved = self.leftReserved.replace('END', '')
            return
        elif line[0:10] == 'CHARACTERS':
            self.reservedCount +=1
            self.leftReserved = self.leftReserved.replace('CHARACTERS ', '')
            self.currentType = 'CHARACTERS'
        elif line[0:9] == 'KEYWORDS':
            self.reservedCount +=1
            self.leftReserved = self.leftReserved.replace('KEYWORDS ', '')
            self.currentType = 'KEYWORDS'
        elif line[0:8] == 'TOKENS':
            self.reservedCount +=1
            self.currentType = 'TOKENS'
            self.leftReserved = self.leftReserved.replace('TOKENS ', '')
        elif line[0:12] == 'PRODUCTIONS':
            self.reservedCount +=1
            self.leftReserved = self.leftReserved.replace('PRODUCTIONS ', '')
            self.currentType = 'PRODUCTIONS'
            return
        else:
            # Verificar que termine con .
            if letters[-1] != '.' and letters[-1] != '=' and letters[-1] != '+':
                print('\nError al final de linea. Debe terminar en =, + o .\n')
                quit()
            # Separar linea
            if self.finishedLine == False:
                letters = 'a=' + letters
            words = letters.split('=')
            
            # Analizar characters
            if self.currentType == 'CHARACTERS':
                id = words[0]
                value = []
                text = words[1].split('+')
                if letters[-1] == '.':
                    text[-1] = text[-1][:-1]
                text = [x for x in text if x]

                
                if letters[-1] == '.' or letters[-1] == '+':
                    pos = 0
                    while pos < len(text):
                        if text[pos][0] == '"':
                            # String de caracteres
                            alph = list(text[pos].replace('"',''))
                            for i in alph:
                                value.append(i)
                        elif text[pos][0:4] == 'CHR(':
                            # ASCII
                            number = text[pos][4:][:-1]
                            value.append(chr(int(number)))
                        else:
                            # Caracter ya definido
                            found =False
                            for i in self.characters:
                                if i.id == text[pos]:
                                    for j in i.alphabet:
                                        value.append(j)
                                        found = True
                                    break
                            if found == False:
                                print('\nError: el caracter %s no esta definido\n' % text[pos])
                                quit()
                        pos += 1
                if self.finishedLine:
                    self.characters.append(Characters(id, value))
                else:
                    for i in value:
                        self.characters[-1].alphabet.append(i)
                    self.finishedLine = True

            # Analizar Keywords
            elif self.currentType == 'KEYWORDS':
                id = words[0]
                value = []
                if letters[-1] == '.':
                    value = words[1][:-1].replace('"','')
 
                if self.finishedLine:
                    self.keywords.append(Keywords(id, value))
                else:
                    self.keywords[-1].value = value
                    self.finishedLine = True

            # Analizar tokens
            elif self.currentType == 'TOKENS':
                id = words[0]
                value = []
                value = words[1]
                pos = 2
                hasExcept = False
                while pos < len(words):
                    if words[pos] == 'EXCEPT':
                        hasExcept = True
                        break
                    value += ' ' + words[pos]
                    pos+=1
                if hasExcept == False and letters[-1] == '.':
                    value = value[:-1]

                if value.find('EXCEPT') != -1:
                    value = value[0:value.find('EXCEPT')]
                if self.finishedLine:
                    self.tokens.append(Token(id, value))
                else:
                    self.tokens[-1].value += value
                    self.finishedLine = True
            
            if letters[-1] == '=' or letters[-1] == '+':
                self.finishedLine = False
    
    def getTokens(self):
        return self.tokens
        
    def getCharacters(self):
        return self.characters

    def getKeywords(self):
        return self.keywords
                
                        


                    

