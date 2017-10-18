#!/usr/local/bin/Rscript

args <- commandArgs(trailingOnly = TRUE)

file1 <- args[1]
file2 <- gsub(".txt",".outputMatrixUniqueColumns",file1)

train = read.table(file1, header=TRUE)
row.names(train) <- train[,1]
train[,1] <- NULL
features_pair <- combn(names(train), 2, simplify = F) # list all column pairs
toRemove <- c() # init a vector to store duplicates
newNames = 0*c(1:dim(train)[2])
names(newNames) = names(train)
newNames[1:dim(train)[2]] = names(train)
for(pair in features_pair) { # put the pairs for testing into temp objects
	f1 <- pair[1]
	f2 <- pair[2]
	
	if (!(f1 %in% toRemove) & !(f2 %in% toRemove)) {
		if (all(train[[f1]] == train[[f2]])) { # test for duplicates
		    toRemove <- c(toRemove, f2) # build the list of duplicates
		    newNames[f1] = paste0(newNames[f1],',',f2)
		}
	}
}
newNames = setdiff(newNames, toRemove)
train[toRemove] <- NULL
colnames(train) <- newNames
newTrain = data.frame("cellID/mutID"=row.names(train),train)
colnames(newTrain)[1] = gsub(".mutID","/mutID",colnames(newTrain)[1])
colnames(newTrain)[-1] = gsub("\\.",",",colnames(newTrain)[-1])
write.table(newTrain,file2, row.names=FALSE, sep="\t",quote=FALSE)