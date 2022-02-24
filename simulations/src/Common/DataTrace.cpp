#include "HowLog/HowLog.h"
#include "DataTrace.h"
#include <stdio.h>

DataTrace::DataTrace()
{
    _traces.reserve(100);
}

void DataTrace::LoadFromFile(const string &path){
    FILE *fin = fopen(path.c_str(), "rb");
    if (fin == NULL)
        return;

    char tmp_five_tuple[13];
    _traces.clear();
    while(fread(tmp_five_tuple, 1, 13, fin) == 13)
    {
        _traces.push_back(new TracePacket(tmp_five_tuple));
    }
    fclose(fin);
    HOW_LOG(L_INFO, "Successfully read in %s, %d packets.", path.c_str(), _traces.size());
}

DataTrace::~DataTrace(){
    for(int i=0; i<_traces.size(); ++i){
        delete _traces[i];
    }
}

DataTrace::iterator DataTrace::begin(){
    return _traces.begin();
}
DataTrace::iterator DataTrace::end(){
    return _traces.end();
}
int DataTrace::size() const{
    return (int)_traces.size();
}