
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include <ctime>
#include <cmath>
#include "Csver.h"

// Dataplane config.
const uint32_t TOTAL_MEM = 40960;
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 3;
const uint32_t BLOCK_SIZE = TOTAL_MEM / BLOCK_NUM / 2;  
const uint32_t SUB_BLOCK_NUM = 1;
const uint32_t coff = 1;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

void measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("./results/ddos/flymon_beaucoup_3d.csv");
    // HOW_LOG(L_INFO, "Construct CM Sketch on TBC, Total Memory %d, %d rows, each with %d counters.", TOTAL_MEM, d, w);
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    // int task_id = tbc_manager.allocate_beaucoup_128(BLOCK_NUM, BLOCK_SIZE, filter, ACTION_SET_KEY_IPDST, ACTION_SET_VAL_IPSRC_HASH, ACTION_SET_PARAM_IPSRC);
    int task_id = tbc_manager.allocate_beaucoup_256(BLOCK_NUM, BLOCK_SIZE, filter, ACTION_SET_KEY_IPDST, ACTION_SET_VAL_IPSRC_HASH, ACTION_SET_PARAM_IPSRC);
    int count = 0;
    unordered_map<string, int> EstiDDoSV;
    unordered_map<string, int> RealDDoSV;
    unordered_map<string, vector<string>> ground_truth;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        string ipdst((const char*)((*it)->getDstBytes()), 4);
        string ipsrc((const char*)((*it)->getSrcBytes()), 4);
        if(find(ground_truth[ipdst].begin(), ground_truth[ipdst].end(), ipsrc) == ground_truth[ipdst].end()){
            ground_truth[ipdst].push_back(ipsrc);
        }
        int re = tbc_manager.beaucoup_apply(*it);
        if(re  == 1){
            EstiDDoSV[ipdst] = 1;
        } 
    }
    for(auto& ipdst : ground_truth){
        uint16_t src_num = ipdst.second.size();
        if(src_num >= 256) RealDDoSV[ipdst.first] = 1;
    }
    int estimate_right = 0;
    for(auto& esti : EstiDDoSV)
    {
        if(RealDDoSV.find(esti.first) != RealDDoSV.end()){
            estimate_right += 1;
        }
    }
    double precision =  (double)estimate_right / (double)EstiDDoSV.size();
    double recall = (double)estimate_right / (double)RealDDoSV.size();
    double f1 = (2 * precision * recall) / (precision + recall);
    HOW_LOG(L_DEBUG, "Real Heavyhitter = %d, Estimate Heavyhitter = %d, PR = %.2f, RR = %.2f, F1 Score = %.2f", RealDDoSV.size(), EstiDDoSV.size(), precision, recall, f1); 
    delete filter;
    csver.write(TOTAL_MEM/1024, BLOCK_NUM, precision, recall, f1);
    return;
}

int main(){
    LOG_LEVEL = L_INFO;
    clock_t start = clock();
    DataTrace trace;
    trace.LoadFromFile(".//.//data/sixty_sec_0.dat");
    HOW_LOG(L_INFO, "Dataplane Info: %d TBC, each with %d block, each block contains %d counters, TOTAL %d Bytes.", TBC_NUM, BLOCK_NUM, BLOCK_SIZE, TOTAL_MEM);
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}