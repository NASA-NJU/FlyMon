#include <stdio.h>
#include <stdlib.h>
#include <unordered_map>
#include <vector>

#include "CMHeap.h"
#include "DataTrace.h"
#include "HowLog/HowLog.h"
using namespace std;

#define START_FILE_NO 1
#define END_FILE_NO 10


int main()
{
	DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
    int packet_count = trace.size();
    int threashold = packet_count * 0.00001;

	LOG_LEVEL = L_INFO;

	const int HEAP_CAPACITY  = (150 * 1024 / 64);
	CMHeap<4, HEAP_CAPACITY> *cmheap = NULL;


	unordered_map<string, int> Real_Freq;
	cmheap = new CMHeap<4, HEAP_CAPACITY>(450 * 1024);  

	int packet_cnt = (int)trace.size();
	
	for(auto it = trace.begin();  it != trace.end(); ++it)
	{
		// HOW_LOG::INFO("Add");
		// cmheap->insert((uint8_t*)((*it)->getFlowKey_IPPair()));
		// // HOW_LOG::INFO("Done");
		// string str((const char*)((*it)->getFlowKey_IPPair()), 8);
		cmheap->insert((uint8_t*)(*it)->getSrcBytes());
        string str((const char*)((*it)->getSrcBytes()), 4);

		Real_Freq[str]++;
	}
	HOW_LOG(L_INFO, "Done Done");

	double temp_relation_error_sum = 0;
	for(auto item : Real_Freq){
		string flow_key = item.first;
		int estimate = cmheap->query((uint8_t*)flow_key.c_str());
		double relative_error = abs(item.second - estimate) / (double)item.second;
		temp_relation_error_sum += relative_error;
		// HOW_LOG(L_DEBUG, "Real %d, Estimate %d, Relative Error = %f.", item.second, estimate, relative_error);
	}

	HOW_LOG(L_INFO, "Total %d packets, Average Relative Error = %f , Different flow num = %d.",  
	                 packet_cnt, temp_relation_error_sum/Real_Freq.size(), Real_Freq.size());


    vector< pair<string, int> > real_heavy_hitters;
    for (auto item : Real_Freq){
        if (item.second >= threashold)
            real_heavy_hitters.push_back(make_pair(item.first, item.second));
    }

    vector< pair<string, uint32_t> > est_heavy_hitters;
    cmheap->get_heavy_hitters(threashold, est_heavy_hitters);
    int estimate_right = 0;
    // HOW_LOG(L_DEBUG, "estimate heavy hitters: <srcIP, count>, threshold=%d", threashold); 
    for(int i = 0; i < (int)est_heavy_hitters.size(); ++i)
    {
        string srcIP = est_heavy_hitters[i].first;
        for(int j = 0; j < (int)real_heavy_hitters.size(); ++j)
        {
            if(real_heavy_hitters[j].first == srcIP){
                estimate_right += 1;
                break;
            }
        }
    }
    HOW_LOG(L_DEBUG, "Total %d heavyhitter, Error Rate = %.2f", (int)real_heavy_hitters.size(), (double)abs(estimate_right - (int)real_heavy_hitters.size()) /(int)real_heavy_hitters.size() ); 

	delete cmheap;
	Real_Freq.clear();
}	


// 1189 heavyhitter, Error Rate = 0.00

// Total 1514 heavyhitter, Error Rate = 0.00