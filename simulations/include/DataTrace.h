#ifndef _DATA_TRACE_H_
#define _DATA_TRACE_H_

#include <vector>
#include <string>
#include<iterator>
#include <memory>

#include "TracePacket.h"

using namespace std;


template<class T>
class TraceIterator;

class DataTrace{
public:
    typedef vector<TracePacket*>::iterator iterator;
    DataTrace();
    ~DataTrace();
    void LoadFromFile(const string &path);
    iterator begin();
    iterator end();
    int size() const;
private:
    vector<TracePacket*> _traces;
    int _size;
};


# endif