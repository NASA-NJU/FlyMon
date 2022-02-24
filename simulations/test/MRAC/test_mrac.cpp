#include "DataTrace.h"
#include "MRAC.h"
#include "HowLog/HowLog.h"
#include <unordered_map>
#include <fstream>
#include <string>
using namespace std;

#define TOT_MEM_IN_BYTES (1.0 * 1024 * 1024)
#define OUT_FILE "flow_distribution_half_1.0.txt"

int main(){
    LOG_LEVEL = L_INFO;
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/ten_sec_1.dat");
    // trace.LoadFromFile("../data/WIDE/thirty_sec_0.dat");
    // trace.LoadFromFile("../data/WIDE/sixty_sec_0.dat");
    trace.LoadFromFile("../data/WIDE/fifteen1.dat");
    MRAC *mrac = new MRAC(TOT_MEM_IN_BYTES, 10);
	unordered_map<string, int> Real_Freq;
    for (auto it = trace.begin(); it!= trace.end(); ++it){
        uint8_t random_number = rand() % 256;
        char bit = ((random_number & 0x01) == 0x01)? '1' : '0';
        if(bit == '0'){
            mrac->insert((*it)->getFlowKey_IPPair(), 8);
        }
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
		Real_Freq[str]++;
    }
    vector<double> distribution;
    mrac->get_distribution(distribution, 2);
    fstream file;
    //here we are going to open the file in append mode (ios::app) or printing mode (ios::out) both
    file.open(OUT_FILE, ios::out);
    for(int i=0; i<distribution.size(); ++i){
        file<<distribution[i];
        if(i != distribution.size() -1){
            file<<" ";
        }
    }
    int real = Real_Freq.size();
    int estimate = 0;
    for(auto& item : distribution){
        estimate += item;
    }
    double RE = abs(real - estimate) / (double)real;
    HOW_LOG(L_INFO, "Write to file %s, size %d, estimate %d, real %d, RE %.2f", OUT_FILE, distribution.size(), estimate, real, RE);
    //closing the file
    file.close();
    delete mrac;
}