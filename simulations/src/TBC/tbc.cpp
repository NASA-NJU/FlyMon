#include "tbc/tbc.h"
#include <ctime>
#include <cstdlib>

TBlock::TBlock(uint16_t id, uint32_t size)
{
    _id = id;
    _size = size;
    _pages.resize(size,0);
    _tables[TABLE_KEY_INIT] = new FlowTable();
    _tables[TABLE_VAL_INIT] =  new FlowTable();
    _tables[TABLE_PARAM_INIT] = new FlowTable();
    _tables[TABLE_KEY_MAPPING] = new FlowTable();
    _tables[TABLE_VAL_PROCESS] = new FlowTable();
    _tables[TABLE_OP_SELECT] = new FlowTable();
}

TBlock::TBlock(const TBlock& ano){
    _id = ano._id;
    _size = ano._size;
    _pages = ano._pages;
    for(auto& table : ano._tables){
        FlowTable* temp = new FlowTable(*table.second);
        _tables.insert(make_pair(table.first, temp));
    }    
}
TBlock::~TBlock(){
    for(auto& table : _tables){
        delete table.second;
    }
}

void TBlock::apply(TracePacket* hdr, PipeMeta* meta){
    _tables[TABLE_KEY_INIT]->apply(hdr, meta);
    _tables[TABLE_VAL_INIT]->apply(hdr, meta);
    _tables[TABLE_PARAM_INIT]->apply(hdr, meta);
    _tables[TABLE_KEY_MAPPING]->apply(hdr, meta);
    _tables[TABLE_VAL_PROCESS]->apply(hdr, meta);
    _tables[TABLE_OP_SELECT]->apply(hdr, meta);
}

TBC::TBC(uint16_t block_num, uint32_t block_size)
{
    _block_num = block_num;
    _block_size = block_size;
    
    random_device rd;
    _keyhash_func = new BOBHash32(uint32_t(rd() % MAX_PRIME32));
    for(auto i=0; i<block_num; ++i){
        _blocks.push_back(TBlock(i, block_size)); //在构造列表里面，可能会引用同一个实例.
    } 
    load_actions();
}

string TBC::apply(TracePacket* hdr, PipeMeta* meta){
    string coins = this->init(hdr, meta);
    for (int i=0; i<_block_num; ++i){
        _blocks[i].apply(hdr, meta);
    }
    return coins;
}

string TBC::init(TracePacket* hdr, Metadata* meta){
    // roll coins.
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    uint8_t random_number = rand() % 256;
    for(uint32_t i =0; i<pipe_meta->coins.size(); ++i){
        pipe_meta->coins[i] = ((random_number & (1<<i)) == (1<<i))? '1' : '0';
    }
    // It's no need to dynamic change hash functions in simulation.
    // We pre-calculate all hashes.
    for(int i=0; i<_block_num; ++i){  // block_num <= 4
        // select hash from different bit range from compression layer. TODO: more clearly.
        pipe_meta->ipsrc_prehash = _keyhash_func->run((char *)hdr->getSrcBytes(), 4);
        pipe_meta->ipdst_prehash = _keyhash_func->run((char *)hdr->getDstBytes(), 4);
        pipe_meta->ippair_prehash = _keyhash_func->run((char *)hdr->getFlowKey_IPPair(), 8);
        uint64_t timestamp = hdr->getTimestamp_ns();
        pipe_meta->tstamp_prehash = _keyhash_func->run((char *)(&timestamp), 8);
    }
    return string(pipe_meta->coins.begin(), pipe_meta->coins.end());
}

void TBC::load_actions(){
    Actions[ACTION_SET_KEY_IPPAIR] = ActionMaker::make_action(&TBC::action_setkey_ippair, this);
    Actions[ACTION_SET_KEY_IPSRC] = ActionMaker::make_action(&TBC::action_setkey_ipsrc, this);
    Actions[ACTION_SET_KEY_IPDST] = ActionMaker::make_action(&TBC::action_setkey_ipdst, this); 
    // 

    Actions[ACTION_SET_VAL_CONST] = ActionMaker::make_action(&TBC::action_setval_const, this);
    Actions[ACTION_SET_VAL_IPPAIR_HASH] = ActionMaker::make_action(&TBC::action_setval_ippair_hash, this); 
    Actions[ACTION_SET_VAL_IPSRC_HASH] = ActionMaker::make_action(&TBC::action_setval_ipsrc_hash, this); 
    Actions[ACTION_SET_VAL_IPDST_HASH] = ActionMaker::make_action(&TBC::action_setval_ipdst_hash, this); 
    Actions[ACTION_SET_VAL_TIMESTAMP] = ActionMaker::make_action(&TBC::action_setval_timestamp, this); 
    
    Actions[ACTION_SET_PARAM_CONST] =  ActionMaker::make_action(&TBC::action_setparam_const, this); 
    Actions[ACTION_SET_PARAM_RESULT] = ActionMaker::make_action(&TBC::action_setparam_result, this); 
    Actions[ACTION_SET_PARAM_IPSRC] =  ActionMaker::make_action(&TBC::action_setparam_ipsrc, this); 
    Actions[ACTION_SET_PARAM_IPPAIR] =  ActionMaker::make_action(&TBC::action_setparam_ippair, this); 
    Actions[ACTION_SET_PARAM_TIMESTAMP] =  ActionMaker::make_action(&TBC::action_setparam_timestamp, this); 

    Actions[ACTION_SET_KEY_MAPPING_1] = ActionMaker::make_action(&TBC::action_key_mapping_1, this);
    Actions[ACTION_SET_KEY_MAPPING_2] = ActionMaker::make_action(&TBC::action_key_mapping_2, this);
    Actions[ACTION_SET_KEY_MAPPING_4] = ActionMaker::make_action(&TBC::action_key_mapping_4, this);
    Actions[ACTION_SET_KEY_MAPPING_8] = ActionMaker::make_action(&TBC::action_key_mapping_8, this);
    Actions[ACTION_SET_KEY_MAPPING_16] = ActionMaker::make_action(&TBC::action_key_mapping_16, this);
    Actions[ACTION_SET_KEY_MAPPING_32] = ActionMaker::make_action(&TBC::action_key_mapping_32, this);
    Actions[ACTION_SET_KEY_MAPPING_64] = ActionMaker::make_action(&TBC::action_key_mapping_64, this);
    Actions[ACTION_SET_KEY_MAPPING_128] = ActionMaker::make_action(&TBC::action_key_mapping_128, this);

    Actions[ACTION_VAL_NO_ACTION] = ActionMaker::make_action(&TBC::action_val_no_action, this);
    Actions[ACTION_VAL_SUB_RESULT] = ActionMaker::make_action(&TBC::action_val_subresult, this); 
    Actions[ACTION_VAL_ONE_HOT] = ActionMaker::make_action(&TBC::action_val_one_hot, this); 
    
    Actions[ACTION_OP_CMP_ADD] = ActionMaker::make_action(&TBC::action_op_cmp_add, this);  
    Actions[ACTION_OP_MAX] = ActionMaker::make_action(&TBC::action_op_max, this);
    Actions[ACTION_OP_SET] = ActionMaker::make_action(&TBC::action_op_set, this);  
    Actions[ACTION_OP_AND] = ActionMaker::make_action(&TBC::action_op_and, this);  
    Actions[ACTION_OP_OR] = ActionMaker::make_action(&TBC::action_op_or, this);  
    Actions[ACTION_OP_RANGE_COUNT] = ActionMaker::make_action(&TBC::action_op_range_count, this);  
}

bool RandomFTupleMatch::hit(TracePacket* hdr, Metadata* meta)const{
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    // uint8_t coins = pipe_meta->coins[_block_id];
    auto& in_coins = pipe_meta->coins;
    // HOW_LOG(L_INFO, "尝试比较coins, Rule Coins %s, Packet Coins %s", string(_coins.begin(), _coins.end()).c_str(), string(in_coins.begin(), in_coins.end()).c_str());
    if(in_coins.size() != _coins.size()){
        HOW_LOG(L_INFO, "TBC structure coin size %d, input rule coin size %d", in_coins.size(), _coins.size());
        exit(1);
    }

    for(auto i =0; i<in_coins.size(); ++i){
        if(_coins[i] != '*' && in_coins[i] != _coins[i])
            return false;
    }
    if( _extra_match_key != ""){
        bitset<32> extra_val = bitset<32>(pipe_meta->get_metadata(_extra_match_key));
        // for(auto i=0; i<_extra_match_val.size(); ++i){   // 从低位向高位匹配, 防止param过小.
        //     char bit_val = ((extra_val & (1<<i)) == (1<<i))? '1' : '0';
        //     if(_extra_match_val[i] != '*' && _extra_match_val[i] != bit_val)  // 这个倒是暂时无所谓, 实际值的0001 匹配rule的 1000.
        //         return false;
        // }
        if((extra_val & _extra_match_mask_fast) != _extra_match_val_fast){
            return false;
        }
    }
    return FTupleMatch::hit(hdr, meta);
}

// There are some common actions.
// Param 0: Block ID
void TBC::action_setkey_ippair(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->key = ( (pipe_meta->ippair_prehash & (0xfffff << 4*block_id)) >> (4*block_id)  ) % _block_size;
}

void TBC::action_setkey_ipsrc(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->key = ( (pipe_meta->ipsrc_prehash & (0xfffff << 4*block_id)) >> (4*block_id)  ) % _block_size;
}

void TBC::action_setkey_ipdst(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->key = ( (pipe_meta->ipdst_prehash & (0xfffff << 4*block_id)) >> (4*block_id)  ) % _block_size;
}

void TBC::action_setval_ippair_hash(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->val = (pipe_meta->ipdst_prehash & (0xfffff000 >> 4*block_id)) >> (12 - 4*block_id);
}
void TBC::action_setval_ipsrc_hash(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->val = (pipe_meta->ipsrc_prehash & (0xfffff000 >> 4*block_id)) >> (12 - 4*block_id);
}
void TBC::action_setval_ipdst_hash(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->val = (pipe_meta->ipdst_prehash & (0xfffff000 >> 4*block_id)) >> (12 - 4*block_id);
}
void TBC::action_setval_timestamp(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){ // us level
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        pipe_meta->val = static_cast<uint16_t>(hdr->getTimestamp_us());
}

// Param 0: Const value
void TBC::action_setval_const(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t const_val = params[0];
        pipe_meta->val = const_val;
}

// Param 0: Const value
void TBC::action_setparam_const(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t const_val = params[0];
        pipe_meta->param = const_val;
}

void TBC::action_setparam_result(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        pipe_meta->param = pipe_meta->result;
}

void TBC::action_setparam_ipsrc(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->param = (pipe_meta->ipsrc_prehash & (0xfffff000 >> 4*block_id)) >> (12 - 4*block_id);
}
void TBC::action_setparam_ippair(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->param = (pipe_meta->ippair_prehash & (0xfffff000 >> 4*block_id)) >> (12 - 4*block_id);
}

void TBC::action_setparam_timestamp(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        pipe_meta->param = (pipe_meta->tstamp_prehash & (0xfffff000 >> 4*block_id)) >> (12 - 4*block_id);
}

void TBC::action_key_mapping_1(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        // Do Nothing
}
void TBC::action_key_mapping_2(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 1;
        pipe_meta->key += range*(_block_size/2);
}
void TBC::action_key_mapping_4(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 2;
        pipe_meta->key += range*(_block_size/4);
}
void TBC::action_key_mapping_8(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 3;
        pipe_meta->key += range*(_block_size/8);
}
void TBC::action_key_mapping_16(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 4;
        pipe_meta->key += range*(_block_size/16);
        // cout <<"sub block " << range << " key " << pipe_meta->key << endl;
}
void TBC::action_key_mapping_32(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 5;
        pipe_meta->key += range*(_block_size/32);
        // cout <<"sub block " << range << " key " << pipe_meta->key << endl;
}

void TBC::action_key_mapping_64(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 6;
        pipe_meta->key += range*(_block_size/64);
        // cout <<"sub block " << range << " key " << pipe_meta->key << endl;
}

void TBC::action_key_mapping_128(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint32_t range = params[0];
        pipe_meta->key = pipe_meta->key >> 7;
        pipe_meta->key += range*(_block_size/128);
        // cout <<"sub block " << range << " key " << pipe_meta->key << endl;
}


void TBC::action_val_no_action(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        // NO ACTION
}

void TBC::action_val_subresult(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        // NO ACTION
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        pipe_meta->val = pipe_meta->val - pipe_meta->result;
}
void TBC::action_val_one_hot(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        pipe_meta->val = params[0];
}

// Param 0: Block ID
void TBC::action_op_cmp_add(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
        PipeMeta* pipe_meta = (PipeMeta*)meta;
        if(params.size() < 1)
        {
            HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
            return;
        }
        uint16_t block_id = params[0];
        uint16_t mem_val = _blocks[block_id].get(pipe_meta->key);
        if(mem_val < pipe_meta->param)
        {

            int new_val = (mem_val > 65530)? mem_val : mem_val + pipe_meta->val;
            _blocks[block_id].set(pipe_meta->key, new_val);
            pipe_meta->result = new_val;
        }
        else{
            pipe_meta->result = pipe_meta->param;
        }
        // record
        pipe_meta->results[block_id] = pipe_meta->result;
}

// Param 0: Block ID
void TBC::action_op_max(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    if(params.size() < 1)
    {
        HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
        return;
    }
    uint16_t block_id = params[0];
    uint16_t mem_val = _blocks[block_id].get(pipe_meta->key);
    if(mem_val < pipe_meta->val)
    {
        pipe_meta->result = mem_val;
        
        _blocks[block_id].set(pipe_meta->key, pipe_meta->val);
    }
    else{
        pipe_meta->result = pipe_meta->val;
    }
    // record
    pipe_meta->results[block_id] = pipe_meta->result;
}
void TBC::action_op_and(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    if(params.size() < 1)
    {
        HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
        return;
    }
    uint16_t block_id = params[0];
    uint16_t mem_val = _blocks[block_id].get(pipe_meta->key);
    // _blocks[block_id].set(pipe_meta->key, mem_val & pipe_meta->val);
    pipe_meta->result = mem_val & pipe_meta->val;
    // record
    pipe_meta->results[block_id] = pipe_meta->result;
}
void TBC::action_op_or(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    if(params.size() < 1)
    {
        HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
        return;
    }
    uint16_t block_id = params[0];
    uint16_t mem_val = _blocks[block_id].get(pipe_meta->key);
    _blocks[block_id].set(pipe_meta->key, mem_val | pipe_meta->val);
    pipe_meta->result = mem_val;
    // record
    pipe_meta->results[block_id] = pipe_meta->result;
}

// set new value, output old value.
void TBC::action_op_set(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    if(params.size() < 1)
    {
        HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
        return;
    }
    uint16_t block_id = params[0];
    uint16_t mem_val = _blocks[block_id].get(pipe_meta->key);
    _blocks[block_id].set(pipe_meta->key, pipe_meta->val);
    if(pipe_meta->param == 0){
        pipe_meta->result = pipe_meta->val;
    }else{
        pipe_meta->result = mem_val;
    }
    pipe_meta->results[block_id] = pipe_meta->result;
}

// set new value, output old value.
void TBC::action_op_range_count(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params) {
    PipeMeta* pipe_meta = (PipeMeta*)meta;
    if(params.size() < 1)
    {
        HOW_LOG(L_ERROR, "Invalid Action Params Num...%s:%s", __FILE__, __LINE__);
        return;
    }
    uint16_t block_id = params[0];
    uint16_t mem_val = _blocks[block_id].get(pipe_meta->key);
    _blocks[block_id].set(pipe_meta->key, pipe_meta->val);
    if(pipe_meta->val < pipe_meta->param ){
        _blocks[block_id].set(pipe_meta->key, mem_val+1);
    }
    pipe_meta->result = _blocks[block_id].get(pipe_meta->key);
    pipe_meta->results[block_id] = pipe_meta->result;
}