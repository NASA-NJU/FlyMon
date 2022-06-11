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

const uint32_t TOTAL_MEMORY = 100 * 1024;
const uint32_t Threshold = 0;
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
    BeauCoup<256>* bc = new BeauCoup<256>(TOTAL_MEMORY);
    
    // bc->register_attr_table(FIELD_TSTAMP);
    bc->register_attr_table(FIELD_IPPAIR);
    // int qid = bc->register_query(FIELD_IPPAIR, FIELD_TSTAMP);  // heavy hitter
    int qid = bc->register_query(FIELD_CONST, FIELD_IPPAIR);  // cardinality
    // uint32_t coupon_num = 32;
    // M=32, N=32, P=0.031250, Target=129.87, Var=39.03, RE=0.30
    // M=32, N=32, P= 1/64, Target=259.87, Var=39.03, RE=0.30
    // M=4, N=4, P=0.250000, Target=8.33, Var=3.80, RE=0.46
    uint32_t coupon_num = 254; // 32  19  131072 ===> 115128;
    for(uint32_t i=0; i<coupon_num; ++i){
        bitset<12> bits(i);
        string coins = bits.to_string() + "*";
        bc->register_query_coupon(qid, coins, i);
    }
	unordered_map<string, uint32_t> ground_truth;
    vector<string> heavy_esti;
    CSVer csver("./results/cardinality/beaucoup.csv");
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        ground_truth[str]++;
        int re = bc->apply(*it);
        if(re == 1){
            double real_size = ground_truth.size();
            double estimate_size = 20000;
            double re = abs(real_size- estimate_size) / real_size;
            // csver.write(256/8, 256, coupon_num, 12, 20000, real_size, re);
            csver.write(256/8, re);
            return 0;
        }
    }
    csver.write("Failed");
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