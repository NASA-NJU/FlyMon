
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include "EMFSD.h"
#include "CommonFunc.h"
#include <fstream>
#include <ctime>
#include <bitset>
#include "Csver.h"


// #define FILE_MRAC_DSITRIBUTION "flow_distribution0.02.txt"  //1MB
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 5;
const uint32_t SUB_BLOCK_NUM = 1;
const uint32_t MEMORY = 8192; 
const uint32_t BLOCK_SIZE = MEMORY / 2;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;
double measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("./result/cardinality/hyperloglog.csv");
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int hll_task_id = tbc_manager.allocate_hyperloglog_new(BLOCK_SIZE, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_IPPAIR_HASH, 0);
    if(hll_task_id < 0) {
        return -1;
    }
    unordered_map<string, int> Real_Freq;
    uint32_t max_size = 0;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        Real_Freq[str]++;
        if(Real_Freq.size() >= 20000){
            break;
        }
    } 
    map<uint16_t, map<uint16_t, vector<uint16_t>>> hll_sketch;
    tbc_manager.query(hll_task_id, hll_sketch);
    auto& hll_data = hll_sketch[0][0];
    uint32_t estimate_distinct = HyperLogLogCalc(hll_data);
    double real_distinct = 20000;
    double re = abs(real_distinct - estimate_distinct) / real_distinct;
    csver.write(MEMORY, re);
    delete filter;
    return 0;
}

int main(int argc, char* argv[]){
    LOG_LEVEL = L_DEBUG;
    clock_t start = clock();
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    trace.LoadFromFile(".//.//data/fifteen1.dat");
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}