
#ifndef _CM_SKETCH_H_
#define _CM_SKETCH_H_

#include "StreamAlgorithm.h"
#include "BOBHash/BOBHash32.h"
#include "CRCHash/CRC.h"
#include <vector>

using namespace std;

class CM_Sketch : public StreamAlgorithm{
public:
    CM_Sketch(int d, int key_len, int memLimit); //Bytes
    CM_Sketch(const CM_Sketch &);
    virtual int insert(const uint8_t * key);
    virtual int query(const uint8_t * key);
    virtual void get_heavy_hitters(int threshold, vector<pair<string, int>> & results) {}; // Not Support
    virtual double get_cardinality() { return 0;}; // Not Support
    virtual double get_entropy() {return 0;};
    virtual int insert_src_port(const uint8_t * key);
    virtual int query_src_port(const uint8_t * key);
    void reset();
    
    CM_Sketch& operator=(const CM_Sketch &);
private:
    int _d;
    int _w;
    vector<vector<int>> _cm_sketch;
    vector<BOBHash32 *> _hash_funcs;
    vector<BOBHash32 *> _secondary_hash_funcs;
};


#endif