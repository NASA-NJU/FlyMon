
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include <ctime>


// Dataplane config.
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 3;
const uint32_t BLOCK_SIZE = 32;

int main(){

    clock_t start = clock();
    DataTrace trace;
    trace.LoadFromFile("../data/WIDE/head1000.dat");
    HOW_LOG(L_INFO, "Dataplane Info: %d TBC, each with %d block, each block contains %d counters", TBC_NUM, BLOCK_NUM, BLOCK_SIZE);
    auto& tbc_manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, 1>::getDataplane();

    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int task_id = tbc_manager.allocate_cmsketch(3, 2, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_CONST, 1);
    if(task_id < 0){
        HOW_LOG(L_INFO, "Dataplane ERROR");
        exit(1);
    }
  
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
    }
    map<uint16_t, map<uint16_t, vector<uint16_t>>> sketch; //tbc, block, array.
    tbc_manager.query(task_id, sketch, true);
    delete filter;
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}