import numpy as np

class Node:
	def __init__(self, name, parent):
		self.name = name
		self.parent = parent
		self.children = []
		if parent:
			parent.children.append(self)

	def print_node_dot(self, fout):
		if not self.parent == None:
			fout.write('\t"%s" -- "%s";\n' % (self.parent.name, self.name))

	def print_node_comp(self, fout):
		if not self.parent == None:
			fout.write('\t%s -> %s;\n' % (self.parent.name, self.name))

def __print_tree_comp(node,fout):
	if len(node.children) == 0:
		node.print_node_comp(fout)
	else:
		node.print_node_comp(fout)
		for child in node.children:
			__print_tree_comp(child,fout)

def __print_tree(node,fout):
	if len(node.children) == 0:
		node.print_node_dot(fout)
	else:
		node.print_node_dot(fout)
		for child in node.children:
			__print_tree(child,fout)

def __print_dot_tree(node, fout):
	fout.write('graph phylogeny {\n')
	__print_tree(node,fout)
	fout.write('}\n')

def __print_dot_comp(node, fout):
	fout.write('digraph phylogeny {\n')
	__print_tree_comp(node,fout)
	fout.write('}\n')

def __print_tikz_rec(node):
	if len(node.children) == 0:
		return '[{%s}]' % node.name
	else:
		str_children = []
		for child in node.children:
			str_children.append(__print_tikz_rec(child))
		return '[{%s} [%s]]' % (node.name, ''.join(str_children))

# def compress_tree(node):
# 	if node.name == 'germline':
# 		for c in node.children:
# 			compress_tree(c)
# 	elif len(node.children) == 0:
# 		return
# 	elif len(node.children) == 1:
# 		child = node.children[0]
# 		node.name += ',{0}'.format(child.name)
# 		node.children = child.children
# 		for c in child.children:
# 			c.parent = node
# 		compress_tree(node)
# 	else:
# 		for c in node.children:
# 			compress_tree(c)


def __print_tikz_tree(root, fout):
	fout.write('\\documentclass[tikz]{standalone}\n\\usepackage{forest}\\usepackage{fancyvrb}\n\\begin{document}\n\\begin{forest}\n')
	fout.write('for tree={\n\tgrow=0,\n\treversed, % tree direction\n\tparent anchor=east,\n\t%child anchor=west, % edge anchors\n')
	fout.write('\tanchor=west,\n\tedge path={\n\t\\noexpand\\path[\\forestoption{edge}](!u.parent anchor) -- +(5pt,0) |- (.child anchor)\\forestoption{edge label};},\n')
	fout.write('\tdelay={where content={}{shape=coordinate,for parent={for children={anchor=west}}}{}}\n}')
	fout.write(__print_tikz_rec(root))
	fout.write('\n\\end{forest}\n\\end{document}')

# True if col1 contains col2
def contains(col1, col2):
	for i in range(len(col1)):
		if not col1[i] >= col2[i]:
			return False
	return True

def write_tree(matrix, names, write_file):
	i = 0
	while i < matrix.shape[1]:
		j = i + 1
		while j < matrix.shape[1]:
			if np.array_equal(matrix[:,i], matrix[:,j]):
				matrix = np.delete(matrix, j, 1)
				x = names.pop(j)
				names[i] += ',' + x
				j -= 1
			j += 1
		i += 1

	rows = len(matrix)
	cols = len(matrix[0])

	dimensions = np.sum(matrix, axis=0)
	# ordered indeces
	indeces = np.argsort(dimensions)
	dimensions = np.sort(dimensions)

	mutations_name = []
	for i in range(cols):
		mutations_name.append(names[indeces[i]])

	# REMEMBER:
	# get the i-th columk with matrix[:,i]

	root = Node('germline', None)

	driver_mut = Node(mutations_name[-1], root)

	mut_nod = {}

	mut_nod[mutations_name[cols-1]] = driver_mut

	i = cols - 2
	while i >=0:
		if dimensions[i] == 0:
			break

		attached = False
		for j in range(i+1, cols):
			if contains(matrix[:, indeces[j]], matrix[:, indeces[i]]):
				node = Node(mutations_name[i], mut_nod[mutations_name[j]])
				mut_nod[mutations_name[i]] = node
				attached = True
				break

		if not attached:
			node = Node(mutations_name[i], root, indeces[i])
			mut_nod[mutations_name[i]] = node
		i -=1

	with open(write_file + '.gv', 'w+') as fout:
		__print_dot_tree(root, fout)


	with open(write_file + '.tex', 'w+') as fout:
		__print_tikz_tree(root, fout)

	return root, mut_nod

def write_tree_comp(matrix, names, write_file):

	i = 0
	while i < matrix.shape[1]:
		j = i + 1
		while j < matrix.shape[1]:
			if np.array_equal(matrix[:,i], matrix[:,j]):
				matrix = np.delete(matrix, j, 1)
				x = names.pop(j)
				names[i] += ',' + x
				j -= 1
			j += 1
		i += 1

	rows = len(matrix)
	cols = len(matrix[0])

	dimensions = np.sum(matrix, axis=0)
	# ordered indeces
	indeces = np.argsort(dimensions)
	dimensions = np.sort(dimensions)

	mutations_name = []
	for i in range(cols):
		mutations_name.append(names[indeces[i]])

	# REMEMBER:
	# get the i-th columk with matrix[:,i]

	root = Node('germline', None)

	driver_mut = Node(mutations_name[-1], root)

	mut_nod = {}

	mut_nod[mutations_name[cols-1]] = driver_mut

	cont = 2

	i = cols - 2

	while i >=0:
		if dimensions[i] == 0:
			break

		attached = False
		for j in range(i+1, cols):
			if contains(matrix[:, indeces[j]], matrix[:, indeces[i]]):
				node = Node(mutations_name[i], mut_nod[mutations_name[j]])
				mut_nod[mutations_name[i]] = node
				cont += 1
				attached = True
				break

		if not attached:
			node = Node(mutations_name[i], root, indeces[i])
			mut_nod[mutations_name[i]] = node
			cont += 1
		i -=1

	with open(write_file + '.gv', 'w+') as fout:
		__print_dot_comp(root, fout)

	return root, mut_nod
