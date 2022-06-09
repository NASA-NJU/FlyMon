
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include <ctime>
#include <fstream>
#include "Csver.h"


#define HH_THRESHOLD 4096
const uint32_t TOTAL_MEM = 409600;
const uint32_t TBC_NUM =   1;
const uint32_t BLOCK_NUM = 3;
const uint32_t BLOCK_SIZE = TOTAL_MEM / BLOCK_NUM / 2;  // each counter use 2 Bytes.
const uint32_t SUB_BLOCK_NUM = 16;
const uint32_t coff = 1;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

uint16_t count_min( Manager& manager,
                    int task_id,
                    map<uint16_t, map<uint16_t, vector<uint16_t>>>& sketch,
                    const uint8_t* key,
                    int key_len, int coff)
{
    uint32_t min = 0x1f1f1f1f;
    for(auto& tbc : sketch){ // tbc, block, coin, data.
        uint32_t tbc_id = tbc.first;
        double value = 0.0;
        for(auto& block : tbc.second){
            uint32_t block_id = block.first;
            uint32_t address = manager.get_address(task_id, tbc_id, block_id, key, key_len);
            value = coff * sketch[tbc_id][block_id][address];
            if(value < min)
                min = value;
        }
    }
    if(min == 0x1f1f1f1f)
        min = 0;
    return min;
}


vector<double> measure_main(DataTrace& trace, Manager& tbc_manager){
    // HOW_LOG(L_INFO, "Construct CM Sketch on TBC, Total Memory %d, %d rows, each with %d counters.", TOTAL_MEM, d, w);
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    //CSVer csver_fs("");
    CSVer csver_hv("./results/heavyhitter/flymon_sumax3d.csv");
    int task_id = tbc_manager.allocate_cusketch(BLOCK_NUM, BLOCK_SIZE, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_CONST);
    if(task_id < 0){
        return {0,0,0,0};
    }
    unordered_map<string, int> Real_Freq;
    uint64_t total_size = 0;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        Real_Freq[str]++;
        total_size++;
    }

    map<uint16_t, map<uint16_t, vector<uint16_t>>> sketch; //tbc, block, array.
    tbc_manager.query(task_id, sketch);
    vector< pair<string, int> > Esti_HH;
    vector< pair<string, int> > Real_HH;
    double temp_weighted_error_sum = 0;
    double temp_relative_error_sum = 0;
    for (auto& item : Real_Freq){
        string key = item.first;
 		int estimate = count_min(tbc_manager, task_id, sketch, (const uint8_t *)key.c_str(), 8, coff);
		double relative_error = abs(item.second - estimate) / (double)item.second;
        double x_error = abs(item.second - estimate) / (double)item.second;
        if(item.second > HH_THRESHOLD){
            Real_HH.push_back(make_pair(key, item.second));
        }
        if(estimate > HH_THRESHOLD){
            Esti_HH.push_back(make_pair(key, estimate));
        }
		temp_weighted_error_sum += x_error;
        temp_relative_error_sum += x_error/item.second;
        // HOW_LOG(L_DEBUG, "Flow %s=>%s, real=%d, estimate=%d.", TracePacket::bytes_to_ip_str((uint8_t*)item.first.c_str()).c_str(), 
        //                              TracePacket::bytes_to_ip_str((uint8_t*)item.first.c_str()+4).c_str(), item.second, estimate);   
    }

    int estimate_right = 0;
    double hh_relative_error_sum = 0;
    for(int i = 0; i < (int)Esti_HH.size(); ++i)
    {
        string key = Esti_HH[i].first;
        // HOW_LOG(L_DEBUG, "<%s, %d>", TracePacket::b, est_heavy_hitters[i].second); 
        for(int j = 0; j < (int)Real_HH.size(); ++j)
        {
            if(Real_HH[j].first == key){
                hh_relative_error_sum +=  abs(Real_HH[j].second - Esti_HH[i].second) / (double)Real_HH[j].second;
                // HOW_LOG(L_DEBUG, "Heavy Hitter %d, Real %d, Estimate %d", j, Real_HH[j].second, Esti_HH[i].second); 
                estimate_right += 1;
                break;
            }
        }
    }
    double precision =  (double)estimate_right / (double)Esti_HH.size();
    double recall = (double)estimate_right / (double)Real_HH.size();
    double f1 =  (2 * precision * recall) / (precision + recall);
    // HOW_LOG(L_DEBUG, "Real Heavyhitter = %d, Estimate Heavyhitter = %d, PR = %.2f, RR = %.2f, F1 Score = %.2f", Real_HH.size(), Esti_HH.size(), precision, recall, f1); 
    delete filter;
    // csver_fs.write(TOTAL_MEM/1024, TBC_NUM, BLOCK_NUM, Real_Freq.size(), temp_relative_error_sum/Real_Freq.size());
    csver_hv.write(TOTAL_MEM/1024, TBC_NUM, BLOCK_NUM, Real_Freq.size(), precision, recall, f1);
    return {temp_relative_error_sum/Real_Freq.size(), temp_weighted_error_sum/total_size, precision, recall, f1, hh_relative_error_sum/estimate_right};
}

int main(){

    clock_t start = clock();
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    // trace.LoadFromFile("../data/WIDE/test.dat");
    // trace.LoadFromFile("../data/WIDE/ten_sec_1.dat");
     trace.LoadFromFile(".//.//data/fifteen1.dat");
    HOW_LOG(L_INFO, "Dataplane Info: %d TBC, each with %d block, each block contains %d counters, TOTAL %d Bytes.", TBC_NUM, BLOCK_NUM, BLOCK_SIZE, TOTAL_MEM);
    auto& tbc_manager = Manager::getDataplane();
    vector<double> result = measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}