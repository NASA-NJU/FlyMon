#include "UnivMon.h"
#include "DataTrace.h"
#include "HowLog/HowLog.h"
#include <unordered_map>
#include <string>
#include "TracePacket.h"
#include "Csver.h"




double get_real_entropy(unordered_map<string, int>& flow_map){
    unordered_map<int, int> size_map;
    double m = 0;
    for(auto& flow : flow_map){
        m += flow.second;
    }
    double entropy = 0;
    for(auto& flow : flow_map){
        double p = flow.second/m;
        entropy += p*log2(p);
    }
    return -1*entropy;
}


#define TOT_MEM_IN_BYTES   400 * 1024

int main(){

    LOG_LEVEL = L_DEBUG;
    DataTrace trace;
    trace.LoadFromFile(".//.//data/fifteen1.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/fifteen1.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
    int threashold = 1024;

    const int key_len = 8;
// template<uint8_t key_len, uint64_t mem_in_bytes, uint8_t level = 14>
	UnivMon<key_len, 14> *umsketch = new UnivMon<key_len, 14>(TOT_MEM_IN_BYTES);

    HOW_LOG(L_DEBUG, "Test umsketch_sketch_sw, memory allocated : %d B, flow_key = %d", TOT_MEM_IN_BYTES, key_len);  

	unordered_map<string, int> Real_Freq;
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        string str;
        if (key_len == 4){
            umsketch->insert((*it)->getSrcBytes());
            str = string((const char*)((*it)->getSrcBytes()), 4);
        }else{
            umsketch->insert((*it)->getFlowKey_IPPair());
            str = string((const char*)((*it)->getFlowKey_IPPair()), 8);         
        }
		Real_Freq[str]++;
    }

    vector< pair<string, int> > real_heavy_hitters;
    for (auto item : Real_Freq){
        if (item.second >= threashold)
            real_heavy_hitters.push_back(make_pair(item.first, item.second));
    }
    int real_cardinality = Real_Freq.size();
    int real_entropy= get_real_entropy(Real_Freq);


    vector< pair<string, int> > est_heavy_hitters;
    umsketch->get_heavy_hitters(threashold, est_heavy_hitters);
    int estimate_right = 0;
    for(int i = 0; i < (int)est_heavy_hitters.size(); ++i)
    {
        string key = est_heavy_hitters[i].first;
        // HOW_LOG(L_DEBUG, "<%s, %d>", srcIP.c_str(), est_heavy_hitters[i].second); 
        for(int j = 0; j < (int)real_heavy_hitters.size(); ++j)
        {
            if(real_heavy_hitters[j].first == key){
                estimate_right += 1;
                break;
            }
        }
    }
    double precision =  (double)estimate_right / (double)est_heavy_hitters.size();
    double recall = (double)estimate_right / (double)real_heavy_hitters.size();
    double f1 = (2 * precision * recall) / (precision + recall);
    HOW_LOG(L_DEBUG, "Real Heavyhitter = %d, PR = %.2f, RR = %.2f, F1 Score = %.2f", (int)real_heavy_hitters.size(), precision, recall, f1); 
    // CSVer csver("./results/heavyhitter/univmon.csv");
    // csver.write(400, 0,0, real_heavy_hitters.size(),precision, recall, f1);

    // int es_cardinality = umsketch->get_cardinality();
    // double re = abs(es_cardinality - real_cardinality) / (double)real_cardinality;
    // HOW_LOG(L_DEBUG, "Real Cardinality = %d, UNV Cardinality = %d, RE = %.2f", real_cardinality, es_cardinality, re); 
    // CSVer csver("./results/heavyhitter/univmon.csv");
    // csver.write(0.0, TOT_MEM_IN_BYTES, re);

    int es_entropy = umsketch->get_entropy();
    double re = abs(real_entropy - es_entropy) / (double)real_entropy;
    HOW_LOG(L_DEBUG, "Real Entropy = %d, UNV Entropy = %d, RE = %.2f", real_entropy, es_entropy, re); 
    CSVer csver("./results/heavyhitter/univmon.csv");
    csver.write(400, re);
}