readLog = function(path, pattern) {
	out = list()
	files <- list.files(path=path, pattern=pattern, full.names=T, recursive=FALSE)
	for(x in files) {
		out[[x]] = try(as.character(read.delim(x, header=FALSE, sep=' ')[,'V2']))
		if (class(out[[x]]) != "try-error") {
			out[[x]] = as.character(read.delim(x, header=FALSE, sep=' ')[,'V2'])
		} else {
			out[[x]] = rep("NA", 17)
		}
	}
	out
}
readOut = function(path, pattern) {
	CSP = list()
	files <- list.files(path=path, pattern=pattern, full.names=T, recursive=FALSE)
	for(x in files) {
		a = read.table(x, header = TRUE, sep = "\t")
		a[,'cellID.mutID'] <- NULL
		CSP[[x]] <- a
	}
	CSP
}

z3_output = readOut("./z3", "*.output")
z3_log_15 = readLog("~/Desktop/result/15", "*.log")
z3_log_16 = readLog("~/Desktop/result/16", "*.log")
z3_log_17 = readLog("~/Desktop/result/17", "*.log")
z3_log_18 = readLog("~/Desktop/result/18", "*.log")
z3_log_19 = readLog("~/Desktop/result/19", "*.log")
z3_log_20 = readLog("~/Desktop/result/20", "*.log")
elim_col_15 <- sapply(z3_log_15, `[[`, 16)
elim_col_16 <- sapply(z3_log_16, `[[`, 16)
elim_col_17 <- sapply(z3_log_17, `[[`, 16)
elim_col_18 <- sapply(z3_log_18, `[[`, 16)
elim_col_19 <- sapply(z3_log_19, `[[`, 16)
elim_col_20 <- sapply(z3_log_20, `[[`, 16)
name <- names(elim_col_15)
names(elim_col_15) <- NULL
names(elim_col_16) <- NULL
names(elim_col_17) <- NULL
names(elim_col_18) <- NULL
names(elim_col_19) <- NULL
names(elim_col_20) <- NULL
MyData <- data.frame(Files=name, W_15=elim_col_15, W_16=elim_col_16, W_17=elim_col_17, W_18=elim_col_18, W_19=elim_col_19, W_20=elim_col_20)
write.table(MyData, file="~/Desktop/result.txt", row.names=FALSE, col.names=TRUE, sep="\t")
#================
files <- list.files(path=paste0(path, "2oct/z3/colElim=0"), pattern="logFile.*.txt", full.names=T, recursive=FALSE)
MyData <- data.frame(Files=files, Z3=Z3, ILP=ILP)
write.table(MyData, file="./result.txt", row.names=FALSE, col.names=TRUE, sep="\t")
#================
fn = c(0.05,0.1,0.15,0.2,0.25,0.3)
n = c(10,20,50)
for(i in n) {
	for (j in fn) {
		ILP = readLog(path, "6sep/ilp1-2", 4, paste0("log.*n_",i,".*fn_",j,".txt"))
		Z3 = readLog(path, "6sep/z3-0", 5, paste0("logFile.*n_",i,".*fn_",j,".txt"))
		cat(mean(Z3))
		cat("\t")
		cat(mean(ILP))
		cat("\n")
	}
	cat("\n")
}
#=================
for(i in c(6:14)) {
	ILP = readLog(path, "6sep/ilp1", i, "log.*.txt")
	Z3 = readLog(path, "6sep/z3", i+1, "logFile.*.txt")
	cat(length(which(ILP!=Z3)))
	cat("\n")
}
#=================
result = c()
i = 1
for(i in 1:180) {
	a = which(CSP1[[i]] != CSP2[[i]])
	result[i] = length(a)
	i = i +1
}
result
files[which(result>0)]
