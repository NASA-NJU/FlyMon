#ifndef _STREAM_ALG_H_
#define _STREAM_ALG_H_

#include "TracePacket.h"


class StreamAlgorithm {
public:
    StreamAlgorithm(int key_len, int memLimit) 
        : _memLimit(memLimit), _key_len(key_len) {}
    virtual int insert(const uint8_t * key) = 0;
    virtual int query(const uint8_t * key) = 0;
    virtual void get_heavy_hitters(int threshold, vector<pair<string, int>> & results) = 0;
    virtual double get_cardinality() = 0;
    virtual double get_entropy() = 0;
protected:
    int _memLimit;  // KB
    int _key_len;
};
#endif