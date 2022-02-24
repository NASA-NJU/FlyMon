
#ifndef _CM_SKETCH_H_
#define _CM_SKETCH_H_

#include "BOBHash/BOBHash32.h"
#include "HowLog/HowLog.h"
#include "CRCHash/CRC.h"
#include <vector>

using namespace std;

struct Block{
    uint8_t pid;
    uint8_t flag;
    uint32_t value;
    Block(){
        pid = -1;
        flag = 0;
        value = 0;
    }
};

struct Stage{
    vector<BOBHash32 *> hash_funcs;
    vector<vector<Block>> regs;
};

class StageFly {
public:
    StageFly(int stage_num, int reg_per_stage, int key_len, int memLimit); //Bytes
    virtual int insert(const uint8_t * key);
    virtual int query(const uint8_t * key);
    void reset();
private:
    // return:
    // 1 done.
    // 0 pass.
    int process_stage(Stage&);
    int packet_cnt;
    vector<Stage> _stages;
};

StageFly::StageFly(int stage_num, int reg_per_stage, int key_len, int memLimit) 
{
    int per_stage_bytes = memLimit / stage_num;
    int per_reg_size = per_stage_bytes / reg_per_stage / 6;
    random_device rd;
    _stages.resize(stage_num);
    for(int i=0; i<stage_num; ++i){
        _stages[i].hash_funcs.resize(reg_per_stage);
        _stages[i].regs.resize(reg_per_stage);
        for(int j=0; j<reg_per_stage; ++j){
            _stages[i].hash_funcs[j] = new BOBHash32(uint32_t(rd() % MAX_PRIME32));
            _stages[i].regs[j].resize(per_reg_size);
        }
    }
    packet_cnt = 0;
    HOW_LOG(L_DEBUG, "Initalize stage-fly with %d stages, each with %dx%d registers...", stage_num, reg_per_stage, per_reg_size);
}

int StageFly::process_stage(Stage& stage){
    
    for( int i=0; i<)
    int reg0_index =_hash_funcs[i]->run((char *)key, _key_len) % _w;
}

int StageFly::insert(const uint8_t * key){
    HOW_LOG(L_DEBUG, "Incomming packet %d.", packet_cnt++);
    int stage_index = 0;
    for(auto& stage : _stages){
        HOW_LOG(L_DEBUG, "-- Processing stage %d...", stage_index++);
        process_stage(stage);
    }
}

#endif