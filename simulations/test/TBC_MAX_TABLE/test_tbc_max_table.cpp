
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include <ctime>
#include <cmath>
#include "Csver.h"

#define HH_THRESHOLD 1024

// Dataplane config.
const uint32_t TOTAL_MEM = 10240000;
const uint32_t TBC_NUM =   3;
const uint32_t BLOCK_NUM = 3;
const uint32_t BLOCK_SIZE = TOTAL_MEM /  3 / BLOCK_NUM;  
const uint32_t SUB_BLOCK_NUM = 1;
const uint32_t coff = 1;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

void measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("./results/max_interval_time/tbc_maxtable_max_interval.csv");
    // HOW_LOG(L_INFO, "Construct CM Sketch on TBC, Total Memory %d, %d rows, each with %d counters.", TOTAL_MEM, d, w);
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    vector<int> task_ids;
    for(uint32_t i=0; i<3; ++i){
        task_ids.push_back(tbc_manager.allocate_max_interval(BLOCK_SIZE, filter, ACTION_SET_KEY_IPPAIR));
    }
    unordered_map<string, uint64_t> RealLastTime;
    unordered_map<string, uint64_t> RealInterval;
    int count = 0;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        uint64_t last_time = (RealLastTime[str] == 0)? (*it)->getTimestamp_us() : RealLastTime[str];
        RealLastTime[str] =  (*it)->getTimestamp_us();  // update last time.
        uint64_t interval = (*it)->getTimestamp_us() - last_time;
        RealInterval[str] =  RealInterval[str] > interval ? RealInterval[str] : interval;  // update last time.
    }
    count = 0;
    HOW_LOG(L_INFO, "Process packets done!");
    double re_sum = 0;
    vector<map<uint16_t, map<uint16_t, vector<uint16_t>>>> sketches(3);
    for(uint32_t i=0; i<3; ++i){
        tbc_manager.query(task_ids[i], sketches[i]);
    }
    for(auto& kv : RealInterval){
        double real_intv = static_cast<double>(kv.second);
        double esti_intv = 0x1f1f;
        for(uint32_t i=0; i<3; ++i){
            int task_id = task_ids[i];
            uint32_t address = tbc_manager.get_address(task_id, i, 2, (const uint8_t *)kv.first.c_str(), 8);
            uint16_t temp = sketches[i][i][2][address];  // a little wield
            esti_intv = esti_intv < temp ? esti_intv : temp;
        }
        re_sum += abs(esti_intv - real_intv) / real_intv;
    }
    csver.write(TOTAL_MEM/1024, 3, re_sum / RealInterval.size());
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