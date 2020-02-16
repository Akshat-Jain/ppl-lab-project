import json
with open('input.json', 'r') as myfile:
    x=myfile.read()

data = json.loads(x)
outputFileName = data['absolutePath']
outputfile = open(outputFileName, 'w')

tab=0

def printTabs(k):
	for i in range(0,k):
		print('\t', file=outputfile, end="")

def decodeAssignmentExpression(node):
	global tab
	printTabs(tab)
	expression = node['expression']
	print(expression['leftHandSide']['name'] + ' = ' + expression['rightHandSide']['value'] + ';', file=outputfile)

def decodeExpressionStatement(node):
	if(node['expression']['nodeType']=='Assignment'):
		decodeAssignmentExpression(node)

def decodeReturnStatement(node):
	global tab
	printTabs(tab)
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

def decodeConstructor(node):
	global tab
	print('constructor() ' + node['visibility'] + '{', file=outputfile)
	tab += 1
	statements = node['body']['statements']
	# print(statements, file=outputfile)
	for statement in statements:
		if(statement['nodeType']=='ExpressionStatement'):
			decodeExpressionStatement(statement)
	tab -= 1
	printTabs(tab)
	print('}', file=outputfile)

def decodeFunction(node):
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
			decodeExpressionStatement(statement)
		elif(statement['nodeType']=='Return'):
			decodeReturnStatement(statement)

	tab -= 1
	printTabs(tab)
	print('}', file=outputfile)
	pass

def decodeVariableDeclaration(node):
	global tab
	printTabs(tab)
	print(node['typeName']['name'] + ' ' + node['name'], file=outputfile, end="")
	value = node['value']
	if(value is not None):
		print(' = ' + str(value), file=outputfile, end="")
	print(';', file=outputfile)

def decodeFunctionDefinition(node):
	global tab
	printTabs(tab)
	if(node['kind']=='constructor'):
		decodeConstructor(node)
	elif(node['kind']=='function'):
		decodeFunction(node)

def decodePragmaDirective(node):
	print('pragma ' + str(node['literals'][0]) + ' ' + str(node['literals'][1]) + str(node['literals'][2]) + ';', file=outputfile)

def decodeContractDefinition(node):
	print('contract ' + str(node['name']) + '{', file=outputfile)
	global tab
	tab += 1
	for i in node['nodes']:
		nodeType = i['nodeType']
		if(nodeType=='VariableDeclaration'):
			decodeVariableDeclaration(i)
		elif(nodeType=='FunctionDefinition'):
			decodeFunctionDefinition(i)
	tab -= 1
	print('}', file=outputfile)

for i in data['nodes']:
	nodeType = i['nodeType']
	if(nodeType=='PragmaDirective'):
		decodePragmaDirective(i)
	elif(nodeType=='ContractDefinition'):
		decodeContractDefinition(i)