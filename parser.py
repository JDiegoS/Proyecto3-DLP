

def EstadoInicial(self):
	while self.currentToken in ['Instruccion']:
		self.Instruccion()
		if self.currentToken == ';':

def Instruccion(self):
	resultado=0
	resultado = self.Expresion(resultado)
	print(resultado)

def Expresion(self, resultado):
	resultado1=resultado2=0
	resultado1 = self.Termino(resultado1)
	while self.currentToken in ['+','-']:
		if self.currentToken == '+':
			resultado1+=resultado2
		elif self.currentToken == '-':
			resultado1-=resultado2
			resultado=resultado1

def Termino(self, resultado):
	resultado1=resultado2=0
	resultado1 = self.Factor(resultado1)
	while self.currentToken in ['*','/']:
		if self.currentToken == '*':
			resultado1*=resultado2
		elif self.currentToken == '/':
			resultado1/=resultado2
			resultado=resultado1

def Factor(self, resultado):
	signo=1
	if self.currentToken == '-':
		resultado = self.Number(resultado)
		if self.currentToken == '(':
			resultado*=signo

def Number(self, resultado):
	resultado=ultimoToken.obtenerValor()