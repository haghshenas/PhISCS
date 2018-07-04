import os
import sys
from sets import Set
#import graphviz as gv
#from ancAdjMatricesFunctions import *
#from variousFunctions import *

DIFFERENT_LINEAGES  = 0
ANCESTOR_DESCENDANT = 1
DESCENDANT_ANCESTOR = 2
SAME_NODE	    = 3 




class Tree:
	def __init__(self, ancMatrix):
		self.treeSize = len(ancMatrix)
		self.ancMatrix = [[ancMatrix[row][column] for column in range(self.treeSize)] for row in range(self.treeSize)]
		self.nodeLabels = ["" for i in range(self.treeSize)]
		self.nodeFreqs = [-1 for i in range(self.treeSize)]
		self.edgeLabels = ["" for i in range(self.treeSize)]
		self.additionalINFO = ""
		self.mutationsAtNode  = [[] for i in range(self.treeSize)]
	
	def addMutationToNode(self, mutID, nodeID):
		assert nodeID >=0 and nodeID < self.treeSize, "In function addMutationToNode value of nodeID out of [0, treeSize) interval"
		assert (mutID in self.mutationsAtNode[nodeID]) == False, "In function addMutationToNode mutation with ID " + mutID + " already exists at node " + nodeID
		self.mutationsAtNode[nodeID].append(mutID)

	def getAllMutIDs(self):
		mutIDs = []
		for node in range(self.treeSize):
			for mutID in self.mutationsAtNode[node]:
				mutIDs.append(mutID)
		return mutIDs

	def getSize(self):
		return self.treeSize

	def getNodeOfMutation(self, mutID):
		for i in range(self.treeSize):
			if mutID in self.mutationsAtNode[i]:
				return i
		print("Error in function getNodeOfMutation in class Tree. There does not exist mutation " + mutID)
		sys.exit(2)

	def getMutationsAncestryRelation(self, mut1, mut2):
		node1 = -1
		node2 = -1
		for node in range(self.treeSize):
			if mut1 in self.mutationsAtNode[node]:
				assert node1 == -1, "Error in Tree class function getMutationsAncestryRelation. Mutation " + mut1 + " present at multiple nodes"
				node1 = node
			if mut2 in self.mutationsAtNode[node]:
				assert node2 == -1, "Error in Tree class function getMutationsAncestryRelation. Mutation " + mut2 + " present at multiple nodes"
				node2 = node
		
		assert node1 != -1, "Error in Tree class function getMutationsAncestryRelation. Mutation " + mut1 + " not found in the tree."
		assert node2 != -1, "Error in Tree class function getMutationsAncestryRelation. Mutation " + mut2 + " not found in the tree."
	
		if node1 == node2:
			return SAME_NODE
		elif self.ancMatrix[node1][node2] == 1:
			return ANCESTOR_DESCENDANT
		elif self.ancMatrix[node2][node1] == 1:
			return DESCENDANT_ANCESTOR
		elif self.ancMatrix[node1][node2] == 0 and self.ancMatrix[node2][node1] == 0:
			return DIFFERENT_LINEAGES
		else:
			print("ERROR in function getMutationsAncestryRelation. Nothing returned. Exiting.")
			sys.exit(2)
	

	def addStringToNodeLabel(self, strToAdd, nodeID):
		assert nodeID >=0 and nodeID < self.treeSize, "In function addStringToNodeLabel value of nodeID out of [0, treeSize) interval"
		currentLabel = self.nodeLabels[nodeID]
		updatedLabel = currentLabel
		if len(currentLabel) - currentLabel.rfind("\n") + len(strToAdd)> 15:
			updatedLabel += "\n"
		updatedLabel += strToAdd
		self.nodeLabels[nodeID] = updatedLabel



	def addStringToEdgeLabel(self, strToAdd, nodeID):
		MAX_LABEL_LENGTH = 25
		assert nodeID >=0 and nodeID < self.treeSize, "In function addStringToNodeLabel value of nodeID out of [0, treeSize) interval"
		currentLabel = self.edgeLabels[nodeID]
		updatedLabel = currentLabel
		if len(currentLabel) - currentLabel.rfind("\n") + len(strToAdd)> MAX_LABEL_LENGTH:
			updatedLabel += "\n"
		updatedLabel += strToAdd
		self.edgeLabels[nodeID] = updatedLabel


	def assignMutVAFsAsNodeLabels(self, bulkMutations):
		for node in range(self.treeSize):
			for mutID in self.mutationsAtNode[node]:
				self.addStringToNodeLabel(floatToStr(bulkMutations[mutID].getVAF()), node)


	def printTree(self, pathOutputFile):
		outputFile = open(pathOutputFile, "w")
		row_column_heads = [""] * self.treeSize
		for i in range(self.treeSize):
			headString = ""
			for mut in self.mutationsAtNode[i]:
				headString += str(mut) + ","
			headString = headString.rstrip(",")
			row_column_heads[i] = headString
		
		outputFile.write("mutsAtNode/mutsAtNode")
		for col in range(self.treeSize):
			if row_column_heads[col] == "":
				row_column_heads[col] = "No_MUT_(ROOT)"
			outputFile.write("\t" + row_column_heads[col])
		outputFile.write("\n")

		for row in range(self.treeSize): 
			print(str(self.ancMatrix[row][row]))
			outputFile.write(row_column_heads[row])
			for col in range(self.treeSize):
				outputFile.write("\t" + str(self.ancMatrix[row][col]))
			outputFile.write("\n")
		outputFile.close()


# Below conflict free matrix is supposed to have unique columns, exactly as I described in one e-mails from today.


def readConflictFreeMatrix(pathConflictFreeMatrix):
	assert os.path.exists(pathConflictFreeMatrix), "In function readConflictFreeMatrix there does not exist file " + pathConflictFreeMatrix
	matrixFile = open(pathConflictFreeMatrix)
	conflictFreeMatrix = []
	matrixFile.readline() #header line
	for line in matrixFile.readlines():
		conflictFreeMatrix.append([int(x) for x in line.strip().split()[1:]])
	matrixFile.close()
	return conflictFreeMatrix


def readMutIDsConflictFreeMatrix(pathConflictFreeMatrix):
	assert os.path.exists(pathConflictFreeMatrix), "There does not exist file " + pathConflictFreeMatrix + ". Function constructTreeFromCFMatrix"
	matrixFile = open(pathConflictFreeMatrix)
	mutIDs = matrixFile.readline().strip().split()[1:]
	matrixFile.close()
	return mutIDs



def conflictFreeMatrixToAncMatrix(conflictFreeMatrix):
	n=len(conflictFreeMatrix[0]) # numMutations
	m=len(conflictFreeMatrix)    # numCells
	ancMatrix = [[0 for column in range(n)] for row in range(n)]

	for mut1 in range(n):
	#	for mut2 in range(mut1+1, n):
		for mut2 in range(n):
			counts = [[0 for i in range(2)] for j in range(2)]
			for cell in range(m):
				counts[conflictFreeMatrix[cell][mut1]][conflictFreeMatrix[cell][mut2]] += 1
			if counts[1][1] >0 and counts[1][0] == 0 and counts[0][1] == 0:
				ancMatrix[mut1][mut2] = 1
			elif counts[1][1] == 0:
				continue
			elif counts[1][0] >= 1 and counts[0][1] == 0:
				ancMatrix[mut1][mut2] = 1
			elif counts[1][0] == 0 and counts[0][1] >= 1:
				ancMatrix[mut2][mut1] = 1
			else:
				print("ERROR in function conflictFreeMatrixToAncMatrix for columns " + str(mut1) + " and " + str(mut2))
				for i in range(2):
					for j in range(2):
						print("Counts[" + str(i) + "," + str(j) + "]=" + str(counts[i][j]))
				print(" ")

	# below we add root to our tree
	for i in range(n):
		ancMatrix[i].append(0)
	ancMatrix.append([1 for i in range(n+1)])
	return ancMatrix					
		
def constructTreeFromConflictFreeMatrix(pathConflictFreeMatrix):
	assert os.path.exists(pathConflictFreeMatrix), "In function constructTreeFromConflictFreeMatrix file " + pathConflictFreeMatrix + "does not exist"
	conflictFreeMatrix = readConflictFreeMatrix(pathConflictFreeMatrix)
	ancMatrix = conflictFreeMatrixToAncMatrix(conflictFreeMatrix)	
	T = Tree(ancMatrix)
	mutIDs = readMutIDsConflictFreeMatrix(pathConflictFreeMatrix) #mutID[i] contains mutations assigned to node i
	for nodeID in range(len(mutIDs)):
		for mutID in mutIDs[nodeID].split(","):
			T.addMutationToNode(mutID, nodeID)
			T.addStringToEdgeLabel(mutID + ", ", nodeID)
	return T

def assertMutIDsIdentity(tree1, tree2):
	#print tree1.getAllMutIDs()
	#print tree2.getAllMutIDs()
	if Set(tree1.getAllMutIDs()) != Set(tree2.getAllMutIDs()):
		print("Error in function identicalMutIDs. Mutation IDs in trees provided are not identical.")
		print(str(tree1.getAllMutIDs()))
		print(str(tree2.getAllMutIDs()))
		sys.exit(2)

def diffLineagesAccurracy(resultTree, trueTree):  #T1 --- first tree 
	assertMutIDsIdentity(resultTree, trueTree)
	mutIDs = resultTree.getAllMutIDs()
	numMutations = len(mutIDs)	
	correctlyInferredDifferentBranches = 0
	totalDifferentBranches = 0
	for i in range(numMutations):
		for j in range(i+1, numMutations):
			mut1 = mutIDs[i]
			mut2 = mutIDs[j]
			resultDependency = resultTree.getMutationsAncestryRelation(mut1, mut2)
			trueDependency	 = trueTree.getMutationsAncestryRelation(mut1, mut2)
			if trueDependency == DIFFERENT_LINEAGES:
				totalDifferentBranches += 1
				if resultDependency == DIFFERENT_LINEAGES:
					correctlyInferredDifferentBranches += 1

	return (float(correctlyInferredDifferentBranches))/totalDifferentBranches

def ancestorDescendantAccurracy(resultTree, trueTree):
	assertMutIDsIdentity(resultTree, trueTree)	
	mutIDs       = resultTree.getAllMutIDs()
	numMutations = len(mutIDs)
	totalPairs   = 0
	correctlyInferred = 0
	for i in range(numMutations):
		for j in range(i+1, numMutations):
			mut1 = mutIDs[i]
			mut2 = mutIDs[j]
			trueRelation     = trueTree.getMutationsAncestryRelation(mut1, mut2)
			inferredRelation = resultTree.getMutationsAncestryRelation(mut1, mut2)
			if trueRelation == SAME_NODE or trueRelation == DIFFERENT_LINEAGES:
				continue
			if trueRelation == ANCESTOR_DESCENDANT:
				totalPairs += 1	
				if inferredRelation == ANCESTOR_DESCENDANT:
					correctlyInferred += 1
			if trueRelation == DESCENDANT_ANCESTOR:
				totalPairs += 1
				if inferredRelation == DESCENDANT_ANCESTOR:
					correctlyInferred += 1
	if totalPairs == 0:
		print("In function ancestorDescendantAccurracy total Pairs is zero")
		return 0
	else:
		return (float(correctlyInferred))/totalPairs

if __name__ == '__main__':

	fileg = sys.argv[1]
	fileilp = sys.argv[2]
	filez3 = sys.argv[3]
	filewbo = sys.argv[4]
	f = fileg
	f = f.replace('.txt', '')
	f = f + '_measures.txt'
	mfile = open(f, 'a')
	GT = constructTreeFromConflictFreeMatrix(fileg)
	
	ITilp = constructTreeFromConflictFreeMatrix(fileilp)
	ADailp = ancestorDescendantAccurracy(ITilp, GT)
	DLailp = diffLineagesAccurracy(ITilp, GT)

	ITz3 = constructTreeFromConflictFreeMatrix(filez3)
	ADaz3 = ancestorDescendantAccurracy(ITz3, GT)
	DLaz3 = diffLineagesAccurracy(ITz3, GT)

	ITwbo = constructTreeFromConflictFreeMatrix(filewbo)
	ADawbo = ancestorDescendantAccurracy(ITwbo, GT)
	DLawbo = diffLineagesAccurracy(ITwbo, GT)

	mfile.write(str('X') + ' '+ str(ADaz3)+ ' '+ str(ADawbo) + ' '+ str('X')+ ' '+ str(DLaz3) + ' '+ str(DLawbo) +'\n')
	mfile.close()
