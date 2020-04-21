import json

# Load data from input.json file
with open('input.json', 'r') as myfile:
    x=myfile.read()

# Read output file name from the input file, or use a default output file name if not provided
data = json.loads(x)
if('absolutePath' in data):
	outputFileName = data['absolutePath']
else:
	outputFileName = 'defaultOutput.sol'
outputfile = open(outputFileName, 'w')

# A counter to maintain the current indentation level
tab=0

# A function to print tabs based on the current indentation level
def printTabs(k):
	for i in range(0,k):
		print('\t', file=outputfile, end="")

# A class to handle all the conditional statements
class ConditionalStatements():
	def __init__(self, node):
		self.node = node

	# Function to decode conditional statements
	def decode(self):
		global tab
		printTabs(tab)
		self.getCondition(self.node)
		self.getBody(self.node)

	# Helper function to extract the condition from the node
	def getCondition(self, node):
		global tab
		if(node['condition']['nodeType']=='BinaryOperation'):
			x = node['condition']['leftExpression']
			if(x['nodeType']=='IndexAccess'):
				baseExpression = x['baseExpression']['name']
				indexExpression = x['indexExpression']
				if(indexExpression['kind']=='typeConversion'):
					variable = indexExpression['arguments'][0]['name']
					datatype = indexExpression['expression']['typeName']['name']
					operator = node['condition']['operator']
					rhs = node['condition']['rightExpression']['name']
					condition = f'{baseExpression}[{datatype}({variable})] == {rhs}'
					ifCondition = f'if({condition}){{'
					print(ifCondition,file=outputfile)
					tab+=1
			elif(x['nodeType']=='Identifier'):
				variable = node['condition']['leftExpression']['name']
				operator = node['condition']['operator']
				if(node['condition']['rightExpression']['nodeType']=='Identifier'):
					value = node['condition']['rightExpression']['name']
				elif(node['condition']['rightExpression']['nodeType']=='Literal'):
					value = node['condition']['rightExpression']['value']
				condition = f'{variable} {operator} {value}'
				ifCondition = f'if({condition}){{'
				print(ifCondition,file=outputfile)
				tab+=1

	# Helper function to extract the body from the node
	def getBody(self, node):
		if('trueBody' in node):
			x = node['trueBody']
			trueBody = self.decodeTrueBody(node)
			printTabs(tab)
			print("}", file=outputfile)
			if('falseBody' in node and node['falseBody'] is not None):
				falseBody = self.decodeFalseBody(node)
		else:
			pass

	# Helper function to extract the true body from the node
	def decodeTrueBody(self, node):
		global tab
		trueBody = node['trueBody']
		if(trueBody['nodeType']=='Return'):
			if(trueBody['expression']['kind']=='typeConversion'):
				variable = trueBody['expression']['arguments'][0]['name']
				datatype = trueBody['expression']['expression']['typeName']['name']
				returnStatement = f'return {datatype}({variable});'
				printTabs(tab)
				print(returnStatement, file=outputfile)
				tab -= 1
		elif(trueBody['nodeType']=='Block'):
			for statement in trueBody['statements']:
				if(statement['nodeType']=='WhileStatement'):
					x = LoopingStatement(statement)
					x.decode()
				elif(statement['nodeType']=='DoWhileStatement'):
					x = LoopingStatement(statement)
					x.decode()
				else:
					expression = statement['expression']
					lhs = expression['leftHandSide']['name']
					operator = expression['operator']
					if(expression['rightHandSide']['nodeType']=='UnaryOperation'):
						typeDescription = str(expression['rightHandSide']['typeDescriptions']['typeString']).split()
						value = typeDescription[1]
					x = f'{lhs} {operator} {value};'
					printTabs(tab)
					print(x,file=outputfile)
			tab -= 1
		elif(trueBody['nodeType']=='ExpressionStatement'):
			if(trueBody['expression']['nodeType']=='Assignment'):
				lhs = trueBody['expression']['leftHandSide']['name']
				operator = trueBody['expression']['operator']
				if(trueBody['expression']['rightHandSide']['nodeType']=='UnaryOperation'):
					typeDescription = str(trueBody['expression']['rightHandSide']['typeDescriptions']['typeString']).split()
					value = typeDescription[1]
				x = f'{lhs} {operator} {value};'
				printTabs(tab)
				print(x,file=outputfile)
			tab -= 1

	# Helper function to extract the false body from the node
	def decodeFalseBody(self, node):
		global tab
		if(node['falseBody']['nodeType']=='IfStatement'):
			printTabs(tab)
			print("else ", file=outputfile, end="")
			falseBody = node['falseBody']
			if('condition' in falseBody):
				condition = self.getCondition(falseBody)
				x = self.getBody(falseBody)
			else:
				condition=""
		elif(node['falseBody']['nodeType']=='Block'):
			printTabs(tab)
			print("else{",file=outputfile)
			tab += 1
			y = node['falseBody']['statements'][0]
			if(y['expression']['nodeType']=='Assignment'):
				lhs = y['expression']['leftHandSide']['name']
				operator = y['expression']['operator']
				if(y['expression']['rightHandSide']['nodeType']=='Literal'):
					typeDescription = str(y['expression']['rightHandSide']['typeDescriptions']['typeString']).split()
					value = typeDescription[1]
				x = f'{lhs} {operator} {value};'
				printTabs(tab)
				print(x,file=outputfile)
			tab -= 1
			printTabs(tab)
			print("}",file=outputfile)
			pass

# A class to handle all the looping statements
class LoopingStatement():
	def __init__(self, node):
		self.node = node

	# Function to decode looping statements
	def decode(self):
		if(self.node['nodeType']=='ForStatement'):
			self.decodeForStatement(self.node);
		elif(self.node['nodeType']=='WhileStatement'):
			self.decodeWhileStatement(self.node);
		elif(self.node['nodeType']=='DoWhileStatement'):
			self.decodeDoWhileStatement(self.node);

	# Function to decode for loop statements
	def decodeForStatement(self, node):
		printTabs(tab)
		variableDeclarationStatement = self.getVariableDeclarationStatement(node)
		condition = self.getCondition(node)
		loopExpression = self.getExpressionStatement(node)
		forStatement = f'for ({variableDeclarationStatement}; {condition}; {loopExpression})'
		print(forStatement, file=outputfile)
		if(node['body']['nodeType']=='IfStatement'):
			x = ConditionalStatements(node['body'])
			x.decode()

	# Helper function to extract variable declaration statement from the node
	def getVariableDeclarationStatement(self, node):
		x = node['initializationExpression']
		variable = x['declarations'][0]['name']
		datatype = x['declarations'][0]['typeName']['name']
		initialValue = node['initializationExpression']['initialValue']['value']
		variableDeclarationStatement = f'{datatype} {variable} = {initialValue}'
		return variableDeclarationStatement

	# Helper function to extract the condition from the node
	def getCondition(self, node):
		lhs = node['condition']['leftExpression']['name']
		operator = node['condition']['operator']
		rhs=""
		if(node['condition']['rightExpression']['nodeType']=='Literal'):
			rhs = node['condition']['rightExpression']['value']
		else:
			rhs = node['condition']['rightExpression']['name']
		condition = f'{lhs} {operator} {rhs}'
		return condition

	# Helper function to extract the expression statement from the node
	def getExpressionStatement(self, node):
		if(node['loopExpression']['expression']['nodeType']=='UnaryOperation'):
			operator = node['loopExpression']['expression']['operator']
			name = node['loopExpression']['expression']['subExpression']['name']
			expression = f'{name}{operator}'
			return expression

	# Function to decode while statements
	def decodeWhileStatement(self, node):
		global tab
		condition = self.getCondition(node)
		printTabs(tab)
		conditionLine = f'while({condition}){{'
		print(conditionLine,file=outputfile)
		tab += 1
		for statement in node['body']['statements']:
			variable=""
			operator=""
			expression=""
			if(statement['nodeType']=='ExpressionStatement'):
				variable = statement['expression']['leftHandSide']['name']
				operator = statement['expression']['operator']
				if(statement['expression']['rightHandSide']['nodeType']=='BinaryOperation'):
					x = statement['expression']['rightHandSide']
					lhs = x['leftExpression']['name']
					operator2 = x['operator']
					if(x['rightExpression']['nodeType']=='UnaryOperation'):
						rhs = x['rightExpression']['subExpression']['name'] + x['rightExpression']['operator']
						expression = f'{lhs} {operator2} {rhs}'
			y = f'{variable} {operator} {expression};'
			printTabs(tab)
			print(y, file=outputfile)
		tab -= 1
		printTabs(tab)
		print("}",file=outputfile)

	# Function to decode do while statements
	def decodeDoWhileStatement(self, node):
		global tab
		condition = self.getCondition(node)
		printTabs(tab)
		doLine = f'do{{'
		print(doLine,file=outputfile)
		tab += 1
		for statement in node['body']['statements']:
			variable=""
			operator=""
			expression=""
			if(statement['nodeType']=='ExpressionStatement'):
				variable = statement['expression']['leftHandSide']['name']
				operator = statement['expression']['operator']
				if(statement['expression']['rightHandSide']['nodeType']=='BinaryOperation'):
					x = statement['expression']['rightHandSide']
					lhs = x['leftExpression']['name']
					operator2 = x['operator']
					if(x['rightExpression']['nodeType']=='UnaryOperation'):
						rhs = x['rightExpression']['subExpression']['name'] + x['rightExpression']['operator']
						expression = f'{lhs} {operator2} {rhs}'
					elif(x['rightExpression']['nodeType']=='Identifier'):
						rhs = x['rightExpression']['name']
						expression = f'{lhs} {operator2} {rhs}'
					elif(x['rightExpression']['nodeType']=='Literal'):
						rhs = x['rightExpression']['value']
						expression = f'{lhs} {operator2} {rhs}'
			y = f'{variable} {operator} {expression};'
			printTabs(tab)
			print(y, file=outputfile)
		tab -= 1
		printTabs(tab)
		whileLine = f'}}while({condition});'
		print(whileLine,file=outputfile)

# A class to handle all the functions
class FunctionDefinition():
	def __init__(self, node):
		self.node = node

	# Function to decode function statements
	def decode(self):
		node = self.node
		global tab
		printTabs(tab)
		if(node['kind']=='constructor'):
			self.decodeConstructor(node)
		elif(node['kind']=='function'):
			self.decodeFunction(node)

	# Function to decode constructor functions
	def decodeConstructor(self, node):
		global tab
		print('constructor() ' + node['visibility'] + '{', file=outputfile)
		tab += 1
		statements = node['body']['statements']
		for statement in statements:
			if(statement['nodeType']=='ExpressionStatement'):
				self.decodeExpressionStatement(statement)
		tab -= 1
		printTabs(tab)
		print('}', file=outputfile)

	# Function to decode function statements (other than constructor function)
	def decodeFunction(self, node):
		global tab
		functionDeclaration = self.getFunctionDeclaration(node)
		print(functionDeclaration + "{", file=outputfile)
		tab += 1

		self.parseFunctionBody(node)
		tab -= 1
		printTabs(tab)
		print('}\n', file=outputfile)

	# Function to decode function body
	def parseFunctionBody(self, node):
		for statement in node['body']['statements']:
			if(statement['nodeType'] in ['ForStatement','WhileStatement','DoWhileStatement']):
				x = LoopingStatement(statement)
				x.decode()
			elif(statement['nodeType']=='IfStatement'):
				x = ConditionalStatements(statement)
				x.decode()
			elif(statement['nodeType']=='VariableDeclarationStatement'):
				self.decodeVariableDeclarationStatement(statement)
			elif(statement['nodeType']=='ExpressionStatement'):
				self.decodeExpressionStatement(statement)
			elif(statement['nodeType']=='Return'):
				self.decodeReturnStatement(statement)

	# Helper function to extract variable declaration statement from the node
	def decodeVariableDeclarationStatement(self, node):
		variable = node['declarations'][0]['name']
		datatype = node['declarations'][0]['typeName']['name']
		if(node['initialValue']['nodeType']=='Identifier'):
			initialValue = node['initialValue']['name']
		elif(node['initialValue']['nodeType']=='Literal'):
			initialValue = node['initialValue']['value']

		printTabs(tab)
		variableDeclarationStatement = f'{datatype} {variable} = {initialValue};'
		print(variableDeclarationStatement,file=outputfile)

	# Helper function to extract function declaration from the node
	def getFunctionDeclaration(self, node):
		functionParameters = self.getFunctionParametersString(node)
		returnParameters = self.getReturnParametersString(node)
		name = self.getFunctionName(node)
		stateMutability = self.getStateMutability(node)
		visibility = self.getVisibility(node)
		functionDeclaration = f'function {name}({functionParameters}) {visibility} {stateMutability} returns({returnParameters})'
		return functionDeclaration

	# Helper function to extract function name from the node
	def getFunctionName(self, node):
		return node['name']

	# Helper function to extract state mutability from the node
	def getStateMutability(self, node):
		if('stateMutability' in node):
			return node['stateMutability']
		else:
			return "pure"

	# Helper function to extract visibility from the node
	def getVisibility(self, node):
		return node['visibility']

	# Helper function to extract function parameters from the node
	def getFunctionParametersString(self, node):
		s = ""
		variableDatatypes = []
		variableNames = []
		for i in node['parameters']['parameters']:
			if(i['typeName']['nodeType']=='ArrayTypeName'):
				variableDatatypes.append(i['typeName']['baseType']['name'] + '[] memory')
			else:
				variableDatatypes.append(i['typeName']['name'])
			variableNames.append(i['name'])
		
		for i in range(0,len(variableDatatypes)):
			s = s + variableDatatypes[i] + ' ' + variableNames[i] + ', '

		s = s[:-2]
		return s;

	# Helper function to extract return parameters from the node
	def getReturnParametersString(self, node):
		s = ""
		for i in node['returnParameters']['parameters']:
			s = s + i['typeName']['name'] + ', '

		s = s[:-2]
		return s

	# Helper function to extract expression statements from the node
	def decodeExpressionStatement(self, node):
		if(node['expression']['nodeType']=='Assignment'):
			self.decodeAssignmentExpression(node)

	# Helper function to extract return statement from the node
	def decodeReturnStatement(self, node):
		global tab
		printTabs(tab)
		returnStatementString = ""
		condition = ""
		if(node['expression']['nodeType']=='Identifier'):
			returnStatementString += 'return ' + str(node['expression']['name']) + ', '
			returnStatementString = returnStatementString[:-2] + ';'
		elif(node['expression']['nodeType']=='TupleExpression'):
			for component in node['expression']['components']:
				returnStatementString += str(component['name']) + ', '
			returnStatementString = returnStatementString[:-2]
			returnStatementString = 'return (' + returnStatementString + ')'
		elif(node['expression']['nodeType']=='UnaryOperation'):
			typeDescription = str(node['expression']['typeDescriptions']['typeString']).split()
			value = typeDescription[1]
			returnStatementString = f'return {value};'
		elif(node['expression']['nodeType']=='Conditional'):
			condition = self.getTernaryCondition(node['expression'])
			trueExpression = node['expression']['trueExpression']['name']
			typeDescription = str(node['expression']['falseExpression']['typeDescriptions']['typeString']).split()
			falseExpression = typeDescription[1]
			returnStatementString = f'return {condition}?{trueExpression}:{falseExpression};'
		print(returnStatementString, file=outputfile)

	# Helper function to extract ternary condition statements from the node
	def getTernaryCondition(self, node):
		global tab
		if(node['condition']['nodeType']=='BinaryOperation'):
			x = node['condition']['leftExpression']
			if(x['nodeType']=='IndexAccess'):
				baseExpression = x['baseExpression']['name']
				indexExpression = x['indexExpression']
				if(indexExpression['kind']=='typeConversion'):
					variable = indexExpression['arguments'][0]['name']
					datatype = indexExpression['expression']['typeName']['name']
					operator = node['condition']['operator']
					rhs = node['condition']['rightExpression']['name']
					condition = f'{baseExpression}[{datatype}({variable})] == {rhs}'
					ternaryCondition = f'if({condition}){{'
					return ternaryCondition
			elif(x['nodeType']=='Identifier'):
				variable = node['condition']['leftExpression']['name']
				operator = node['condition']['operator']
				if(node['condition']['rightExpression']['nodeType']=='Identifier'):
					value = node['condition']['rightExpression']['name']
				elif(node['condition']['rightExpression']['nodeType']=='Literal'):
					value = node['condition']['rightExpression']['value']
				elif(node['condition']['rightExpression']['nodeType']=='FunctionCall'):
					functionName = node['condition']['rightExpression']['expression']['name']
					value = node['condition']['rightExpression']['arguments'][0]['name']
				ternaryCondition = f'{variable}{operator}{functionName}({value})'
				return ternaryCondition

	# Helper function to extract assignment expressions from the node
	def decodeAssignmentExpression(self, node):
		global tab
		printTabs(tab)
		expression = node['expression']
		print(expression['leftHandSide']['name'] + ' = ' + expression['rightHandSide']['value'] + ';', file=outputfile)

# A class to handle the pragma directive
class PragmaDirective():
	def __init__(self, node):
		self.node = node

	# Function to decode the pragma directive
	def decode(self):
		print('pragma ' + str(self.node['literals'][0]) + ' ' + str(self.node['literals'][1]) + str(self.node['literals'][2]) + ';\n', file=outputfile)

# A class to handle all the contracts
class ContractDefinition():
	def __init__(self, node):
		self.node = node

	# Function to decode the contract
	def decode(self):
		print('contract ' + str(self.node['name']) + ' {\n', file=outputfile)
		global tab
		tab += 1
		for i in self.node['nodes']:
			nodeType = i['nodeType']
			if(nodeType=='VariableDeclaration'):
				self.decodeVariableDeclaration(i)
			elif(nodeType=='FunctionDefinition'):
				x = FunctionDefinition(i)
				x.decode()
		tab -= 1
		print('}', file=outputfile)

	# Helper function to extract the variable declaration statements from the node
	def decodeVariableDeclaration(self, node):
		global tab
		printTabs(tab)
		print(node['typeName']['name'] + ' ' + node['name'], file=outputfile, end="")
		value = node['value']
		if(value is not None):
			print(' = ' + str(value), file=outputfile, end="")
		print(';', file=outputfile)

# Main entry point of the program
for i in data['nodes']:
	nodeType = i['nodeType']
	if(nodeType=='PragmaDirective'):
		x = PragmaDirective(i)
		x.decode()
	elif(nodeType=='ContractDefinition'):
		x = ContractDefinition(i)
		x.decode()