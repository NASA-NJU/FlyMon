
#ifndef _TBC_H_
#define _TBC_H_

#include<cstdint>
#include <map>
#include <bitset>
#include <cmath>
#include <vector>
#include "tbc/p4.h"
#include "tbc/tbc_common.h"
#include "BOBHash/BOBHash32.h"
#include "HowLog/HowLog.h"
using namespace std;



class PipeMeta: public Metadata{
public:
    PipeMeta(int block_num){
        key = 0;
        val = 0;
        param = 0;
        result = 0;
        uint32_t coin_size = static_cast<uint32_t>(log2(MEMROY_PARTITION));
        coins.resize(coin_size);
        results.resize(block_num);
        ipsrc_prehash = 0;
        ipdst_prehash = 0;
        ippair_prehash = 0;
        tstamp_prehash = 0;
    }
    ~PipeMeta() = default;

    uint32_t get_metadata(const string& name){
        if(name == "key") return key;
        else if (name == "val") return val;
        else if (name == "param") return param;
        else if (name == "result") return result;
        return 0;
    }
    uint32_t key;
    uint16_t val; 
    uint16_t param;
    uint16_t result;

    vector<uint16_t> results; // temp

    vector<char>  coins;
    uint32_t ipsrc_prehash;
    uint32_t ipdst_prehash;
    uint32_t ippair_prehash;
    uint32_t tstamp_prehash;
};

class TBlock {
    public:
        TBlock(uint16_t id, uint32_t size);
        TBlock(const TBlock& tblock);
        ~TBlock();
        void addRule(uint16_t table_id, 
                     FlowRuleMatch* match, 
                     FlowRuleAction* action, const vector<uint16_t>& params){
            if (_tables.find(table_id) != _tables.end()){
                _tables[table_id]->addRule(match, action, params);
            }
        }
        uint16_t get(uint32_t index){
            if(index >= _size) return -1;
            return _pages[index];
        }
        uint16_t set(uint32_t index, uint16_t value){
            if(index >= _size) 
                return -1;
            _pages[index] = value;
            return 0;
        }
        void apply(TracePacket* hdr, PipeMeta* meta);
    private:
        uint16_t _id;
        uint32_t _size;
        vector<uint16_t> _pages;
        map<uint16_t, FlowTable*>  _tables;
};


class TBC{
private:
    uint16_t _block_num;
    uint32_t _block_size;
    vector<TBlock> _blocks;
    BOBHash32* _keyhash_func;
    // BOBHash32* _coinhash_func;

public: // action list..
    // action name, action instance.
    map<uint16_t, FlowRuleAction*> Actions; // block actions array.

public:
    TBC(uint16_t block_num, uint32_t block_size);
    ~TBC(){
        delete _keyhash_func;
        _blocks.clear();
        for(auto& item : Actions){
            delete item.second;
        }
        // delete _coinhash_func;
    }

    // return coins.
    string apply(TracePacket* hdr, PipeMeta* meta);

    void addRule(uint16_t block_id, uint16_t table_id, 
                               FlowRuleMatch* match, 
                               FlowRuleAction* action, const vector<uint16_t>& params={}){
        _blocks[block_id].addRule(table_id, match, action, params);
    }

    void readBlock(uint16_t block_id, vector<uint16_t>& values){
        values.resize(_block_size, 0);
        for(uint32_t i=0; i<_block_size; ++i){
            values[i] = _blocks[block_id].get(i);
        }
    }
    uint16_t readMemory(uint16_t block_id, uint32_t address){
        return _blocks[block_id].get(address);
    } 
    void writeMemory(uint16_t block_id, uint32_t address, uint16_t value){
        _blocks[block_id].set(address, value);
    } 

    BOBHash32* getHashFunc(){ return _keyhash_func;}

private:
    string init(TracePacket* hdr, Metadata* meta);
    void load_actions();

    // Initialization Stage
    void action_setkey_ippair(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 
    void action_setkey_ipsrc(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 
    void action_setkey_ipdst(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 

    void action_setval_const(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});    // can be shared by multiple blocks.
    void action_setval_ippair_hash(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});    // can be shared by multiple blocks.
    void action_setval_ipsrc_hash(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});    // can be shared by multiple blocks.
    void action_setval_ipdst_hash(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});    // can be shared by multiple blocks.
    void action_setval_timestamp(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});    // can be shared by multiple blocks.


    void action_setparam_const(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});    // can be shared by multiple blocks.
    void action_setparam_ipsrc(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 
    void action_setparam_ippair(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 
    void action_setparam_result(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 
    void action_setparam_timestamp(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={}); 

    // Pre-processing Stage
    void action_key_mapping_1(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});
    void action_key_mapping_2(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});  
    void action_key_mapping_4(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});  
    void action_key_mapping_8(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});  
    void action_key_mapping_16(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});  
    void action_key_mapping_32(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});
    void action_key_mapping_64(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});  
    void action_key_mapping_128(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params={});  

    void action_val_subresult(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params);
    void action_val_no_action(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params);
    void action_val_one_hot(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params);  

    // Operation Stage
    void action_op_cmp_add(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params);    
    void action_op_max(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params);
    void action_op_set(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params); 
    void action_op_and(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params); 
    void action_op_or(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params); 
    void action_op_range_count(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params);  
};

class RandomFTupleMatch : public FTupleMatch{
public:
    RandomFTupleMatch(  const string& coins,    
                        const string& ipsrc_w_mask,    // 10.0.0.*
                        const string& ipdst_w_mask,    // 10.0.0.*
                        const string& sport_w_mask,    // uint16_t or *
                        const string& dport_w_mask,    // uint16_t or *
                        const string& protocol_w_mask, // uint8_t or *
                        const string& extra_key = "",
                        const string& extra_val = "") 
        :FTupleMatch(ipsrc_w_mask, ipdst_w_mask, sport_w_mask, dport_w_mask, protocol_w_mask){
        _coins.assign(coins.begin(), coins.end());
        _extra_match_key = extra_key;
        if(extra_key != "")
        {
            // _extra_match_val.assign(extra_val.begin(), extra_val.end());
            string matcha;
            string mask;
            int len = 0;
            for(auto & ch : extra_val)
            {
                if(ch != '*') 
                {
                    matcha.push_back(ch);
                    mask.push_back('1');
                    len += 1;
                }
                else break;
            }
            string zeros;
            zeros.resize(32-len, '0');
            matcha = zeros + matcha;
            mask = zeros + mask;
            _extra_match_val_fast = bitset<32>(matcha );
            _extra_match_mask_fast = bitset<32>(mask );
        }
    }
    RandomFTupleMatch(  const string& coins,          
                        FTupleMatch* match,
                        const string& extra_key = "",
                        const string& extra_val = "")  
        :FTupleMatch(match){
        _coins.assign(coins.begin(), coins.end());
        _extra_match_key = extra_key;
        if(extra_key != "")
        {
            // _extra_match_val.assign(extra_val.begin(), extra_val.end());
            string matcha;
            string mask;
            int len = 0;
            for(auto & ch : extra_val)
            {
                if(ch != '*') 
                {
                    matcha.push_back(ch);
                    mask.push_back('1');
                    len += 1;
                }
                else break;
            }
            string zeros;
            zeros.resize(32-len, '0');
            matcha = zeros + matcha;
            mask = zeros + mask;
            _extra_match_val_fast = bitset<32>(matcha );
            _extra_match_mask_fast = bitset<32>(mask );
        }
        
    }
    virtual bool hit(TracePacket* hdr, Metadata* meta)const;
    ~RandomFTupleMatch(){
    }
private:
    vector<char> _coins;
    string _extra_match_key;
    // vector<char> _extra_match_val;
    bitset<32> _extra_match_val_fast;
    bitset<32> _extra_match_mask_fast;
};
#endif