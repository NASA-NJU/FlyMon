#include "DataTrace.h"
#include "CMSketch.h"
#include "HowLog/HowLog.h"
#include <unordered_map>
#include <string>
#include "Csver.h"
using namespace std;

#define TOT_MEM_IN_BYTES 1024000

int main(){
    LOG_LEVEL = L_INFO;
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    trace.LoadFromFile("/home/hzheng/workSpace/SketchLab/data/WIDE/fifteen1.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
    CSVer csver_fs("outputs/original_cmsketch_flowsize.csv");
    // CSVer csver_hv("");

    HOW_LOG(L_DEBUG, "Test cm_sketch, memory allocated : %d B, flow_key = %d", TOT_MEM_IN_BYTES, 8);  
    CM_Sketch cm_sketch(3, 8, TOT_MEM_IN_BYTES);

	unordered_map<string, int> Real_Freq;
    // int mid_size = trace.size() / 2;
    int count = 0;
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        count++;
        cm_sketch.insert((*it)->getFlowKey_IPPair());
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
		Real_Freq[str]++;
    }
    double temp_relation_error_sum = 0;
    int key_num = Real_Freq.size();
    for (auto item : Real_Freq){
        string key = item.first;
 		int estimate = cm_sketch.query((uint8_t*)key.c_str());
		double relative_error = abs(item.second - estimate) / (double)item.second;
		temp_relation_error_sum += relative_error;       
    }
    csver_fs.write(TOT_MEM_IN_BYTES/1024, Real_Freq.size(), temp_relation_error_sum/Real_Freq.size());
    HOW_LOG(L_DEBUG, "Total %d packets, %d flows, ARE = %f", trace.size(), 
                     Real_Freq.size(), 
                     temp_relation_error_sum/Real_Freq.size());
}