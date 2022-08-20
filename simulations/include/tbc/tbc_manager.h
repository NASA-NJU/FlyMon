#ifndef _TBC_MANAGER_H_
#define _TBC_MANAGER_H_

#include "tbc/tbc.h"
#include "tbc/tbc_common.h"
#include "HowLog/HowLog.h"
#include "tbc/tbc_resource_mgr.h"
#include <bitset>
#include <map>
#include <algorithm>

struct BLOCK_INFO{
    // {i, j, task_memory_type, static_cast<uint32_t>(re1)}
    int tbc_id;
    int block_id;
    int block_type;
    int block_offset;
};

struct TASK_INFO{
    int task_id;
    string coins;
    vector<RandomFTupleMatch*> filters;
    vector<BLOCK_INFO> _blocks;  //tbc, block, sub_type, sub_block_id.
    ~TASK_INFO(){
        for( int i=0; i<filters.size(); ++i){
            delete filters[i];
        }
        filters.clear();
    }
};

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
class TBC_Manager
{
private:
    int _TASK_ID;
    TBC* _tbc[TBC_NUM];
    TBC_Resource_Manager* _status[TBC_NUM]; 
    map<int, TASK_INFO> _tasks; // task_id, info.
    map<string, vector<int>> _coins_tasks; // coins, [task_id].
    map<int, unordered_map<string, int>> _tasks_gt; // task_id, packets statistics.
    vector<vector<vector<uint16_t>>> _mdata;
private:
	TBC_Manager() {
        srand((int)time(0));
        _mdata.resize(TBC_NUM);
        for(int i =0; i < TBC_NUM; ++i){
            _tbc[i]= new TBC(BLOCK_NUM, BLOCK_SIZE);
            _status[i]= new TBC_Resource_Manager(BLOCK_NUM, get_level_num());
            _mdata[i].resize(BLOCK_NUM, vector<uint16_t>(0,0));
        }
        _TASK_ID = 0;
        HOW_LOG(L_INFO, "Setup TBC Num %d, Block Num %d, Block Size %d, SubBlock Num %d.", TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM);
    }
	~TBC_Manager() {
        for(int i=0; i<TBC_NUM; ++i)
        {
            delete _tbc[i];
            delete _status[i];
        }

    }
	TBC_Manager(const TBC_Manager&){}
	TBC_Manager& operator=(const TBC_Manager&){}
    void update(bool verbose = false);
    void read(int tbc_id, int block_id, int memory_type, int sub_block_id, vector<uint16_t>& block);
    uint32_t temp_key(int tbc_id, int block_id){ return tbc_id* 100 + block_id; }
    string getSubBlockTypeStr(int block_type);
    int getSubBlockSize(int block_type);
    int getSubBlockType(int sub_block_num);
    int getSubBlockLevel(int sub_block_type);
    int register_tasks(int block_num, int block_size, int coin_level=COINS_DEAULT);
    // allocate block by gragh
    // mode 0: accurate.
    // mode 1: efficient.
    int register_tasks_v2(const vector<int>& gragh, int mode=MEM_MODE_ACCURATE, int coin_level=COINS_DEAULT);  

    int get_level_num()const{
        switch(SUB_BLOCK_NUM){
            case 1: return 1;
            case 2: return 2;
            case 4: return 3;
            case 8: return 4;
            case 16: return 5;
            case 32: return 6;
            case 64: return 7;
            case 128: return 8;
        }
    }
    // double coins2double(const string& coins);

public:
	static TBC_Manager& getDataplane() 
    {
		static TBC_Manager instance;
		return instance;
	}

    void reset();

    // return taks_id.
    int allocate_cmsketch(int d, int w, FTupleMatch* filter, int key_id, int val_id, int coin_level=COINS_DEAULT);
    // return taks_id.
    int allocate_cusketch(int d, int w, FTupleMatch* filter, int key_id, int val_id);

    int allocate_max_interval(int w, FTupleMatch* filter, int key_id);

    // 1024 is the threshold.
    int allocate_beaucoup_1024(int k, int w, FTupleMatch* filter, int key_id, int val_id, int param_id);
    int allocate_beaucoup_128(int k, int w, FTupleMatch* filter, int key_id, int val_id, int param_id);
    int allocate_beaucoup_256(int k, int w, FTupleMatch* filter, int key_id, int val_id, int param_id);

    int allocate_bloom_filter(int k, int w, FTupleMatch* filter, int key_id); // k*w = m
    int insert_bloom_filter(int task_id, const uint8_t* key, uint32_t key_len); // k*w = m

    int allocate_bloom_filter_wo_optm(int k, int w, FTupleMatch* filter, int key_id); // k*w = m
    int insert_bloom_filter_wo_optm(int task_id, const uint8_t* key, uint32_t key_len); // k*w = m

    // int allocate_bloom_filter(int k, int w, FTupleMatch* filter, int key_id); // k*w = m
    // int insert_bloom_filter(int task_id, const uint8_t* key, uint32_t key_len); // k*w = m

    // fit in hash share.
    int allocate_hyperloglog_new(int m, FTupleMatch* filter, int key_id, int val_id, int coin_level=COINS_DEAULT);

    int allocate_mrachll(int m, int n, int coin_level, FTupleMatch* filter, int key_id, int val_id);

    int allocate_multi_hll_new(int d, int m, FTupleMatch* filter, int key_id, int val_id, int coin_level=COINS_DEAULT);


    int allocate_range_table(int d, int m, FTupleMatch* filter, int key_id, int val_id, int coin_level=COINS_DEAULT);

    // query result.
    int query(int task_id, map<uint16_t, map<uint16_t, vector<uint16_t>>>& mdata, bool verbose=false); // Coin ID, Values.

    void getTaskStatistics(int task_id, unordered_map<string, int>& statistics){
        statistics = _tasks_gt[task_id];
    }

    int get_address(int task_id, int tbc_id, int block_id, const uint8_t* key, int key_len);
    int get_val_hash(int task_id, int tbc_id, int block_id, const uint8_t* key, int key_len);

    BOBHash32* get_hash_func(int tbc_id){
        return _tbc[tbc_id]->getHashFunc();
    }

    // run tbcs.
    void apply(TracePacket* hdr){
        PipeMeta* meta = new PipeMeta(BLOCK_NUM);
        for(int i=0; i<TBC_NUM; i++){
            string coins = _tbc[i]->apply(hdr, meta);
            // cout <<"返回的coins : "<< coins <<endl;
            for(auto& task_id : _coins_tasks[coins]){
                // cout <<task_id <<" 有这样的coins" << endl;
                _tasks_gt[task_id][string((const char*)hdr->getFlowKey_IPPair(), 8)] += 1;
            }
        }
        delete meta; // remeber to release memory.
    }
    int bloom_apply(TracePacket* hdr){
        PipeMeta* meta = new PipeMeta(BLOCK_NUM);
        for(int i=0; i<TBC_NUM; i++){
            string coins = _tbc[i]->apply(hdr, meta);
            for(auto& task_id : _coins_tasks[coins]){
                _tasks_gt[task_id][string((const char*)hdr->getFlowKey_IPPair(), 8)] += 1;
            }
        }
        int count = 0;
        for(auto& result : meta->results){
            if(result > 0) count += 1;
        }
        delete meta; // remeber to release memory.
        if(count == BLOCK_NUM) 
            return 1;
        else
            return 0;
    }

    int beaucoup_apply(TracePacket* hdr) {
        PipeMeta* meta = new PipeMeta(BLOCK_NUM);
        for(int i=0; i<TBC_NUM; i++){
            string coins = _tbc[i]->apply(hdr, meta);
            for(auto& task_id : _coins_tasks[coins]){
                _tasks_gt[task_id][string((const char*)hdr->getFlowKey_IPPair(), 8)] += 1;
            }
        }
        int count = 0;
        for(auto& result : meta->results){
            if(result == 0xffff) count += 1;
        }
        delete meta; // remeber to release memory.
        if(count == BLOCK_NUM) 
            return 1;
        else
            return 0;
    }
};




template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_cmsketch(int d, int w, FTupleMatch* filter, int key_id, int val_id, int coin_level){
    int task_id = register_tasks(d,w, coin_level);
    if(task_id < 0){
        return -1;
    }
    auto& task = _tasks[task_id];
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    // // Add rules.
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  // 需要一个block id 参数
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {1});         // 需要一个const val 参数
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_CONST], {0x1f1f}); // 需要一个const val 参数
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_NO_ACTION]);
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_CMP_ADD], {block_id});     // 需要一个block id 参数
        // HOW_LOG(L_INFO, "Allocate tbc%d, block %d and sub_block %d (type %s, real block num %d) for task %d with coins %s.", tbc_id, block_id, sub_block_id, getSubBlockTypeStr(memory_type).c_str(), getSubBlockSize(memory_type), task_id, coins.c_str());
        HOW_LOG(L_INFO, "[CM Sketch] Allocate tbc%d, block %d and sub_block %d (type %s, real block num %d) for task %d with coins %s.", 
                         tbc_id, block_id, sub_block_id, getSubBlockTypeStr(memory_type).c_str(), getSubBlockSize(memory_type), task_id, task.coins.c_str());
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_cusketch(int d, int w, FTupleMatch* filter, int key_id, int val_id){
    int task_id = register_tasks(d,w);
    if(task_id < 0){
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    int count = 0;
    // // Add rules.
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  // 需要一个block id 参数
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {1});         // 需要一个const val 参数
        if(count == 0){
            _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_CONST], {0x1f1f}); // 需要一个const val 参数
        }else{
            _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_RESULT], {}); 
        }
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_NO_ACTION]);
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_CMP_ADD], {block_id});     // 需要一个block id 参数
        HOW_LOG(L_INFO, "Allocate tbc%d, block %d and sub_block %d (type %s, real block num %d) for task %d with coins %s.", tbc_id, block_id, sub_block_id, getSubBlockTypeStr(memory_type).c_str(), getSubBlockSize(memory_type), task_id, task.coins.c_str());
        count += 1;
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_max_interval(int w, FTupleMatch* filter, int key_id){
    vector<int> resource_graph(3, w);
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, 0);
    if(task_id < 0) {
        HOW_LOG(L_ERROR, "Allocate Failed!");
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    int count = 0;
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        if(count == 0){
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_VAL_IPPAIR_HASH], {block_id});
            _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_IPPAIR], {block_id});
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
            for(uint16_t i=0; i<16; ++i){
                bitset<4> match(i);
                RandomFTupleMatch* temp_filter = new RandomFTupleMatch(task.coins, filter, "param", match.to_string()+"*");
                _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, temp_filter, _tbc[tbc_id]->Actions[ACTION_VAL_ONE_HOT], {(uint16_t)(1 << i)});
                task.filters.push_back(temp_filter);
            }
            _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_OR], {block_id});     // 需要一个block id 参数
        }
        else if(count == 1){
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_VAL_TIMESTAMP], {});
            _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_RESULT], {});
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_NO_ACTION]);
            _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_SET], {block_id});   
        }else{
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_VAL_TIMESTAMP], {});
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_SUB_RESULT]);
            _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_MAX], {block_id});     // 需要一个block id 参数
        }
        HOW_LOG(L_INFO, "Allocate tbc%d, block %d and sub_block %d (type %s, real block num %d) for task %d with coins %s.", 
                    tbc_id, block_id, sub_block_id, getSubBlockTypeStr(memory_type).c_str(), getSubBlockSize(memory_type), task_id, task.coins.c_str());
        count += 1;
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_bloom_filter(int k, int w, FTupleMatch* filter, int key_id){
    vector<int> resource_graph(k, w);
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, 0);
    if(task_id < 0) {
        HOW_LOG(L_ERROR, "Allocate Failed!");
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_VAL_IPPAIR_HASH], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_IPPAIR], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        for(uint16_t i=0; i<16; ++i){
            bitset<4> match(i);
            RandomFTupleMatch* temp_filter = new RandomFTupleMatch(task.coins, filter, "param", match.to_string()+"*");
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, temp_filter, _tbc[tbc_id]->Actions[ACTION_VAL_ONE_HOT], {(uint16_t)(1 << i)});
            task.filters.push_back(temp_filter);
        }
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_AND], {block_id});     // 需要一个block id 参数
    }
    return task_id;
}

// Currently just support 16 coupon.
template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_beaucoup_1024(int k, int w, FTupleMatch* filter, int key_id, int val_id, int param_id){
    vector<int> resource_graph(k, w);
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, 0);
    if(task_id < 0) {
        HOW_LOG(L_ERROR, "Allocate Failed!");
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[param_id], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        for(uint16_t i=0; i<16; ++i){
            bitset<8> match(i);
            RandomFTupleMatch* temp_filter = new RandomFTupleMatch(task.coins, filter, "param", match.to_string()+"*");
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, temp_filter, _tbc[tbc_id]->Actions[ACTION_VAL_ONE_HOT], {(uint16_t)(1 << i)});
            task.filters.push_back(temp_filter);
        }
        // must add a defult action if p less than 1/16.
        RandomFTupleMatch* default_filter = new RandomFTupleMatch(task.coins, filter, "param", "*");
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, default_filter, _tbc[tbc_id]->Actions[ACTION_SET_VAL_CONST], {0});
        task.filters.push_back(default_filter);
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_OR], {block_id});     // 需要一个block id 参数
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_beaucoup_128(int k, int w, FTupleMatch* filter, int key_id, int val_id, int param_id){
    vector<int> resource_graph(k, w);
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, 0);
    if(task_id < 0) {
        HOW_LOG(L_ERROR, "Allocate Failed!");
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[param_id], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        for(uint16_t i=0; i<16; ++i){
            bitset<5> match(i);
            RandomFTupleMatch* temp_filter = new RandomFTupleMatch(task.coins, filter, "param", match.to_string()+"*");
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, temp_filter, _tbc[tbc_id]->Actions[ACTION_VAL_ONE_HOT], {(uint16_t)(1 << i)});
            task.filters.push_back(temp_filter);
        }
        RandomFTupleMatch* default_filter = new RandomFTupleMatch(task.coins, filter, "param", "*");
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, default_filter, _tbc[tbc_id]->Actions[ACTION_SET_VAL_CONST], {0});
        task.filters.push_back(default_filter);
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_OR], {block_id});     // 需要一个block id 参数
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_beaucoup_256(int k, int w, FTupleMatch* filter, int key_id, int val_id, int param_id){
    vector<int> resource_graph(k, w);
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, 0);
    if(task_id < 0) {
        HOW_LOG(L_ERROR, "Allocate Failed!");
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[param_id], {block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        for(uint16_t i=0; i<16; ++i){
            bitset<6> match(i);
            RandomFTupleMatch* temp_filter = new RandomFTupleMatch(task.coins, filter, "param", match.to_string()+"*");
            _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, temp_filter, _tbc[tbc_id]->Actions[ACTION_VAL_ONE_HOT], {(uint16_t)(1 << i)});
            task.filters.push_back(temp_filter);
        }
        RandomFTupleMatch* default_filter = new RandomFTupleMatch(task.coins, filter, "param", "*");
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, default_filter, _tbc[tbc_id]->Actions[ACTION_SET_VAL_CONST], {0});
        task.filters.push_back(default_filter);
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_OR], {block_id});     // 需要一个block id 参数
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_bloom_filter_wo_optm(int k, int w, FTupleMatch* filter, int key_id){
    vector<int> resource_graph(k, w);
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, 0);
    if(task_id < 0) {
        HOW_LOG(L_ERROR, "Allocate Failed!");
        return -1;
    }
    auto& task = _tasks[task_id]; 
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_VAL_CONST], {1});
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_CONST], {1});
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_NO_ACTION], {});
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_AND], {block_id});     // 需要一个block id 参数
    }
    return task_id;
}

uint16_t get_onehot(uint16_t val){
    // 历史原因，从低位往高位匹配.
    uint16_t match = val & 0x000f; // 0b0110
    uint16_t match_rev = 0;
    match_rev |= ((match & (1<<0)) << 3); // 0b0000
    match_rev |= ((match & (1<<1)) << 1); // 0b0100
    match_rev |= ((match & (1<<2)) >> 1); // 0b0110
    match_rev |= ((match & (1<<3)) >> 3); // 0b0110
    return 1 << match_rev;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::insert_bloom_filter(int task_id, const uint8_t* key, uint32_t key_len){
    auto& task = _tasks[task_id]; 
    for(auto& block : task._blocks){
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        uint32_t address = get_address(task_id, 0, block_id, key, key_len);
        uint16_t one_hot = get_onehot(get_val_hash(task_id,tbc_id, block_id, key, key_len));
        uint16_t memValue = _tbc[tbc_id]->readMemory(block_id, address);
        _tbc[tbc_id]->writeMemory(block_id, address, memValue | one_hot);
    }
    return 0;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::insert_bloom_filter_wo_optm(int task_id, const uint8_t* key, uint32_t key_len){
    auto& task = _tasks[task_id]; 
    for(auto& block : task._blocks){
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        uint32_t address = get_address(task_id, 0, block_id, key, key_len);
        _tbc[tbc_id]->writeMemory(block_id, address, 1);
    }
    return 0;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_hyperloglog_new(int m, FTupleMatch* filter, int key_id, int val_id, int coin_level){
    int task_id = register_tasks(1, m, coin_level);
    if(task_id < 0){
        return -1;
    }
    auto& task = _tasks[task_id];
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    // // Add rules.
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t memory_type = block.block_type;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  // 需要一个block id 参数
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {block_id});     
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[tbc_id]->Actions[memory_type], {sub_block_id});
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_NO_ACTION], {});
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_MAX], {block_id});     // 需要一个block id 参数
        HOW_LOG(L_INFO, "[Hyperloglog] Allocate tbc%d, block %d and sub_block %d (type %s, real block num %d) for task %d with coins %s.", 
                        tbc_id, block_id, sub_block_id, getSubBlockTypeStr(memory_type).c_str(), getSubBlockSize(memory_type), task_id, task.coins.c_str());
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_multi_hll_new(int d, int sub_num, FTupleMatch* filter, int key_id, int val_id, int coin_level){
    vector<int> resource_graph(d, BLOCK_SIZE); // allocate a whole block.
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, coin_level);
    if(task_id < 0){
        return -1;
    }
    auto& task = _tasks[task_id];
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    uint16_t memory_type = 0;
    if(sub_num == 1)
        memory_type= MEMORY_1; // need to split block by it self.
    else if(sub_num == 2)
        memory_type= MEMORY_2; // need to split block by it self.
    else if(sub_num == 4)
        memory_type= MEMORY_4; // need to split block by it self.
    else if(sub_num == 8)
        memory_type= MEMORY_8; // need to split block by it self.
    else if(sub_num == 16)
        memory_type= MEMORY_16; // need to split block by it self.
    else if(sub_num == 32)
        memory_type= MEMORY_32; // need to split block by it self.
    else if(sub_num == 64)
        memory_type= MEMORY_64; // need to split block by it self.
    else if(sub_num == 128)
        memory_type= MEMORY_128; // need to split block by it self.
    else
    {
        HOW_LOG(L_ERROR, "Unsupported MultiHLL memory type...");
        exit(1);
    }
    // // Add rules.
    for(auto& block : task._blocks){
        uint16_t task_id = task.task_id;
        uint16_t tbc_id = block.tbc_id;
        uint16_t block_id = block.block_id;
        uint16_t sub_block_id = block.block_offset;
        _tbc[tbc_id]->addRule(block_id, TABLE_KEY_INIT, task.filters[0], _tbc[tbc_id]->Actions[key_id], {block_id});  // 需要一个block id 参数
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_INIT, task.filters[0], _tbc[tbc_id]->Actions[val_id], {block_id});    
        _tbc[tbc_id]->addRule(block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_SET_PARAM_IPSRC], {block_id}); // only for ddos detection.
        for(uint16_t i = 0; i<sub_num; ++i){
            bitset<MAX_COIN_NUM> bits(i);
            string bits_str = bits.to_string();
            uint16_t real_coin_num = static_cast<uint16_t>(log2(sub_num));
            string real_bits_str(MAX_COIN_NUM, '*');
            int real_index = real_coin_num -1; 
            for(uint16_t k = MAX_COIN_NUM-1; k >=0; --k){
                if(real_index >= 0)
                { // reverse?
                    real_bits_str[real_index] = bits_str[k];
                    real_index -= 1;
                }else{
                    break;
                }
            }
            // filter has problems.
            RandomFTupleMatch* temp_filter = new RandomFTupleMatch(task.coins, filter, "param", real_bits_str);
            // for intra-task selection.
            _tbc[tbc_id]->addRule(block_id, TABLE_KEY_MAPPING, temp_filter, _tbc[tbc_id]->Actions[memory_type], {i});
            task.filters.push_back(temp_filter);
        }
        _tbc[tbc_id]->addRule(block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[tbc_id]->Actions[ACTION_VAL_NO_ACTION], {});
        _tbc[tbc_id]->addRule(block_id, TABLE_OP_SELECT, task.filters[0], _tbc[tbc_id]->Actions[ACTION_OP_MAX], {block_id});     // 需要一个block id 参数
        HOW_LOG(L_INFO, "[Multi-Hyperloglog] Allocate tbc %d, block %d and sub_block_num %d for task %d with coins %s.", 
                tbc_id, block_id, sub_num, task_id, task.coins.c_str());
    }
    return task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::allocate_mrachll(int m, int n, int coin_level, FTupleMatch* filter, int key_id, int val_id){
    vector<int> resource_graph = {m, n};
    int task_id = register_tasks_v2(resource_graph, MEM_MODE_ACCURATE, coin_level);
    if(task_id < 0){
        return -1;
    }
    auto& task = _tasks[task_id];
    task.filters.push_back(new RandomFTupleMatch(task.coins, filter));
    // cout << task.coins << endl;
    // Add rules to construct hyperloglog.
    auto& block_hll = task._blocks[0];
    uint16_t hll_tbc_id = block_hll.tbc_id;
    uint16_t hll_block_id = block_hll.block_id;
    uint16_t hll_block_type  = block_hll.block_type;
    uint16_t hll_block_offset  = block_hll.block_offset;
    _tbc[hll_tbc_id]->addRule(hll_block_id, TABLE_KEY_INIT, task.filters[0], _tbc[hll_block_id]->Actions[key_id], {hll_block_id});  // 需要一个block id 参数
    _tbc[hll_tbc_id]->addRule(hll_block_id, TABLE_VAL_INIT, task.filters[0], _tbc[hll_block_id]->Actions[val_id], {1});         // 需要一个const val 参数
    _tbc[hll_tbc_id]->addRule(hll_block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[hll_block_id]->Actions[hll_block_type], {hll_block_offset});
    _tbc[hll_tbc_id]->addRule(hll_block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[hll_block_id]->Actions[ACTION_VAL_NO_ACTION], {hll_block_id});
    _tbc[hll_tbc_id]->addRule(hll_block_id, TABLE_OP_SELECT, task.filters[0], _tbc[hll_block_id]->Actions[ACTION_OP_MAX], {hll_block_id});     // 需要一个block id 参
   
    // Add rules to construct mrac.
    auto& block_mrac = task._blocks[1];
    uint16_t mrac_tbc_id = block_mrac.tbc_id;
    uint16_t mrac_block_id = block_mrac.block_id;
    uint16_t mrac_block_type  = block_mrac.block_type;
    uint16_t mrac_block_offset  = block_mrac.block_offset;
    _tbc[mrac_tbc_id]->addRule(mrac_block_id, TABLE_KEY_INIT, task.filters[0], _tbc[mrac_tbc_id]->Actions[key_id], {mrac_block_id});  // 需要一个block id 参数
    _tbc[mrac_tbc_id]->addRule(mrac_block_id, TABLE_VAL_INIT, task.filters[0], _tbc[mrac_tbc_id]->Actions[ACTION_SET_VAL_CONST], {1});         // 需要一个const val 参数
    _tbc[mrac_tbc_id]->addRule(mrac_block_id, TABLE_PARAM_INIT, task.filters[0], _tbc[mrac_tbc_id]->Actions[ACTION_SET_PARAM_CONST], {0x1f1f}); // 需要一个const val 参数
    _tbc[mrac_tbc_id]->addRule(mrac_block_id, TABLE_KEY_MAPPING, task.filters[0], _tbc[mrac_tbc_id]->Actions[mrac_block_type], {mrac_block_offset});
    _tbc[mrac_tbc_id]->addRule(mrac_block_id, TABLE_VAL_PROCESS, task.filters[0], _tbc[mrac_tbc_id]->Actions[ACTION_VAL_NO_ACTION]);
    _tbc[mrac_tbc_id]->addRule(mrac_block_id, TABLE_OP_SELECT, task.filters[0], _tbc[mrac_tbc_id]->Actions[ACTION_OP_CMP_ADD], {mrac_block_id});     // 需要一个block id 参数
    return task_id;
}


template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
void TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::update(bool verbose) {
    for(int i=0; i<TBC_NUM; ++i){
        for(int j=0; j<BLOCK_NUM; ++j){
            _tbc[i]->readBlock(j, _mdata[i][j]);
            if(verbose){
                for(int k=0; k<BLOCK_SIZE; ++k)
                cout<<_mdata[i][j][k]<<", ";
                cout << endl;
            }
            
        }
    }
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::query(int task_id, map<uint16_t, map<uint16_t, vector<uint16_t>>>& mdata, bool verbose){
    // tbc_id, <block_id, data>
    update(verbose); //Read Data.
    for(auto& task : _tasks){
        int temp_task_id = task.first;
        auto& temp_task_info = task.second;
        if(temp_task_id == task_id){
            for(auto& block : temp_task_info._blocks){
                vector<uint16_t> temp;
                int tbc_id = block.tbc_id;
                int block_id = block.block_id;
                int memory_type = block.block_type;
                int sub_block_id = block.block_offset;
                read(tbc_id, block_id, memory_type, sub_block_id, temp);
                mdata[tbc_id][block_id] = temp;
            }
        }
    }
}



template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
void TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::read(int tbc_id, int block_id, int memory_type, int sub_block_id, vector<uint16_t>& block){
    block.resize(0);
    if(memory_type == MEMORY_1){
        // block.assign(_mdata[tbc_id][block_id].begin(), _mdata[tbc_id][block_id].end());
        block.insert(block.begin(), _mdata[tbc_id][block_id].begin(), _mdata[tbc_id][block_id].end());
        return;
    }
    int begin, end;
    if(memory_type == MEMORY_2){
        begin = sub_block_id * (BLOCK_SIZE/2);
        end = begin + (BLOCK_SIZE/2);
    }
    else if(memory_type == MEMORY_4){
        begin = sub_block_id * (BLOCK_SIZE/4);
        end = begin + (BLOCK_SIZE/4);
    }
    else if(memory_type == MEMORY_8){
        begin = sub_block_id * (BLOCK_SIZE/8);
        end = begin + (BLOCK_SIZE/8);
    }
    else if(memory_type == MEMORY_16){
        begin = sub_block_id * (BLOCK_SIZE/16);
        end = begin + (BLOCK_SIZE/16);
    }
    else if(memory_type == MEMORY_32){
        begin = sub_block_id * (BLOCK_SIZE/32);
        end = begin + (BLOCK_SIZE/32);
    }
    else if(memory_type == MEMORY_64){
        begin = sub_block_id * (BLOCK_SIZE/64);
        end = begin + (BLOCK_SIZE/64);
    }
    else if(memory_type == MEMORY_128){
        begin = sub_block_id * (BLOCK_SIZE/128);
        end = begin + (BLOCK_SIZE/128);
    }
    HOW_LOG(L_INFO,"Read data for tbc %d:%d, type %d, start %d, end %d", tbc_id, block_id, memory_type, begin, end);
    block.insert(block.begin(), _mdata[tbc_id][block_id].begin()+begin, _mdata[tbc_id][block_id].begin()+end);
    return;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
string TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::getSubBlockTypeStr(int block_type){
    if(block_type == MEMORY_1) return "PARTITION_ALL";
    if(block_type == MEMORY_2) return "PARTITION_2";
    if(block_type == MEMORY_4) return "PARTITION_4";
    if(block_type == MEMORY_8) return "PARTITION_8";
    if(block_type == MEMORY_16) return "PARTITION_16";
    if(block_type == MEMORY_32) return "PARTITION_32";
    if(block_type == MEMORY_64) return "PARTITION_64";
    if(block_type == MEMORY_128) return "PARTITION_128";
    return "UNKOWN";
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::getSubBlockSize(int block_type){
    if(block_type == MEMORY_1)   return BLOCK_SIZE;
    if(block_type == MEMORY_2)   return BLOCK_SIZE/2;
    if(block_type == MEMORY_4)   return BLOCK_SIZE/4;
    if(block_type == MEMORY_8)   return BLOCK_SIZE/8;
    if(block_type == MEMORY_16)  return BLOCK_SIZE/16;
    if(block_type == MEMORY_32)  return BLOCK_SIZE/32;
    if(block_type == MEMORY_64)  return BLOCK_SIZE/64;
    if(block_type == MEMORY_128) return BLOCK_SIZE/128;
    return -1;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::getSubBlockLevel(int sub_block_type){
    if(sub_block_type == MEMORY_1)   return 0;
    if(sub_block_type == MEMORY_2)   return 1;
    if(sub_block_type == MEMORY_4)   return 2;
    if(sub_block_type == MEMORY_8)   return 3;
    if(sub_block_type == MEMORY_16)  return 4;
    if(sub_block_type == MEMORY_32)  return 5;
    if(sub_block_type == MEMORY_64)  return 6;
    if(sub_block_type == MEMORY_128) return 7;
    return -1;
}


template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::getSubBlockType(int need_sub_block){
    // always accurate mode.
    uint16_t times = SUB_BLOCK_NUM / need_sub_block;
    if (times >= 128)
        return MEMORY_128;
    if (times >= 64)
        return MEMORY_64;
    if (times >= 32)
        return MEMORY_32;
    if (times >= 16)
        return MEMORY_16;
    if (times >= 8)
        return MEMORY_8;
    if (times >= 4)
        return MEMORY_4;
    if (times >= 2)
        return MEMORY_2;
    if (times >= 1)
        return MEMORY_1;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::register_tasks(int block_num, int block_size, int coin_level){
    // three independent tasks.
    map<int, vector<BLOCK_INFO>> coin_blocks; // we need to select the common coin with enough blocks.
    // Allocate blocks...
    uint32_t sub_block_size = BLOCK_SIZE / SUB_BLOCK_NUM;
    uint16_t need_sub_block = (block_size / sub_block_size < 1)? 1 : block_size / sub_block_size;
    uint16_t task_memory_type = getSubBlockType(need_sub_block);
    uint16_t task_memory_level = getSubBlockLevel(task_memory_type);
    coin_level = (coin_level == COINS_DEAULT) ? task_memory_level : coin_level;
    HOW_LOG(L_DEBUG, "Require Block Size %d, require block type %d", block_size, task_memory_type);
    for(uint32_t i=0; i<TBC_NUM; i++){
        for(uint32_t j=0; j<BLOCK_NUM; ++j){
            int re1 = _status[i]->check_memory(j, task_memory_level);
            vector<int> re2 = _status[i]->check_coins(j, coin_level);
            if (re1 != -1 and re2.size() != 0) 
            {
                BLOCK_INFO bif = {static_cast<int>(i), static_cast<int>(j), static_cast<int>(task_memory_type), re1};
                for(int k = 0; k<re2.size(); ++k){
                    coin_blocks[re2[k]].push_back(bif);
                }
            }       
        }
    }
    for(auto& item : coin_blocks){
        int coin_level_idx = item.first;
        if(item.second.size() >=  block_num){
            _TASK_ID += 1;
            _tasks[_TASK_ID] = TASK_INFO();
            _tasks[_TASK_ID].task_id = _TASK_ID;
            int allocated_block_num = 0;
            for(auto& block : item.second){
                if(allocated_block_num < block_num){
                    int tbc_id = block.tbc_id;
                    int block_id = block.block_id;
                    int sub_block_id = block.block_offset;
                    _status[tbc_id]->acllocate_memory(block_id, task_memory_level, sub_block_id, _tasks[_TASK_ID].task_id);
                    _tasks[_TASK_ID].coins = _status[tbc_id]->acllocate_coins(block_id, coin_level, coin_level_idx, _tasks[_TASK_ID].task_id);
                    allocated_block_num += 1;
                    _tasks[_TASK_ID]._blocks.push_back(block);
                }
            }
            if(allocated_block_num < block_num)
                return -1;
            vector<string> possible_coins;
            _status[0]->get_possible_coins(_tasks[_TASK_ID].coins, possible_coins);
            for(auto& possible_coin : possible_coins){
                _coins_tasks[possible_coin].push_back(_TASK_ID);
                // cout <<"可能的coin "<< possible_coin <<endl;
            }
            return _tasks[_TASK_ID].task_id;
        }
    }
    return -1;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::register_tasks_v2(const vector<int>& graph, int mode, int coin_level){
    // convert graph to level.
    vector<pair<uint16_t, uint16_t>> real_graph;
    uint32_t sub_block_size = BLOCK_SIZE / SUB_BLOCK_NUM;
    uint16_t smallest_coin_level = 0;  // smallest coin level
    for(int i=0; i<graph.size(); ++i){
        uint16_t need_sub_block = (graph[i] / sub_block_size < 1)? 1 : graph[i]  / sub_block_size;
        uint16_t task_memory_type = getSubBlockType(need_sub_block);
        uint16_t task_memory_level = getSubBlockLevel(task_memory_type);  
        if(task_memory_level > smallest_coin_level){
            smallest_coin_level = task_memory_level;
        }
        // TODO: allocate mode select.  
        real_graph.push_back(make_pair(task_memory_type, task_memory_level));
        HOW_LOG(L_DEBUG, "Graph node %d, memory size %d, type %s.", i, graph[i], getSubBlockTypeStr(task_memory_type).c_str());
    }
    coin_level = (coin_level == COINS_DEAULT) ? smallest_coin_level : coin_level;
    int commmon_coin_id = -1;          // common coin id for smallest coin level.
    // subgraph match.
    vector<BLOCK_INFO> avaliable_block_graph;  // a list of block_graph : vector<BLOCK_INFO>
    for(uint32_t i=0; i<TBC_NUM; i++){
        if(avaliable_block_graph.size() != 0)
            break;
        for(uint32_t j=0; j<BLOCK_NUM; ++j){
            bool isMatch = true;
            vector<vector<int>> avaliable_coins(real_graph.size()); 
            for(int k=0; k<real_graph.size(); ++k){  // a chain-style match.
                if( j + k >= BLOCK_NUM){
                    isMatch = false;
                    break;
                }
                int re1 = _status[i]->check_memory(j+k, real_graph[k].second);   // check if memorys are fit.
                avaliable_coins[k] = _status[i]->check_coins(j+k, coin_level); // we only use the select coin level.
                if( re1 ==-1 || avaliable_coins[k].size() == 0){
                    isMatch = false;
                    break;
                }
            }
            
            if(isMatch){  // Memory is fits. j, j+1, j+...k.
                // Select common coins.
                vector<int> level_coins_ids;
                for(int p =0; p< pow(2, coin_level); ++p )
                    level_coins_ids.push_back(p);  // firstly list all possible coin ids for ;
                for(auto& coin_id : level_coins_ids){
                    // check if all block have this coin_id.
                    bool all_have =true;
                    for(int q=0; q<avaliable_coins.size(); ++q){
                        if(find(avaliable_coins[q].begin(), avaliable_coins[q].end(), coin_id) == avaliable_coins[q].end()){
                            all_have = false;
                            break;
                        }
                    }
                    if(all_have){
                        commmon_coin_id = coin_id;
                        break;
                    }
                }
                if(commmon_coin_id == -1){
                    break;
                }
                for(uint32_t m=0; m<real_graph.size(); ++m){
                    int offset = _status[i]->check_memory(j+m, real_graph[m].second);
                    BLOCK_INFO bif = {static_cast<int>(i), static_cast<int>(j+m), static_cast<int>(real_graph[m].first), offset};
                    avaliable_block_graph.push_back(bif);
                }
                break;
            } 
        }
    }
    if(avaliable_block_graph.size() < real_graph.size()){
        return -1;
    }
    _TASK_ID += 1;
    _tasks[_TASK_ID] = TASK_INFO();
    _tasks[_TASK_ID].task_id = _TASK_ID;
    for(auto& block : avaliable_block_graph){
        int tbc_id = block.tbc_id;
        int block_id = block.block_id;
        int memory_type = block.block_type;
        int sub_block_id = block.block_offset;
        uint16_t task_memory_level = getSubBlockLevel(memory_type);   
        _status[tbc_id]->acllocate_memory(block_id, task_memory_level, sub_block_id, _tasks[_TASK_ID].task_id);
        _tasks[_TASK_ID].coins = _status[tbc_id]->acllocate_coins(block_id, coin_level, commmon_coin_id, _tasks[_TASK_ID].task_id);
        _tasks[_TASK_ID]._blocks.push_back(block);
    }
    // add coin infomation for statistics.
    vector<string> possible_coins;
    _status[0]->get_possible_coins(_tasks[_TASK_ID].coins, possible_coins); // 0 is just a defaut tool.
    for(auto& possible_coin : possible_coins){
        _coins_tasks[possible_coin].push_back(_TASK_ID);  // for ground truth monitor
    }
    HOW_LOG(L_DEBUG, "Graph common coin : %s.", _tasks[_TASK_ID].coins.c_str());
    return _tasks[_TASK_ID].task_id;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
void TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::reset(){
    // Reset All
    for(int i=0; i<TBC_NUM; ++i)
    {
        delete _tbc[i];
        delete _status[i];
    }
    _mdata.clear();
    _tasks.clear();
    _mdata.resize(TBC_NUM);
    for(int i =0; i < TBC_NUM; ++i){
        _tbc[i]= new TBC(BLOCK_NUM, BLOCK_SIZE);
        _status[i]= new TBC_Resource_Manager(BLOCK_NUM, get_level_num());
        _mdata[i].resize(BLOCK_NUM, vector<uint16_t>(0,0));
    }
    _TASK_ID = 0;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::get_address(int task_id, int tbc_id, int block_id, const uint8_t* key, int key_len){
    auto& task_info = _tasks[task_id];
    for(auto& block : task_info._blocks){
        int temp_tbc_id = block.tbc_id;
        int temp_block_id = block.block_id;
        int temp_memory_type = block.block_type;
        int temp_sub_block_id = block.block_offset;
        if(tbc_id ==temp_tbc_id && block_id == temp_block_id){
            uint32_t hash_value = (_tbc[tbc_id]->getHashFunc())->run((char*)key, key_len);
            uint32_t hash_result = ( (hash_value & (0xfffff << 4*temp_block_id)) >> (4*temp_block_id) ) % BLOCK_SIZE;
            if(temp_memory_type == MEMORY_1){
                return hash_result;
            }
            else if(temp_memory_type == MEMORY_2){
                hash_result = hash_result >> 1;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/2);
            }
            else if(temp_memory_type == MEMORY_4){
                hash_result = hash_result >> 2;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/4);
            }
            else if(temp_memory_type == MEMORY_8){
                hash_result = hash_result >> 3;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/8);
            }
            else if(temp_memory_type == MEMORY_16){
                hash_result = hash_result >> 4;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/16);
            }
            else if(temp_memory_type == MEMORY_32){
                hash_result = hash_result >> 5;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/32);
            }
            else if(temp_memory_type == MEMORY_64){
                hash_result = hash_result >> 6;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/64);
            }
            else if(temp_memory_type == MEMORY_128){
                hash_result = hash_result >> 7;
                hash_result += temp_sub_block_id*(BLOCK_SIZE/128);
            }
            return hash_result;
        }
    }
    HOW_LOG(L_ERROR, "Cannot get a valid address.");
    return 0;
}

template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
int TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::get_val_hash(int task_id, int tbc_id, int block_id, const uint8_t* val, int val_len){
    auto& task_info = _tasks[task_id];
    for(auto& block : task_info._blocks){
        int temp_tbc_id = block.tbc_id;
        int temp_block_id = block.block_id;
        int temp_memory_type = block.block_type;
        int temp_sub_block_id = block.block_offset;
        if(tbc_id ==temp_tbc_id && block_id == temp_block_id){
            uint32_t hash_value = (_tbc[tbc_id]->getHashFunc())->run((char*)val, val_len);
            return  ( (hash_value & (0xfffff >> 4*temp_block_id)) >> (12 - 4*temp_block_id) );
        }
    }
    return 0;
}

// template<int BLOCK_SIZE, int SUB_BLOCK_NUM>
// int BLOCK_STATUS<BLOCK_SIZE, SUB_BLOCK_NUM>::judge_flags(int level){ // return index of selected level.
//     vector<int> barrires;
//     int hyper_block_num = 0; // how many subblock in each hyper block
//     int sub_block_num_per_hyper_block = 0;
//     if(level == MEMORY_ALL){
//         sub_block_num_per_hyper_block = SUB_BLOCK_NUM;
//         hyper_block_num = 1;
//     }
//     else if(level == MEMORY_HALF){
//         sub_block_num_per_hyper_block = SUB_BLOCK_NUM/2;
//         hyper_block_num = 2;
//     }
//     else if(level == MEMORY_QUART){
//         sub_block_num_per_hyper_block = SUB_BLOCK_NUM/4;
//         hyper_block_num = 4;
//     }
//     else if(level == MEMORY_EIGHT){
//         sub_block_num_per_hyper_block = SUB_BLOCK_NUM/8;
//         hyper_block_num = 8;
//     }
//     else {
//         sub_block_num_per_hyper_block = SUB_BLOCK_NUM/16;
//         hyper_block_num = 16;
//     }
//     if(sub_block_num_per_hyper_block < 1){
//         HOW_LOG(L_ERROR, "request sub block level too small.");
//         exit(1);
//     }
//     int barrier_num = hyper_block_num + 1;
//     for (int i=0; i<barrier_num; ++i){
//         barrires.push_back(i * sub_block_num_per_hyper_block);
//     }
//     int sub_block_index = 0;
//     for(int b = 0; b<barrires.size()-1; ++b){
//         int start = barrires[b];
//         int end = barrires[b+1];
//         bool ok = true;
//         for(int i=start; i<end; ++i){
//             if(flags[i] != 0)
//             {
//                 ok = false;
//                 break;
//             }
//         }
//         if (ok) return sub_block_index;
//         else sub_block_index += 1;
//     }
//     return -1;
// }

// template<int BLOCK_SIZE, int SUB_BLOCK_NUM>
// void BLOCK_STATUS<BLOCK_SIZE, SUB_BLOCK_NUM>::set_flags(int level, int index, int task_id){ 
//     int half_base = SUB_BLOCK_NUM / 2;
//     int quarter_base = SUB_BLOCK_NUM / 4;
//     int eight_base = SUB_BLOCK_NUM / 8;
//     int sixteen_base = SUB_BLOCK_NUM / 16;
//     if(level == MEMORY_ALL){
//         for(int i=0; i<SUB_BLOCK_NUM; ++i)
//         {
//             flags[i] = task_id;
//         }
//     }
//     else if(level == MEMORY_HALF){
//         for(int i=index * half_base; i < index*half_base + half_base; ++i){
//             flags[i] = task_id;
//         }
//     }
//     else if(level == MEMORY_QUART){
//         for(int i=index*quarter_base; i < index*quarter_base + quarter_base; ++i){
//             flags[i] = task_id;
//         }
//     }else if(level == MEMORY_EIGHT){
//         for(int i=index*eight_base; i < index*eight_base + eight_base; ++i){
//             flags[i] = task_id;
//         }
//     }else{
//         if(SUB_BLOCK_NUM < 16){
//             HOW_LOG(L_ERROR, "request sub block level too small.");
//             exit(1);
//         }
//         flags[i] = task_id;
//     }
// }

// template<int TBC_NUM, int BLOCK_NUM, int BLOCK_SIZE, int SUB_BLOCK_NUM>
// double TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>::coins2double(const string& coins){
//     if(coins.size()!=4){
//         return 0;
//     }
//     if(coins[0] != '*'){
//         return 1/8;
//     }
//     if(coins[1] != '*'){
//         return 1/4;
//     }
//     if(coins[2] != '*'){
//         return 1/2;
//     }
//     return 1;
// }
#endif