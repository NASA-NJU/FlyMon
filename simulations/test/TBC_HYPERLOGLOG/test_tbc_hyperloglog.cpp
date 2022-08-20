
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include "EMFSD.h"
#include <fstream>
#include <ctime>
#include <bitset>


// #define FILE_MRAC_DSITRIBUTION "flow_distribution0.02.txt"  //1MB
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 3;
const uint32_t SUB_BLOCK_NUM = 16;
const uint32_t m = 2048;
const double coff = 1;
const uint32_t BLOCK_SIZE = m * coff;


using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

vector<double> dist;
double measure_main(DataTrace& trace, Manager& tbc_manager){
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int hll_task_id = tbc_manager.allocate_hyperloglog_new(m, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_IPPAIR_HASH);
    if(hll_task_id < 0) {
        return -1;
    }
    unordered_map<string, int> Real_Freq;
    unordered_map<string, int> TBC_Gt;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        Real_Freq[str]++;
    } 
    map<uint16_t, map<uint16_t, vector<uint16_t>>> hll_sketch;
    tbc_manager.query(hll_task_id, hll_sketch);
    tbc_manager.getTaskStatistics(hll_task_id, TBC_Gt);
    double estimate_distinct = 0.0;
    for(auto& tbc : hll_sketch){
        for(auto& block: tbc.second){
            vector<uint16_t>& data = block.second;
            double estimate = 0;                
            double V = 0;
            double dZ = 0;
            double Z = 0;
            double E = 0;
            for(auto& bits : data){
                if(bits == 0){
                    V+=1;
                }
                int p = 0;
                for(int i = 31; i >= 0; --i){
                    uint32_t bit = (bits & (1<<i)) >> i;
                    if(bit == 0){
                        p = (31 - i) + 1;
                        break;
                    }
                }
                dZ += pow(2, -1*p);
            }
            Z = 1.0 / dZ;
            E = 0.679 * pow(m, 2) * Z;
            double E_star = 0;
            if (E < 2.5*m){
                E_star = (V != 0)? m * log2(m/V) : E;
            }
            double pow232 = pow(2, 32);
            E_star = (E <= pow232/30)? E : -1*pow232*log2(1-E/pow232);
            // estimate_distinct = E_star / a;
            estimate_distinct = E_star;
        }
    }
    double E1 = 0;
    double L = 0;
    for(auto& gt : TBC_Gt){
        if(gt.second == 1){
            E1 += 1;
        }
        L += gt.second;
    }
    double P0 = E1 / L;
    HOW_LOG(L_INFO, "E1 = %.1f, L = %.1f, Total = %d, Rate = %.2f", E1, L, trace.size(), L/trace.size());
    double fixed_estimate_distinct = estimate_distinct * (1/(1-P0));
    double real_distinct = static_cast<double>(Real_Freq.size());
    double relative_error = abs(fixed_estimate_distinct - real_distinct) / real_distinct;
    HOW_LOG(L_INFO, "Distinct Real : %.2f, Distinct Estimate: %.2f, After Fixed: %.2f, RE : %.2f", 
                     real_distinct, 
                     estimate_distinct, 
                     fixed_estimate_distinct,
                     relative_error);
    delete filter;
    return relative_error;
}


int main(int argc, char* argv[]){
    clock_t start = clock();
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    // trace.LoadFromFile("../data/WIDE/test.dat");
    // trace.LoadFromFile("../data/WIDE/ten_sec_1.dat");
    trace.LoadFromFile("../data/WIDE/fifteen1.dat");
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}