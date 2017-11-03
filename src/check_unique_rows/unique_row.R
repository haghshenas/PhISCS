#!/usr/local/bin/Rscript

getData <- function(file1) {
	train = read.table(file1, header=TRUE)
	row.names(train) <- train[,1]
	train.T <- t(train[,2:ncol(train)])
	train <- train.T
	features_pair <- combn(colnames(train), 2, simplify = F) # list all column pairs
	toRemove <- c() # init a vector to store duplicates
	newNames = 0*c(1:dim(train)[2])
	names(newNames) = colnames(train)
	newNames[1:dim(train)[2]] = colnames(train)
	for(pair in features_pair) { # put the pairs for testing into temp objects
		f1 <- pair[1]
		f2 <- pair[2]
		if (!(f1 %in% toRemove) & !(f2 %in% toRemove)) {
			if (all(train[,f1] == train[,f2])) { # test for duplicates
				toRemove <- c(toRemove, f2) # build the list of duplicates
				newNames[f1] = paste0(newNames[f1],',',f2)
			}
		}
	}
	newNames = setdiff(newNames, toRemove)
	train <- data.frame(train)
	train[,toRemove] <- NULL
	colnames(train) <- newNames
	train
}
path = "/Users/Farid/Desktop/ground/"
for(id in c(1)) {
	for(s in c(4)) {
		X = list()
		for(k in c(0:2)) {
			file = paste0(path,"simNo_",id,"-n_100-m_40-s_",s,"-minVAF_0.05-cov_2000-k_",k,".SCnoNoise")
			cat(file)
			cat('\n')
			X[[file]] = getData(file)
		}
		for(k1 in c(1:3)) {
			for(k2 in c(1:3)) {
				if(k1 < k2) {
					for(i in c(1:dim(X[[k1]])[2])) {
						for(j in c(1:dim(X[[k2]])[2])) {
							cat(paste0('k=',k1-1,',k=',k2-1,',r=',i,',r=',j,'\t'))
							cat(length(which(X[[k1]][,i]==X[[k2]][,j])))
							cat('\n')
						}
					}
				}
			}
		}
	}
}

a = getData("/Users/Farid/Desktop/ground/simNo_1-n_100-m_40-s_7-minVAF_0.05-cov_2000-k_1.SCnoNoise")
