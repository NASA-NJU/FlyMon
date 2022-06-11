
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include "EMFSD.h"
#include <fstream>
#include <ctime>
#include <bitset>
#include "Csver.h"

// #define FILE_MRAC_DSITRIBUTION "flow_distribution0.02.txt"  //1MB
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 1;
const uint32_t SUB_BLOCK_NUM = 1;
const uint32_t BLOCK_SIZE = 1000*1024/2;


using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

uint32_t get_max(const unordered_map<string, int>& data){
    uint32_t max = 0;
    for(auto& item : data){
        if(item.second > max) 
        {
            max = item.second;
        }
    }
    return max;
}

double get_entropy(const vector<double>& dist){
    unordered_map<int, int> size_map;
    double m = 0;
    for(uint32_t i=1; i<dist.size(); ++i){
        m += i * dist[i];
    }
    double entropy = 0;
    for(uint32_t i=1; i<dist.size(); ++i){
        double p = i/m;
        entropy += dist[i] * p *log2(p);
    }
    return -1*entropy;
}

double calc_wmre(const vector<double>& gt_dist, const vector<double>& est_dist){
    uint32_t max_size = gt_dist.size() > est_dist.size() ? gt_dist.size()  : est_dist.size();
    double molecule = 0;
    double denominator = 0;
    for(int i=0; i<max_size; ++i){
        double gt_value = (i >= gt_dist.size())? 0 : gt_dist[i];
        double est_value = (i >= est_dist.size())? 0 : est_dist[i];
        molecule = molecule + abs(gt_value - est_value);
        denominator = denominator + (gt_value + est_value) / 2;
    }
    return molecule / denominator;
}

double measure_main(DataTrace& trace, Manager& tbc_manager){
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int task_id = tbc_manager.allocate_cmsketch(1, BLOCK_SIZE, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_CONST);
    if(task_id < 0){
        return -1;
    }
    unordered_map<string, int> Real_Freq;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        Real_Freq[str]++;
    }
    map<uint16_t, map<uint16_t, vector<uint16_t>>> sketch; //tbc, block, array.
    tbc_manager.query(task_id, sketch);
    vector<double> dist_groundtruth;
    // get ground truth distribution.
    dist_groundtruth.resize(get_max(Real_Freq)+1, 0);
    for(auto& flow : Real_Freq){
        dist_groundtruth[flow.second] += 1;
    }
    vector<double> dist_est;
    CalcDistribution(sketch[0][0], dist_est);
    double wmre = calc_wmre(dist_groundtruth, dist_est);
    double entrypy_real = get_entropy(dist_groundtruth);
    double entrypy_esti = get_entropy(dist_est);
    double re = abs(entrypy_esti - entrypy_real) / entrypy_real;
    CSVer csver("./results/entropy/flymon_mrac.csv");
    // csver.write(1000, wmre, re);
    csver.write(1000, re);
    delete filter;
}

int main(int argc, char* argv[]){
    clock_t start = clock();
    DataTrace trace;
    trace.LoadFromFile(".//.//data/fifteen1.dat");
    // Load distribution.
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}