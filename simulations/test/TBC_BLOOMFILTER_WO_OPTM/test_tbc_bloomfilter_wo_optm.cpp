
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include <ctime>
#include <cmath>
#include "Csver.h"

#define HH_THRESHOLD 1024

// Dataplane config.
const uint32_t TOTAL_MEM = 1024000;
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 3;
const uint32_t BLOCK_SIZE = TOTAL_MEM / TBC_NUM/ BLOCK_NUM / 2;  
const uint32_t SUB_BLOCK_NUM = 1;
const uint32_t coff = 1;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

void measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("./result/existence/bloom_without_optmi.csv");
    // HOW_LOG(L_INFO, "Construct CM Sketch on TBC, Total Memory %d, %d rows, each with %d counters.", TOTAL_MEM, d, w);
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int task_id = tbc_manager.allocate_bloom_filter_wo_optm(BLOCK_NUM, BLOCK_SIZE, filter, ACTION_SET_KEY_IPPAIR);
    unordered_map<string, int> InsertSet;
    unordered_map<string, int> Real;
    int count = 0;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        Real[str] += 1;
            // Insert it.
        if(InsertSet.size() < 20000){
            tbc_manager.insert_bloom_filter_wo_optm(task_id, (uint8_t *)str.c_str(), 8);
            InsertSet[str] += 1;
        }
        count += 1;
    }
    unordered_map<string, int> posiSet;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        int re = tbc_manager.bloom_apply(*it);
        if(re  == 1){
            posiSet[str] += 1;
        }
    }
    double fp = 0;
    double tp = 0;
    double f = 0;
    for(auto& real : Real){
        if(InsertSet.find(real.first) == InsertSet.end()){
            f += 1;
        }
    }
    for(auto& kv : posiSet){
        auto& key = kv.first;
        if(InsertSet.find(key) == InsertSet.end()){
            fp += 1;
        }else{
            tp += 1;
        }
    }
    double re_fp = fp / f;
    double re_tp = tp / InsertSet.size();
    // csver.write(1024000/1024, 3, Real.size(), InsertSet.size(), f, fp, re_fp, tp, re_tp);
    csver.write(1024000/1024, re_fp);
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