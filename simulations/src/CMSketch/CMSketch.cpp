#include "CMSketch.h"
#include "HowLog/HowLog.h"


#define MASK1 0xfffff800
#define MASK2 0x000001ff
// vector<vector<int>> cm_sketch;
// vector<BOBHash32 *> hash_funcs;
CM_Sketch::CM_Sketch(int d, int key_len, int memLimit) 
    : StreamAlgorithm(key_len, memLimit), _d(d), _w(memLimit/ d / 2), // 16bit is enough
      _cm_sketch(d, vector<int>(_w,0)), _hash_funcs(_w, nullptr), _secondary_hash_funcs(_w, nullptr)
{
    HOW_LOG(L_DEBUG, "Initalize the cm-sketch, d=%d, w=%d", _d, _w);
    // Initialize
    random_device rd;
    for (int i = 0; i < d; i++) {
        _hash_funcs[i] = new BOBHash32(uint32_t(rd() % MAX_PRIME32));
        _secondary_hash_funcs[i] = new BOBHash32(uint32_t(rd() % MAX_PRIME32));
    }
}
CM_Sketch::CM_Sketch(const CM_Sketch & cms) 
 : StreamAlgorithm(cms._key_len, cms._memLimit)
{
    HOW_LOG(L_DEBUG, "Copy Sketch...");
    _d = cms._d;
    _w = cms._w;
    _cm_sketch.resize(_d);
    _hash_funcs.resize(_d);
    _secondary_hash_funcs.resize(_d);
    for(int i=0; i<_d; ++i){
        _cm_sketch[i] = cms._cm_sketch[i];
        _hash_funcs[i] = cms._hash_funcs[i];
    }
}

CM_Sketch& CM_Sketch::operator=(const CM_Sketch & cms){
    _d = cms._d;
    _w = cms._w;
    _cm_sketch.resize(_d);
    _hash_funcs.resize(_d);
    for(int i=0; i<_d; ++i){
        _cm_sketch[i] = cms._cm_sketch[i];
        _hash_funcs[i] = cms._hash_funcs[i];
    }
    _key_len = cms._key_len;
    _memLimit = cms._memLimit;
}

int CM_Sketch::insert(const uint8_t * key) {
    int ans = 0x1f1f1f1f;
    for (int i = 0; i < _d; ++i) {
        int idx = _hash_funcs[i]->run((char *)key, _key_len) % _w;
        _cm_sketch[i][idx] += 1;
        int val = _cm_sketch[i][idx];
        ans = std::min(val, ans);
    }
    return ans;
}

int CM_Sketch::insert_src_port(const uint8_t * key){
    int ans = 0x1f1f1f1f;
    for (int i = 0; i < _d; ++i) {
        uint32_t hash_src = _hash_funcs[i]->run((char*)key, 4) & MASK1;
        uint32_t hash_port = _secondary_hash_funcs[i]->run((char*)key+4, 2) & MASK2;
        uint32_t idx = (hash_src + hash_port) % _w;
        _cm_sketch[i][idx] += 1;
        int val = _cm_sketch[i][idx];
        ans = std::min(val, ans);
    }
    return ans;
}

void CM_Sketch::reset(){
    for (int i = 0; i < _d; ++i) {
        for(int j=0; j<_w; ++j){
            _cm_sketch[i][j] = 0;
        }
    }
}

int CM_Sketch::query(const uint8_t * key){
    int ans = 0x1f1f1f1f;
    for (int i = 0; i < _d; ++i) {
        int idx = _hash_funcs[i]->run((char *)key, _key_len) % _w;
        int val = _cm_sketch[i][idx];
        ans = std::min(val, ans);
    }
    return ans;
}

int CM_Sketch::query_src_port(const uint8_t * key){
    int ans = 0x1f1f1f1f;
    for (int i = 0; i < _d; ++i) {
        uint32_t hash_src = _hash_funcs[i]->run((char*)key, 4) & MASK1;
        uint32_t hash_port = _secondary_hash_funcs[i]->run((char*)key+4, 2) & MASK2;
        uint32_t idx = (hash_src + hash_port) % _w;
        int val = _cm_sketch[i][idx];
        ans = std::min(val, ans);
    }
    return ans;
}