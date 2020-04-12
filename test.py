import json
with open('input2.json', 'r') as myfile:
    x=myfile.read()

data = json.loads(x)
outputFileName = data['absolutePath']
outputfile = open(outputFileName, 'w')

tab=0

class PragmaDirective():
	def __init__(self, node):
		self.node = node

	def decode(self):
		print('pragma ' + str(self.node['literals'][0]) + ' ' + str(self.node['literals'][1]) + str(self.node['literals'][2]) + ';', file=outputfile)

class ContractDefinition():
	def __init__(self, node):
		self.node = node

	def decode(self):
		print('contract ' + str(self.node['name']) + '{', file=outputfile)
		global tab
		tab += 1
		for i in self.node['nodes']:
			nodeType = i['nodeType']
			if(nodeType=='VariableDeclaration'):
				self.decodeVariableDeclaration(i)
			elif(nodeType=='FunctionDefinition'):
				self.decodeFunctionDefinition(i)
		tab -= 1
		print('}', file=outputfile)

	def decodeVariableDeclaration(self, node):
		global tab
		self.printTabs(tab)
		print(node['typeName']['name'] + ' ' + node['name'], file=outputfile, end="")
		value = node['value']
		if(value is not None):
			print(' = ' + str(value), file=outputfile, end="")
		print(';', file=outputfile)

	def decodeFunctionDefinition(self, node):
		global tab
		self.printTabs(tab)
		if(node['kind']=='constructor'):
			self.decodeConstructor(node)
		elif(node['kind']=='function'):
			self.decodeFunction(node)

	def decodeConstructor(self, node):
		global tab
		print('constructor() ' + node['visibility'] + '{', file=outputfile)
		tab += 1
		statements = node['body']['statements']
		# print(statements, file=outputfile)
		for statement in statements:
			if(statement['nodeType']=='ExpressionStatement'):
				self.decodeExpressionStatement(statement)
		tab -= 1
		self.printTabs(tab)
		print('}', file=outputfile)

	def decodeFunction(self, node):
		# State mutability: pure, view, nonpayable, or payable

		global tab

		parameters = node['parameters']
		parametersString = ""

		returnParameters = node['returnParameters']
		returnParametersString = ""

		for parameter in parameters['parameters']:
			parametersString += str(parameter['typeName']['name']) + ', '

		for returnParameter in returnParameters['parameters']:
			returnParametersString += str(returnParameter['typeName']['name']) + ', '

		parametersString = parametersString[:-2]

		returnParametersString = returnParametersString[:-2]
		returnParametersString = ' returns(' + returnParametersString + ')'

		if(node['stateMutability']=='nonpayable'):
			print('function ' + node['name'] + '(' + parametersString + ') ' + node['visibility'] + returnParametersString + '{', file=outputfile)
		else:
			print('function ' + node['name'] + '(' + parametersString + ') ' + node['visibility'] + ' ' + node['stateMutability'] +  returnParametersString + '{', file=outputfile)

		tab += 1

		statements = node['body']['statements']
		for statement in statements:
			if(statement['nodeType']=='ExpressionStatement'):
				self.decodeExpressionStatement(statement)
			elif(statement['nodeType']=='Return'):
				self.decodeReturnStatement(statement)

		tab -= 1
		self.printTabs(tab)
		print('}', file=outputfile)
		pass

	def decodeAssignmentExpression(self, node):
		global tab
		self.printTabs(tab)
		expression = node['expression']
		print(expression['leftHandSide']['name'] + ' = ' + expression['rightHandSide']['value'] + ';', file=outputfile)

	def decodeExpressionStatement(self, node):
		if(node['expression']['nodeType']=='Assignment'):
			self.decodeAssignmentExpression(node)

	def decodeReturnStatement(self, node):
		global tab
		self.printTabs(tab)
		returnStatementString = ""
		if(node['expression']['nodeType']=='Identifier'):
			returnStatementString += 'return ' + str(node['expression']['name']) + ', '
			returnStatementString = returnStatementString[:-2]
		elif(node['expression']['nodeType']=='TupleExpression'):
			for component in node['expression']['components']:
				returnStatementString += str(component['name']) + ', '
			returnStatementString = returnStatementString[:-2]
			returnStatementString = 'return (' + returnStatementString + ')'
		print(returnStatementString + ';', file=outputfile)

	def printTabs(self, k):
		for i in range(0,k):
			print('\t', file=outputfile, end="")


for i in data['nodes']:
	nodeType = i['nodeType']
	if(nodeType=='PragmaDirective'):
		x = PragmaDirective(i)
		x.decode()
	elif(nodeType=='ContractDefinition'):
		x = ContractDefinition(i)
		x.decode()