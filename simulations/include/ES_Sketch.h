/************************************************************
 *  Reffer from https://github.com/BlockLiu/ElasticSketchCode.git
 *  Author : BlockLiu
 *  Modified : mmh
 * **********************************************************/

#ifndef _ELASTIC_SKETCH_H_
#define _ELASTIC_SKETCH_H_


#include "ES_Params.h"
#include "StreamAlgorithm.h"
#include "ES_HeavyPart.h"
#include "ES_LightPart.h"

// #include <x86intrin.h>


template<int bucket_num, int tot_memory_in_bytes>
class ElasticSketch : public StreamAlgorithm {

    static constexpr int heavy_mem = bucket_num * COUNTER_PER_BUCKET * 8;
    static constexpr int light_mem = tot_memory_in_bytes - heavy_mem;

    HeavyPart<bucket_num> heavy_part;
    LightPart<light_mem> light_part;
public:
    ElasticSketch( int key_len) : StreamAlgorithm(key_len, tot_memory_in_bytes)
    { 
    }
    ~ElasticSketch();
    virtual int insert(const uint8_t * key);
    virtual int query(const uint8_t * key);
    void clear();

    void get_flowsize(vector<string> &flowIDs, unordered_map<string,int> &freq);

private:

    int query_compressed_part(const uint8_t *key, uint8_t *compress_part, int compress_counter_num);

    int get_compress_width(int ratio);
    void compress(int ratio, uint8_t *dst);

    int get_bucket_num();
    double get_bandwidth(int compress_ratio) ;

    void get_heavy_hitters(int threshold, vector<pair<string, int>> & results);
    double get_cardinality();
    double get_entropy();
    void get_distribution(vector<double> &dist);

public:
    // void *operator new(size_t sz);
    // void operator delete(void *p);
};



template<int bucket_num, int tot_memory_in_bytes>
ElasticSketch<bucket_num, tot_memory_in_bytes>::~ElasticSketch(){}

template<int bucket_num, int tot_memory_in_bytes>
void ElasticSketch<bucket_num, tot_memory_in_bytes>::clear()
{
    INSERT_TIMES = 0;
    heavy_part.clear();
    light_part.clear();
}
template<int bucket_num, int tot_memory_in_bytes>
int ElasticSketch<bucket_num, tot_memory_in_bytes>::insert(const uint8_t * key)
{
    uint8_t* swap_key = new uint8_t[_key_len];
    uint32_t swap_val = 0;
    int result = heavy_part.insert(key, swap_key, swap_val, 1);
    switch(result)
    {
        case 0: break;
        case 1:{
            if(HIGHEST_BIT_IS_1(swap_val))
                light_part.insert(swap_key, _key_len, GetCounterVal(swap_val));
            else
                light_part.swap_insert(swap_key, _key_len,  swap_val);
            break;
        }
        case 2: light_part.insert(key, _key_len,  1);  break;
        default:
            printf("error return value !\n");
            exit(1);
    }
    return ++INSERT_TIMES;
}


template<int bucket_num, int tot_memory_in_bytes>
int ElasticSketch<bucket_num, tot_memory_in_bytes>::query(const uint8_t *key)
{
    uint32_t heavy_result = heavy_part.query(key);
    if(heavy_result == 0 || HIGHEST_BIT_IS_1(heavy_result))
    {
        int light_result = light_part.query(key, _key_len);
        return (int)GetCounterVal(heavy_result) + light_result;
    }
    return heavy_result;
}

// template<int bucket_num, int tot_memory_in_bytes>
// int ElasticSketch<bucket_num, tot_memory_in_bytes>::query(const uint8_t *key, int keylen)
// {
//     uint32_t heavy_result = heavy_part.query(key);
//     if(heavy_result == 0 || HIGHEST_BIT_IS_1(heavy_result))
//     {
//         int light_result = light_part.query(key);
//         return (int)GetCounterVal(heavy_result) + light_result;
//     }
//     return heavy_result;
// }

template<int bucket_num, int tot_memory_in_bytes>
int ElasticSketch<bucket_num, tot_memory_in_bytes>::query_compressed_part(const uint8_t *key, uint8_t *compress_part, int compress_counter_num)
{
    uint32_t heavy_result = heavy_part.query(key);
    if(heavy_result == 0 || HIGHEST_BIT_IS_1(heavy_result))
    {
        int light_result = light_part.query_compressed_part(key,  _key_len, compress_part, compress_counter_num);
        return (int)GetCounterVal(heavy_result) + light_result;
    }
    return heavy_result;
}

template<int bucket_num, int tot_memory_in_bytes>
int ElasticSketch<bucket_num, tot_memory_in_bytes>::get_compress_width(int ratio)
{
    return light_part.get_compress_width(ratio);
}

template<int bucket_num, int tot_memory_in_bytes>
void ElasticSketch<bucket_num, tot_memory_in_bytes>::compress(int ratio, uint8_t *dst)
{
    light_part.compress(ratio, dst);
}
    
template<int bucket_num, int tot_memory_in_bytes>
int ElasticSketch<bucket_num, tot_memory_in_bytes>::get_bucket_num(){
    return heavy_part.get_bucket_num();
}

template<int bucket_num, int tot_memory_in_bytes>
double ElasticSketch<bucket_num, tot_memory_in_bytes>::get_bandwidth(int compress_ratio) 
{
    int result = heavy_part.get_memory_usage();
    result += get_compress_width(compress_ratio) * sizeof(uint8_t);
    return result * 1.0 / 1024 / 1024;
}

template<int bucket_num, int tot_memory_in_bytes>
void ElasticSketch<bucket_num, tot_memory_in_bytes>::get_heavy_hitters(int threshold, vector<pair<string, int>> & results)
{
    for (int i = 0; i < bucket_num; ++i) 
        for (int j = 0; j < MAX_VALID_COUNTER; ++j) 
        {
            if(_key_len == 4){
                uint32_t key = heavy_part.buckets[i].key[j]; // HERE key
                // uint64_t key = heavy_part.buckets[i].key[j]; // HERE key
                int val = query((uint8_t *)&key);
                if (val >= threshold) {
                    // HERE 4--- 8
                    // results.push_back(make_pair(string((const char*)&key, 8), val));
                    results.push_back(make_pair(string((const char*)&key, 4), val));
                }               
            }else{
                uint64_t key = heavy_part.buckets[i].key[j]; // HERE key
                int val = query((uint8_t *)&key);
                if (val >= threshold) {
                    // HERE 4--- 8
                    // results.push_back(make_pair(string((const char*)&key, 8), val));
                    results.push_back(make_pair(string((const char*)&key, 8), val));
                }                  
            }
        }
}

template<int bucket_num, int tot_memory_in_bytes>
double ElasticSketch<bucket_num, tot_memory_in_bytes>::get_cardinality()
{
    int card = light_part.get_cardinality();
    for(int i = 0; i < bucket_num; ++i)
        for(int j = 0; j < MAX_VALID_COUNTER; ++j)
        {
            uint8_t* key= new uint8_t[_key_len];
            //HERE
            if (_key_len == 4){
                *(uint32_t*)key = heavy_part.buckets[i].key[j];
            }
            else{
                *(uint64_t*)key = heavy_part.buckets[i].key[j];
            }

            int val = heavy_part.buckets[i].val[j];
            int ex_val = light_part.query(key, _key_len);

            if(HIGHEST_BIT_IS_1(val) && ex_val)
            {
                val += ex_val;
                card--;
            }
            if(GetCounterVal(val))
                card++;
        }
        return card;
}

template<int bucket_num, int tot_memory_in_bytes>
double ElasticSketch<bucket_num, tot_memory_in_bytes>::get_entropy()
{
    int tot = 0;
    double entr = 0;

    light_part.get_entropy(tot, entr);

    for(int i = 0; i < bucket_num; ++i)
        for(int j = 0; j < MAX_VALID_COUNTER; ++j)
        {
            uint8_t* key = new uint8_t[_key_len];
            // HERE
            if(_key_len == 4){
                *(uint32_t*)key = heavy_part.buckets[i].key[j];
            }else{
                *(uint64_t*)key = heavy_part.buckets[i].key[j];
            }
            
            // *(uint64_t*)key = heavy_part.buckets[i].key[j];
            int val = heavy_part.buckets[i].val[j];

            int ex_val = light_part.query(key, _key_len);

            if(HIGHEST_BIT_IS_1(val) && ex_val)
            {
                val += ex_val;

                tot -= ex_val;

                entr -= ex_val * log2(ex_val);
            }
            val = GetCounterVal(val);
            if(val)
            {
                tot += val;
                entr += val * log2(val);
            }
        }
    return -entr / tot + log2(tot);
}

template<int bucket_num, int tot_memory_in_bytes>
void ElasticSketch<bucket_num, tot_memory_in_bytes>::get_distribution(vector<double> &dist)
{
    light_part.get_distribution(dist);

    for(int i = 0; i < bucket_num; ++i)
        for(int j = 0; j < MAX_VALID_COUNTER; ++j)
        {
            uint8_t* key = new uint8_t[_key_len];
            //HERE
            if( _key_len == 4 ){
                *(uint32_t*)key = heavy_part.buckets[i].key[j];
            }else{
                *(uint64_t*)key = heavy_part.buckets[i].key[j];
            }
            
            // *(uint64_t*)key = heavy_part.buckets[i].key[j];
            int val = heavy_part.buckets[i].val[j];

            int ex_val = light_part.query(key, _key_len);

            if(HIGHEST_BIT_IS_1(val) && ex_val != 0)
            {
                val += ex_val;
                dist[ex_val]--;
            }
            val = GetCounterVal(val);
            if(val)
            {
                if(val + 1 > dist.size())
                    dist.resize(val + 1);
                dist[val]++;
            }
        }
}

// template<int bucket_num, int tot_memory_in_bytes>
// void* ElasticSketch<bucket_num, tot_memory_in_bytes>::operator new(size_t sz)
// {
//     constexpr uint32_t alignment = 64;
//     size_t alloc_size = (2 * alignment + sz) / alignment * alignment;
//     void *ptr = ::operator new(alloc_size);
//     void *old_ptr = ptr;
//     void *new_ptr = ((char*)std::align(alignment, sz, ptr, alloc_size) + alignment);
//     ((void **)new_ptr)[-1] = old_ptr;

//     return new_ptr;
// }

// template<int bucket_num, int tot_memory_in_bytes>
// void ElasticSketch<bucket_num, tot_memory_in_bytes>::operator delete(void *p)
// {
//     ::operator delete(((void**)p)[-1]);
// }


template<int bucket_num, int tot_memory_in_bytes>
void ElasticSketch<bucket_num, tot_memory_in_bytes>::get_flowsize(vector<string> &flowIDs, unordered_map<string,int> &freq)
{
    freq.clear();
    for(auto flowid : flowIDs)
        freq[flowid] = this->query((uint8_t*)flowid.c_str());
}


#endif