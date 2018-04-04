import os
from math import *

def readMatrixIntoHash(pathInputFile):
	assert os.path.exists(pathInputFile), "There does not exist file " + pathInputFile
	inputFile  = open(pathInputFile, "r")
	inputLines = inputFile.readlines()
	inputFile.close()
	assert len(inputLines) > 0, "ERROR. Input file " + pathInputFile + " is empty."

	headerEntries	= inputLines[0].strip().split()
	columnIDs	= headerEntries[1:len(headerEntries)]
	numColumns 	= len(columnIDs)
	assert numColumns > 0, "ERROR. First (header) line in " + pathSCFile + " is empty. Exiting!!!"
	inputLinesWithoutHeader = inputLines[1:len(inputLines)]
	D = {}
	for line in inputLinesWithoutHeader:
		lineColumns = line.strip().split()
		rowID = lineColumns[0].strip()
		assert rowID not in D.keys(), "ERROR in function readMatrixIntoHash. " + rowID + " is already in keys."
		D[rowID] = {}
		for i in range(numColumns):
			D[rowID][columnIDs[i]] = int(lineColumns[1+i])
	return D


def get_liklihood(inputSCMatrixFile, outputCFMatrixFile, fn, fp):
	D = readMatrixIntoHash(inputSCMatrixFile)
	E = readMatrixIntoHash(outputCFMatrixFile)
	alpha = float(fp)
	beta  = float(fn)
	missingEntryCharacter = 2 

	objectiveValueFromCFMatrix = 0.0
	cellIDs = E.keys()
	mutIDs  = E[cellIDs[0]].keys()
	dummyVariable = 1
	for i in cellIDs:
		for j in mutIDs:
			if D[i][j] == 1:
				if E[i][j] == 0:
					objectiveValueFromCFMatrix += log(alpha)
				elif E[i][j] == 1:
					objectiveValueFromCFMatrix += log(1-alpha)
			elif D[i][j] == 0:
				if E[i][j] == 1:
					objectiveValueFromCFMatrix += log(beta)
				elif E[i][j] == 0:
					objectiveValueFromCFMatrix += log(1-beta)
			elif D[i][j] == missingEntryCharacter:
				dummyVariable = 1
	return objectiveValueFromCFMatrix
