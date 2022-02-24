#ifndef _D_LEFT_STOP_H_
#define _D_LEFT_STOP_H_

#include "StreamAlgorithm.h"
#include "BOBHash/BOBHash32.h"
#include <vector>
#include <map>

using namespace std;

class DLS_Table : public StreamAlgorithm{
public:
    DLS_Table(int d, int l, int key_len, int memLimit); //Bytes
    virtual int insert(const uint8_t * key);
    virtual int query(const uint8_t * key);
    virtual void get_heavy_hitters(int threshold, vector<pair<string, int>> & results) {}; // Not Support
private:
    int _d;
    int _l;
    vector<int> _index;
    vector<vector<pair<string, int>>> _items;
};


#endif