
#ifndef _BEAUCOUP_H_
#define _BEAUCOUP_H_

#include "BOBHash/BOBHash32.h"
#include <vector>
#include "TracePacket.h"
#include <bitset>
#include <map>
#include "HowLog/HowLog.h"
#include <cmath>
using namespace std;

struct bitmask_t{
    uint32_t bit_match;
    uint32_t bit_mask;
    bitmask_t(const string& coins) {
        // e.g., 111*****
        string match;
        for(auto& ch : coins){
            if(ch == '*') 
                break;
            match.push_back(ch);
        }
        string mask(match.size(), '1');
        uint32_t rest_size = 32 - match.size();
        string rest_str(rest_size, '0');
        match += rest_str;
        mask += rest_str;
        bitset<32> match_bits(match);
        bitset<32> mask_bits(mask);
        bit_match = match_bits.to_ulong();
        bit_mask = mask_bits.to_ulong();
    }
    bool match(uint32_t input) const{
        uint32_t masked_input = bit_mask & input;
        return masked_input == bit_match;
    }
    bool operator<(const bitmask_t& ano) const{
        if(bit_match != ano.bit_match)
            return bit_match < ano.bit_match;
        return bit_mask < ano.bit_mask;
    }
};

template<int COUPON_NUM_MAX=32>
struct coupon_t{
    int query_id;
    bitset<COUPON_NUM_MAX> coupon_idx;
    coupon_t(int qid = 0, uint32_t coupon_id = 0) {
        query_id = qid;
        if(coupon_id >= COUPON_NUM_MAX){
            HOW_LOG(L_ERROR, "Invalid coupon number!");
        }
        coupon_idx.set(coupon_id);
    }
};

struct query_t{
    int query_id;
    uint32_t key_id;
    uint32_t attr_id;
    uint32_t coupon_num;

    query_t(int qid, uint32_t key, uint32_t val){
        query_id = qid;
        key_id = key;
        attr_id = val;
        coupon_num = 0;
    }
    query_t(){
        query_id = -1;
    }
};

template<int COUPON_NUM_MAX=32, int TABLE_NUM=1>
class BeauCoup {
    // A single attribute implementation
public:
    BeauCoup(uint32_t total_mem){
        int partitions = total_mem / 4 / (pow(2, TABLE_NUM) -1);
        // we donot set timstamp bucket since our measurement task is always under ONE measurement time window. 
        _buckets_tables.resize(TABLE_NUM, vector<bitset<COUPON_NUM_MAX>>());   
        _buckets_chksum.resize(TABLE_NUM, vector<uint32_t>());
        _key_hash_chksum = new BOBHash32(uint32_t(_rd() % MAX_PRIME32));
        _key_hashes.resize(TABLE_NUM, nullptr);
        _w.resize(TABLE_NUM, 0);
        for(int i=0; i<TABLE_NUM; ++i){
            _key_hashes[i] = new BOBHash32(uint32_t(_rd() % MAX_PRIME32)); 
            _w[i] = partitions * pow(2, TABLE_NUM-i-1);
            _buckets_tables[i].resize(_w[i], 0);
            _buckets_chksum[i].resize(_w[i], 0);
            HOW_LOG(L_INFO, "Allocate w_%d: %d", i, _w[i]);
        }
        _qid_allocator = 0;
        HOW_LOG(L_INFO, "Allocate %u bytes for beaucoup.", total_mem);
    }
    ~BeauCoup(){
        for(int i=0; i<TABLE_NUM; ++i)
            delete _key_hashes[i];
        delete _key_hash_chksum;
        for(auto& item : _attr_hashes)
            delete item.second;
        _attr_hashes.clear();
    }
    
    void register_attr_table(uint32_t attr_field_id){
        _attr_tables.insert(make_pair(attr_field_id, map<bitmask_t, coupon_t<COUPON_NUM_MAX>>()));
        _attr_hashes.insert(make_pair(attr_field_id,  new BOBHash32(uint32_t(_rd() % MAX_PRIME32))));
    }

    // return qid
    int register_query(uint32_t key_field_id, uint32_t attr_field_id){
        ++_qid_allocator;
        _qurey_info.insert(make_pair(_qid_allocator, query_t(_qid_allocator, key_field_id, attr_field_id)));
        return _qid_allocator;
    }
    
    int register_query_coupon(int qid, const string& coins, uint32_t coupon_id){
        uint32_t key_field_id = _qurey_info[qid].key_id;
        uint32_t attr_field_id = _qurey_info[qid].attr_id;
        bitmask_t match(coins);
        coupon_t<COUPON_NUM_MAX>  coupon1(qid, coupon_id);
        _attr_tables[attr_field_id].insert(make_pair(match, coupon1));
        _qurey_info[qid].coupon_num += 1;
    }

    int match_attrbutes(TracePacket* hdr, coupon_t<COUPON_NUM_MAX>& coupon){
        vector<coupon_t<COUPON_NUM_MAX>> matched_qcoupon;
        for(auto& table : _attr_tables){
            uint32_t attr_id = table.first;
            pair<const uint8_t*, uint32_t> hdr_attr; 
            hdr->readFeld(attr_id, hdr_attr);
            uint32_t attr_hash = _attr_hashes[attr_id]->run((char*)hdr_attr.first, hdr_attr.second); // get hash value.
            // generate a wrong hash?
            for(auto& rule : table.second){
                if(rule.first.match(attr_hash))  //select coupon.
                {
                    matched_qcoupon.push_back(rule.second);
                    break;
                } 
            }
        }
        if(matched_qcoupon.size() == 0)
            return -1;
        else{
            int idx = rand() % matched_qcoupon.size();
            coupon = matched_qcoupon[idx];
            return 0;
        }
    }
    // return: 1 if meet the threshold.
    // else return 0.
    int apply(TracePacket* hdr){
        coupon_t<COUPON_NUM_MAX> coupon;
        int re = match_attrbutes(hdr, coupon);
        if(re == 0){
            int query_id = coupon.query_id;
            bitset<COUPON_NUM_MAX> coupon_id = coupon.coupon_idx;
            uint32_t key_field_id = _qurey_info[query_id].key_id;
            pair<const uint8_t*, uint32_t> hdr_key; 
            hdr->readFeld(key_field_id, hdr_key);
            uint32_t key_hash_chksum = _key_hash_chksum->run((char*)hdr_key.first, hdr_key.second);
            for(int i=0; i<TABLE_NUM; ++i){
                uint32_t key_hash = _key_hashes[i]->run((char*)hdr_key.first, hdr_key.second) % _w[i];
                if(_buckets_chksum[i][key_hash] == key_hash_chksum 
                    || _buckets_chksum[i][key_hash] == 0 ) { // set 10 second as timeout.
                    _buckets_tables[i][key_hash] |= coupon_id;   // SET THE COUPON
                    _buckets_chksum[i][key_hash] = key_hash_chksum;   // SET THE COUPON
                    uint32_t coupon_num = count_coupon(_buckets_tables[i][key_hash]);
                    if(coupon_num == _qurey_info[query_id].coupon_num) {
                        return 1;
                    }
                    return 0;
                }
                // Hash collision.
                // Check next table.
            }
            return 0;
        }
    }
private:
    
    map<uint32_t, map<bitmask_t, coupon_t<COUPON_NUM_MAX>>>  _attr_tables;    // attr_id-> <attr_wildcard_hash-> qid>.
    
    map<int, query_t> _qurey_info;     // qid -> (key_field_id, attr_field_id)
    int _qid_allocator;

    random_device _rd;
    vector<BOBHash32*> _key_hashes;
    BOBHash32* _key_hash_chksum;
    map<uint32_t, BOBHash32 *>  _attr_hashes;    // attr_id-> <attr_wildcard_hash-> qid>.

    vector<uint32_t> _w;
    vector<vector<bitset<COUPON_NUM_MAX>>> _buckets_tables;
    vector<vector<uint32_t>>               _buckets_chksum;

    uint32_t count_coupon(const bitset<COUPON_NUM_MAX>& coupon){
        uint32_t coupon_num = 0;
        // while (coupon.to_ulong()) {
        //     coupon_num++ ;
        //     coupon &= (coupon - 1) ;
        // }
        for(uint32_t i=0; i<COUPON_NUM_MAX; ++i){
            if(coupon.test(i) == true){
                coupon_num += 1;
            }
        }
        return coupon_num;
    }
};

#endif