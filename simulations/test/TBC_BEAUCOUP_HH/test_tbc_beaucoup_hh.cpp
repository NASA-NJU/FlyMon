
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include <ctime>
#include <cmath>
#include "Csver.h"

#define HH_THRESHOLD 1024

// Dataplane config.
const uint32_t TOTAL_MEM = 9216000;
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 3;
const uint32_t BLOCK_SIZE = TOTAL_MEM / BLOCK_NUM / 2;  
const uint32_t SUB_BLOCK_NUM = 1;
const uint32_t coff = 1;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

void measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("./results/heavyhitter/flymon_beaucoup_3d.csv");
    // HOW_LOG(L_INFO, "Construct CM Sketch on TBC, Total Memory %d, %d rows, each with %d counters.", TOTAL_MEM, d, w);
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int task_id = tbc_manager.allocate_beaucoup_1024(BLOCK_NUM, BLOCK_SIZE, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_TIMESTAMP, ACTION_SET_PARAM_TIMESTAMP);
    int count = 0;
    unordered_map<string, int> RealFreq;
    unordered_map<string, int> EstiHH;
    unordered_map<string, int> RealHH;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        RealFreq[str] += 1;
        if(RealFreq[str] >= 1024){
            RealHH[str] = 1;
        }
        int re = tbc_manager.beaucoup_apply(*it);
        if(re  == 1){
            EstiHH[str] = 1;
        } 
    }
    int estimate_right = 0;
    for(auto& esti : EstiHH)
    {
        if(RealHH.find(esti.first) != RealHH.end()){
            estimate_right += 1;
        }
    }
    double precision =  (double)estimate_right / (double)EstiHH.size();
    double recall = (double)estimate_right / (double)RealHH.size();
    double f1 = (2 * precision * recall) / (precision + recall);
    // HOW_LOG(L_DEBUG, "Real Heavyhitter = %d, Estimate Heavyhitter = %d, PR = %.2f, RR = %.2f, F1 Score = %.2f", Real_HH.size(), Esti_HH.size(), precision, recall, f1); 
    delete filter;
    csver.write(TOTAL_MEM/1024, BLOCK_NUM, precision, recall, f1);
    // csver.write(TOTAL_MEM/1024, BLOCK_NUM, precision, recall, f1);
    return;
}

int main(){
    LOG_LEVEL = L_INFO;
    clock_t start = clock();
    DataTrace trace;
    trace.LoadFromFile(".//.//data/fifteen1.dat");
    HOW_LOG(L_INFO, "Dataplane Info: %d TBC, each with %d block, each block contains %d counters, TOTAL %d Bytes.", TBC_NUM, BLOCK_NUM, BLOCK_SIZE, TOTAL_MEM);
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}