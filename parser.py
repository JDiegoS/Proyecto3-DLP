
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
		self.tokenValues.pop()
		self.EstadoInicial()

	def getNext(self):
		self.index += 1
		if (self.index < len(self.tokens)):
			self.lastToken = self.currentToken
			self.lastTokenValue = self.currentTokenValue
			self.currentToken = self.tokens[self.index]
			self.currentTokenValue = self.tokenValues[self.index]
		else:
			quit()
        
        

	def EstadoInicial(self):
		while self.currentToken in ['numeroToken']:
			if self.currentToken in ['numeroToken']:
				self.Instruccion()
				if self.currentToken == ';':
					self.getNext()
				else:
					print("Error sintactico")
					quit()
		return 

	def Instruccion(self):
		resultado=0
		if self.currentToken in ['numeroToken']:
			resultado = self.Expresion(resultado)
		else:
			print("Error sintactico")
			quit()
		print("Resultado:"+str(resultado))
		return 

	def Expresion(self, resultado):
		resultado1=resultado2=0
		if self.currentToken in ['numeroToken']:
			resultado1 = self.Termino(resultado1)
			while self.currentToken in ['+']:
				if self.currentToken == '+':
					self.getNext()
					if self.currentToken in ['numeroToken']:
						resultado2 = self.Termino(resultado2)
						resultado1+=resultado2
						print("Término:"+str(resultado1))
					else:
						print("Error sintactico")
						quit()
		else:
			print("Error sintactico")
			quit()
		resultado=resultado1
		print("Término:"+str(resultado))
		return resultado

	def Termino(self, resultado):
		resultado1=resultado2=0
		if self.currentToken in ['numeroToken']:
			resultado1 = self.Factor(resultado1)
			while self.currentToken in ['*']:
				if self.currentToken == '*':
					self.getNext()
					if self.currentToken in ['numeroToken']:
						resultado2 = self.Factor(resultado2)
						resultado1*=resultado2
						print("Factor:"+str(resultado1))
					else:
						print("Error sintactico")
						quit()
		else:
			print("Error sintactico")
			quit()
		resultado=resultado1
		print("Factor:"+str(resultado))
		return resultado

	def Factor(self, resultado):
		resultado1=0
		if self.currentToken in ['numeroToken']:
			resultado1 = self.Numero(resultado1)
		else:
			print("Error sintactico")
			quit()
		resultado=resultado1
		print("Número:"+str(resultado))
		return resultado

	def Numero(self, resultado):
		self.getNext()
		resultado=int(self.lastTokenValue)
		print("Token:"+str(resultado))
		return resultado

result = open('scannedTokens.txt')
line = result.readlines()
tokens = line[0].split(' ')
result.close()
vals = open('scannedValues.txt')
line = vals.readlines()
values = line[0].split(' ')
parser = Parser(tokens, values)
        
        