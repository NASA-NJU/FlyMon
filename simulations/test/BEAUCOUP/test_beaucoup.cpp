#include "BeauCoup.h"
#include "DataTrace.h"
#include "HowLog/HowLog.h"
#include <unordered_map>
#include <string>
#include <vector>
#include <bitset>
#include "TracePacket.h"
#include "Csver.h"
#include <algorithm>
using namespace std;

const uint32_t TOTAL_MEMORY = 400 * 1024;
const uint32_t Threshold = 1024;
int main(){

    LOG_LEVEL = L_DEBUG;
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/test.dat");
    // trace.LoadFromFile("/home/hzheng/workSpace/SketchLab/data/WIDE/fifteen1.dat");
    trace.LoadFromFile(".//.//data/fifteen1.dat");
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/fifteen1.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
    BeauCoup<32, 1>* bc = new BeauCoup<32, 1>(TOTAL_MEMORY);
    
    bc->register_attr_table(FIELD_TSTAMP);
    // bc->register_attr_table(FIELD_IPPAIR);
    int qid = bc->register_query(FIELD_IPPAIR, FIELD_TSTAMP);  // heavy hitter
    // int qid = bc->register_query(FIELD_CONST, FIELD_IPPAIR);  // cardinality
    // uint32_t coupon_num = 32;
    // M=32, N=32, P=0.031250, Target=129.87, Var=39.03, RE=0.30
    // M=32, N=32, P= 1/64, Target=259.87, Var=39.03, RE=0.30
    // M=4, N=4, P=0.250000, Target=8.33, Var=3.80, RE=0.46
    uint32_t coupon_num = 32 ; // 32  19  131072 ===> 115128;
    for(uint32_t i=0; i<coupon_num; ++i){
        bitset<8> bits(i);
        string coins = bits.to_string() + "*";
        bc->register_query_coupon(qid, coins, i);
    }
	unordered_map<string, uint32_t> ground_truth;
    vector<string> heavy_esti;
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        ground_truth[str]++;
        int re = bc->apply(*it);
        if(re == 1){
            // exceed the threshold.
            // string key = TracePacket::bytes_to_ip_str((uint8_t*)str.c_str());
            if(find(heavy_esti.begin(), heavy_esti.end(), str) == heavy_esti.end())
                heavy_esti.push_back(str);
        }
    }
    vector<string> real_heavy;
    for(auto& key : ground_truth){
        uint32_t src_num = key.second;
        if(src_num >= Threshold) real_heavy.push_back(key.first);
    }
    // HOW_LOG(L_DEBUG, "Real DDoS victims num: %u", real_ddos.size());
    // for(auto& real : real_ddos){
    //     HOW_LOG(L_DEBUG, "%s", real.c_str());
    // }
    // HOW_LOG(L_DEBUG, "Estimate DDoS victims: %u", esti_ddos.size());
    // for(auto& esti : esti_ddos){
    //     HOW_LOG(L_DEBUG, "%s", esti.c_str());
    // }
    uint32_t estimate_right = 0;
    for(uint32_t i = 0; i < real_heavy.size(); ++i)
    {
        for(uint32_t j = 0; j < heavy_esti.size(); ++j)
        {   
            if(real_heavy[i] == heavy_esti[j]){
                estimate_right += 1;
                break;
            }
        }
    }
    double precision =  (double)estimate_right / (double)heavy_esti.size();
    double recall = (double)estimate_right / (double)real_heavy.size();
    double f1 = (2 * precision * recall) / (precision + recall);
    HOW_LOG(L_INFO, "[Result] BeauCoup %d B, Estimate precision %.2f, recall %.2f, f1 %.2f", TOTAL_MEMORY, precision, recall, f1);
    CSVer csver("./results/heavyhitter/beaucoup_1d.csv");
    csver.write(400, 0, 0, precision, recall, f1);
    delete bc;
}

// import sys

// if len(sys.argv) < 4:
//     exit()
// m = int(sys.argv[1])
// n = int(sys.argv[2])
// p = float(sys.argv[3])
// target = 0
// var = 0
// for i in range(n):
//     P = p * (m - i)
//     target += 1/P
//     var += (1-P)/(P**2)
// std_var = pow(var, 0.5)
// RE = std_var / target
// print("M=%d, N=%d, P=%f, Target=%.2f, Var=%.2f, RE=%.2f" %(m, n, p, target, std_var, RE))

// m n p
// M=32, N=28, P=0.015625, Target=126.41, Var=25.58, RE=0.20
// M=32, N=32, P=0.031250, Target=129.87, Var=39.03, RE=0.30