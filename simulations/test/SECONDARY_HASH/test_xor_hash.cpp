#include "DataTrace.h"
#include "CMSketch.h"
#include "HowLog/HowLog.h"
#include <unordered_map>
#include <string>
using namespace std;

#define TOT_MEM_IN_BYTES 2048576

int main(){
    LOG_LEVEL = L_INFO;
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    trace.LoadFromFile("../data/WIDE/ten_sec_1.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
 
    CM_Sketch cm_sketch1(3, 8, TOT_MEM_IN_BYTES);
    CM_Sketch cm_sketch2(3, 4, TOT_MEM_IN_BYTES);
    CM_Sketch cm_sketch3(3, 4, TOT_MEM_IN_BYTES);

    random_device rd;
    BOBHash32* hash_src_ip;
    BOBHash32* hash_dst_ip;
    hash_src_ip = new BOBHash32(uint32_t(rd() % MAX_PRIME32));
    hash_dst_ip = new BOBHash32(uint32_t(rd() % MAX_PRIME32));

	unordered_map<string, int> Real_Freq;
    unordered_map<string, uint32_t> Real_key2;
    unordered_map<string, uint32_t> Real_key3;
    // int mid_size = trace.size() / 2;
    int mid_size = trace.size();
    int count = 0;
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        count++;
        string key((const char*)((*it)->getFlowKey_IPPair()), 8);
        cm_sketch1.insert((uint8_t*)key.c_str());
        
        // uint32_t hash = hash_src + hash_port;
        //uint32_t hash_dst = hash_src_ip->run((char*)(*it)->getDstBytes(), 4) & 0x0000ffff;
        //uint32_t consolidated_hash = hash_src + hash_dst;
        uint32_t uint_src = (*it)->getSrcIpAddr().getAddrVal();
        uint32_t uint_dst = (*it)->getDstIpAddr().getAddrVal();
        uint32_t xor_key = uint_src ^ uint_dst;
        cm_sketch2.insert((uint8_t*)(&xor_key));
		

        uint32_t hash_src = hash_src_ip->run(key.c_str(), 4);
        uint32_t hash_dst = hash_dst_ip->run(key.c_str()+4, 4);
        uint32_t hash_xor = hash_src ^ hash_dst;
        cm_sketch3.insert((uint8_t*)(&hash_xor));

        Real_Freq[key]++;
        Real_key2[key] = xor_key;
        Real_key3[key] = hash_xor;
    }
    double temp_relation_error_sum1 = 0;
    double temp_relation_error_sum2 = 0;
    double temp_relation_error_sum3 = 0;
    int key_num = Real_Freq.size();
    for (auto item : Real_Freq){
        string key = item.first;
        uint32_t key2 = Real_key2[key];
        uint32_t key3 = Real_key3[key];
 		int estimate1 = cm_sketch1.query((uint8_t*)key.c_str());
        int estimate2 = cm_sketch2.query((uint8_t*)(&key2));
        int estimate3 = cm_sketch3.query((uint8_t*)(&key3));
		double relative_error1 = abs(item.second - estimate1) / (double)item.second;
        double relative_error2 = abs(item.second - estimate2) / (double)item.second;
        double relative_error3 = abs(item.second - estimate3) / (double)item.second;
		temp_relation_error_sum1 += relative_error1;          
        temp_relation_error_sum2 += relative_error2; 
        temp_relation_error_sum3 += relative_error3; 
    }
    HOW_LOG(L_INFO, "Total %d packets, %d flows, ARE1 = %.2f, ARE2 = %.2f, ARE3 = %.2f", trace.size(), 
                     Real_Freq.size(), 
                     temp_relation_error_sum1/Real_Freq.size(), temp_relation_error_sum2/Real_Freq.size(), temp_relation_error_sum3/Real_Freq.size());
}