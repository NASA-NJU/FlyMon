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

const uint32_t TOTAL_MEMORY = 1000 * 1024;
const uint32_t DDoS_Threshold = 256;
int main(){

    LOG_LEVEL = L_DEBUG;
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/test.dat");
    // trace.LoadFromFile("/home/hzheng/workSpace/SketchLab/data/WIDE/fifteen1.dat");
    trace.LoadFromFile("/home/hzheng/workSpace/SketchLab/data/WIDE/sixty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/fifteen1.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
    BeauCoup<32, 3>* bc = new BeauCoup<32, 3>(TOTAL_MEMORY);
    
    bc->register_attr_table(FIELD_IPSRC);
    int qid = bc->register_query(FIELD_IPDST, FIELD_IPSRC);  // key, attr
    uint32_t coupon_num = 32;
    // M=32, N=32, P=0.031250, Target=129.87, Var=39.03, RE=0.30
    // M=32, N=32, P= 1/64, Target=259.87, Var=39.03, RE=0.30
    // M=4, N=4, P=0.250000, Target=8.33, Var=3.80, RE=0.46
    for(uint32_t i=0; i<coupon_num; ++i){
        bitset<6> bits(i);
        string coins = bits.to_string() + "*";
        bc->register_query_coupon(qid, coins, i);
    }
	unordered_map<string, vector<string>> ground_truth;
    vector<string> esti_ddos;
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        string ipdst((const char*)((*it)->getDstBytes()), 4);
        string ipsrc((const char*)((*it)->getSrcBytes()), 4);
        vector<string>& ip_list = ground_truth[ipdst];
        if(find(ip_list.begin(), ip_list.end(), ipsrc) == ip_list.end())
                ip_list.push_back(ipsrc);
        int re = bc->apply(*it);
        if(re == 1){
            // exceed the threshold.
            string key = TracePacket::bytes_to_ip_str((uint8_t*)ipdst.c_str());
            if(find(esti_ddos.begin(), esti_ddos.end(), key) == esti_ddos.end())
                esti_ddos.push_back(key);
        }
    }
    vector<string> real_ddos;
    for(auto& ipdst : ground_truth){
        uint32_t src_num = ipdst.second.size();
        if(src_num >= DDoS_Threshold) real_ddos.push_back(TracePacket::bytes_to_ip_str((uint8_t*)ipdst.first.c_str()));
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
    for(uint32_t i = 0; i < real_ddos.size(); ++i)
    {
        for(uint32_t j = 0; j < esti_ddos.size(); ++j)
        {   
            if(real_ddos[i] == esti_ddos[j]){
                estimate_right += 1;
                break;
            }
        }
    }
    double precision =  (double)estimate_right / (double)esti_ddos.size();
    double recall = (double)estimate_right / (double)real_ddos.size();
    double f1 = (2 * precision * recall) / (precision + recall);
    HOW_LOG(L_INFO, "[Result] BeauCoup %d B, Estimate precision %.2f, recall %.2f, f1 %.2f", TOTAL_MEMORY, precision, recall, f1);
    CSVer csver("outputs_30/ddosvictims_new/ddosvictim_beaucoup_3d.csv");
    csver.write(1000, 0, 0, precision, recall, f1);
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