/*******************************************************************************
* Author: Ehsan Haghshenas
********************************************************************************
* Solving the new CSP formulation from Salem by Max-SAT
*******************************************************************************/

#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unistd.h>
#include <sys/time.h>
#include <sys/resource.h>

using namespace std;

#define MAX_CELL 300
#define MAX_MUT 200

bool IS_WCNF = true;
int  FN_W = 0;
int  FP_W = 0;

int mat[MAX_CELL][MAX_MUT]; // the 0/1 matrix
vector<string> cellId;
vector<string> mutId;
int var_x[MAX_CELL][MAX_MUT]; // X variables for the maxSAT
int var_y[MAX_CELL][MAX_MUT]; // Y variables for the maxSAT; if(Iij==0) Yij=Xij and if(Iij==1) Yij=~Xij
int weight_x[MAX_CELL][MAX_MUT]; // weight of X variables
int var_b[MAX_MUT][MAX_MUT][2][2];
pair<int, int> map_x2ij[MAX_CELL * MAX_MUT + 10]; // maps X variables to matrix position (row and column)
vector<string> wcnf; // the set of clauses for conflicts

int numMut; // actual number of mutations (columns)
int numCell; // actual number of cells (rows)
int numVar; // number of X variables
int numAuxVar; // number of B variables
int numZero; // number of zeros in the input matrix
int numOne; // number of ones in the input matrix

string int2str(int n)
{
	ostringstream sout;
	sout<< n;
	return sout.str();
}

int str2int(string s)
{
	int retVal;
	istringstream sin(s.c_str());
	sin >> retVal;
	return retVal;
}

void get_input_data(string path)
{
	int i, j;
	string tmpStr;
	string line;
    ifstream fin(path.c_str());
    if(fin.is_open() == false)
    {
        cerr<< "Could not open file: " << path << endl;
        exit(EXIT_FAILURE);
    }
	// process the header
    getline(fin, line);
    istringstream sin1(line);
    while(sin1 >> tmpStr)
    {
        mutId.push_back(tmpStr);
    }
    numMut = mutId.size() - 1;
    //
	i = 0;
	while(getline(fin, line))
	{
		istringstream sin(line);
        sin >> tmpStr; // cell name
        cellId.push_back(tmpStr);
		for(int j = 0; j < numMut; j++)
		{
			sin >> mat[i][j];
		}
		i++;
	}
    numCell = i;
    fin.close();
}

void set_xy_variables()
{
	int i, j;
	numVar = 0;
	numZero = 0;
	numOne = 0;
	for(i = 0; i < numCell; i++)
	{
		for(j = 0; j < numMut; j++)
		{
			numVar++;
			var_x[i][j] = numVar;
			map_x2ij[numVar] = make_pair<int, int>(i, j);
			if(mat[i][j] == 0)
			{
				var_y[i][j] = var_x[i][j];
				weight_x[i][j] = FN_W;
				numZero++;
			}
			else // mat[i][j] == 1
			{
				var_y[i][j] = -1 * var_x[i][j];
				weight_x[i][j] = FP_W;
				numOne++;
			}
		}
	}
}

void set_b_variables()
{
	int i, j, p, q;
	numAuxVar = 0;
	for(p = 0; p < numMut; p++)
	{
		for(q = 0; q < numMut; q++)
		{
			for(i = 0; i < 2; i++)
			{
				for(j = 0; j < 2; j++)
				{
					numAuxVar++;
					var_b[p][q][i][j] = numVar + numAuxVar;
				}
			}
		}
	}
}

void add_hard_clauses()
{
	int i;
	int p, q;
	for(i = 0; i < numCell; i++)
	{
		for(p = 0; p < numMut; p++)
		{
			for(q = p; q < numMut; q++)
			{
				// ~Yip v ~Yiq v Bpq11
				wcnf.push_back(int2str(-1*var_y[i][p]) + " " + int2str(-1*var_y[i][q]) + " " + int2str(var_b[p][q][1][1]));
				// Yip v ~Yiq v Bpq01
				wcnf.push_back(int2str(var_y[i][p]) + " " + int2str(-1*var_y[i][q]) + " " + int2str(var_b[p][q][0][1]));
				// ~Yip v Yiq v Bpq10
				wcnf.push_back(int2str(-1*var_y[i][p]) + " " + int2str(var_y[i][q]) + " " + int2str(var_b[p][q][1][0]));
				// ~Bpq01 v ~Bpq10 v ~Bpq11
				wcnf.push_back(int2str(-1*var_b[p][q][0][1]) + " " + int2str(-1*var_b[p][q][1][0]) + " " + int2str(-1*var_b[p][q][1][1]));
			}
		}
	}
}

void save_WCNF(string path)
{
	int i, j;
	int hardWeight = numZero * FN_W + numOne * FP_W + 1;
	ofstream fout(path.c_str());
	if(IS_WCNF)
	{
		fout<< "p wcnf " << numVar + numAuxVar << " " << wcnf.size() + numVar << "\n";
	}
	else
	{
		fout<< "p wcnf " << numVar + numAuxVar << " " << wcnf.size() + numVar << " " << hardWeight << "\n";
	}
	// y variable clauses
	for(i = 1; i <= numVar; i++)
	{
		fout<< weight_x[map_x2ij[i].first][map_x2ij[i].second] << " " << -1*i << " 0\n";
	}
	// conflict clauses
	for(i = 0; i < wcnf.size(); i++)
	{
		fout<< hardWeight << " " << wcnf[i] << " 0\n";
	}

	fout.close();
}

bool parse_maxsat_output(string path, int &flip, int &flip01, int &flip10)
{
    flip = 0;
    flip01 = 0;
    flip10 = 0;
    string line;
    bool oLine = false, sLine = false, vLine = false;
    ifstream fin(path.c_str());
    while(getline(fin, line))
    {
        if(line[0] == 'o')
        {
            oLine = true;
        }
        if(line[0] == 's')
        {
            sLine = true;
        }
        if(line[0] == 'v')
        {
            vLine = true;
            // update the input matrix
            int tmpVar;
            istringstream sin(line.substr(1));
            while(sin >> tmpVar)
            {
                if(tmpVar > 0 && tmpVar <= numVar)
                {
                	flip++;
                	flip01 += (mat[map_x2ij[tmpVar].first][map_x2ij[tmpVar].second] == 0);
                	flip10 += (mat[map_x2ij[tmpVar].first][map_x2ij[tmpVar].second] == 1);
                	// flip 0 -> 1 and 1 -> 0
                    mat[map_x2ij[tmpVar].first][map_x2ij[tmpVar].second] = 1 - mat[map_x2ij[tmpVar].first][map_x2ij[tmpVar].second];
                }
            }
        }
    }
    fin.close();
    return (oLine && sLine && vLine);
}

void save_updated_matrix(string path)
{
    int i, j;
    ofstream fout(path.c_str());
    // header
    for(i = 0; i < mutId.size(); i++)
    {
        fout<< mutId[i] << (i < mutId.size() - 1 ? "\t" : "");
    }
    fout<< "\n";
    //content
    for(i = 0; i < numCell; i++)
    {
        fout<< cellId[i] << "\t";
        for(j = 0; j < numMut; j++)
        {
            fout<< mat[i][j] << (j < numMut - 1 ? "\t" : "");
        }
        fout<< "\n";
    }

    fout.close();
}

string get_file_name(string path)
{
    size_t pos = path.find_last_of("/");
    if(pos != string::npos)
    {
        return path.substr(pos+1);
    }
    else
    {
        return path;
    }
}

string get_dir_path(string path)
{
    size_t pos = path.find_last_of("/");
    if(pos != string::npos)
    {
        return path.substr(0, pos);
    }
    else
    {
        return "";
    }
}

string get_exe_path()
{
  char path[10000];
  ssize_t count = readlink( "/proc/self/exe", path, 10000);
  return string(path, (count > 0) ? count : 0);
}

// double getCpuTime()
// {
// 	struct rusage t;
// 	getrusage(RUSAGE_SELF, &t);
// 	return t.ru_utime.tv_sec + t.ru_utime.tv_usec / 1000000.0 + t.ru_stime.tv_sec + t.ru_stime.tv_usec / 1000000.0;
// }

double getRealTime()
{
	struct timeval t;
	struct timezone tz;
	gettimeofday(&t, &tz);
	return t.tv_sec + t.tv_usec / 1000000.0;
}

int main(int argc, char *argv[])
{
	if(argc < 7)
	{
		cerr << "Wrong arguments!" << endl;
		cerr << "USAGE: ./runMaxSAT noisyMatrix.in outputDir wcnf/pwcnf qmaxsat/openwbo fn_weight fp_weight" << endl;
		exit(EXIT_FAILURE);
	}
	// int i, j, k;
	// int p, q;
	string cmd;
    
    string exeDir = get_dir_path(get_exe_path());
    string pathNoisy = argv[1];
    string workingDir = argv[2];
    // wcnf or pwcnf
    string arg_str = argv[3];
    if(arg_str == "wcnf")
    	IS_WCNF = true;
    else
    	IS_WCNF = false;
    // qmaxsat or openwbo
    arg_str = argv[4];
    string maxSAT_exe;
    if(arg_str == "qmaxsat")
    	maxSAT_exe = exeDir + "/solver/qmaxsat/qmaxsat14.04auto-glucose3_static";
    else if(arg_str == "openwbo")
    	maxSAT_exe = exeDir + "/solver/open-wbo/open-wbo_glucose4.1_static";
    else
    	maxSAT_exe = "noSolver";
    // fn and fp weight
    FN_W = str2int(argv[5]);
    FP_W = str2int(argv[6]);

    // create working directory if does not exist
    cmd = "mkdir -p " + workingDir;
    system(cmd.c_str());
    string fileName = workingDir + "/" + get_file_name(pathNoisy);

    ofstream fLog((fileName + ".log").c_str());
    if(fLog.is_open() == false)
    {
        cerr<< "Could not open file: " << fileName + ".log" << endl;
        exit(EXIT_FAILURE);
    }
    fLog.precision(2);
    fLog<< fixed;

    // double cpuTime = getCpuTime();
	double realTime = getRealTime();

	get_input_data(pathNoisy);
	// formulate as Max-SAT
	set_xy_variables();
	set_b_variables();
	add_hard_clauses();
	save_WCNF(fileName + ".maxSAT.in");
    
    // run Max-SAT solver
    double maxsatTime = getRealTime();
    cmd = maxSAT_exe + " " + fileName + ".maxSAT.in" + " > " + fileName + ".maxSAT.out";
    system(cmd.c_str());
    maxsatTime = getRealTime() - maxsatTime;

    int numFlip = -1;
    int numFlip01 = -1;
    int numFlip10 = -1;
    if(parse_maxsat_output(fileName + ".maxSAT.out", numFlip, numFlip01, numFlip10) == true)
    {
        // solution is found, save it!
        save_updated_matrix(fileName + ".updated");
        fLog<< "FLIPS_IN_SOLUTION: " << numFlip << "\n";
        fLog<< "TOTAL_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: " << numFlip01 + numFlip10 << "\n";
        fLog<< "0_1_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: " << numFlip01 << "\n";
        fLog<< "1_0_FLIPS_REPORTED_BY_SOLUTION_COMPARED_TO_NOISY: " << numFlip10 << "\n";
    }

    fLog<< "MODEL_BUILD_TIME: " << getRealTime() - realTime - maxsatTime << "\n";
    fLog<< "RUNNING_TIME_SECONDS: " << maxsatTime << "\n";
    fLog.close();

	return EXIT_SUCCESS;
}
