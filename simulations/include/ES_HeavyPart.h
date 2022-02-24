# ifndef __ES_HEAVY_PART_H_
# define __ES_HEAVY_PART_H_

#include "ES_Params.h"

#define KEY_TYPE uint64_t

struct Bucket
{
	KEY_TYPE key[COUNTER_PER_BUCKET];   //可不可以是变长flow key
	uint32_t val[COUNTER_PER_BUCKET];
};

template<int bucket_num>
class HeavyPart
{
    // alignas(64) Bucket buckets[bucket_num];
public:
    HeavyPart();
    ~HeavyPart();

    void clear();

    int insert(const uint8_t *key, uint8_t *swap_key, uint32_t &swap_val, uint32_t f = 1);

    int query(const uint8_t *key);

    int get_memory_usage();
    int get_bucket_num();
	Bucket buckets[bucket_num];
private:
    int CalculateFP(const uint8_t *key, KEY_TYPE &fp);
};

template<int bucket_num>
HeavyPart<bucket_num>::HeavyPart()
{
    this->clear();
}

template<int bucket_num>
HeavyPart<bucket_num>::~HeavyPart(){}

template<int bucket_num>
void HeavyPart<bucket_num>::clear()
{
    memset(buckets, 0, sizeof(Bucket) * bucket_num);
}

template<int bucket_num>
int HeavyPart<bucket_num>::insert(const uint8_t *key, uint8_t *swap_key, uint32_t &swap_val, uint32_t f)
{
    // uint64_t fp;
	KEY_TYPE fp; //HERE
	// 将Flow pos, 相当于一个hash函数. 将 *key 映射到某一个筒, 同时fp 是fp将key转为 32 位的数
	int pos = CalculateFP(key, fp);

	/* find if there has matched bucket */
	int matched = -1, empty = -1, min_counter = 0;
	uint32_t min_counter_val = GetCounterVal(buckets[pos].val[0]);
	for(int i = 0; i < COUNTER_PER_BUCKET - 1; i++){
		if(buckets[pos].key[i] == fp){
			matched = i;
			break;
		}
		if(buckets[pos].key[i] == 0 && empty == -1)
			empty = i;
		if(min_counter_val > GetCounterVal(buckets[pos].val[i])){
			min_counter = i;
			min_counter_val = GetCounterVal(buckets[pos].val[i]);
		}
	}

	/* if matched */
	if(matched != -1){
		buckets[pos].val[matched] += f;
		return 0;
	}

	/* if there has empty bucket */
	if(empty != -1){
		buckets[pos].key[empty] = fp;
		buckets[pos].val[empty] = f;
		return 0;
	}

    /* update guard val and comparison */
    uint32_t guard_val = buckets[pos].val[MAX_VALID_COUNTER];
    guard_val = UPDATE_GUARD_VAL(guard_val);

    if(!JUDGE_IF_SWAP(GetCounterVal(min_counter_val), guard_val)){
        buckets[pos].val[MAX_VALID_COUNTER] = guard_val;
        return 2;
    }
	//HERE
	*((KEY_TYPE*)swap_key) = buckets[pos].key[min_counter];
    swap_val = buckets[pos].val[min_counter];

    buckets[pos].val[MAX_VALID_COUNTER] = 0;
    buckets[pos].key[min_counter] = fp;
    buckets[pos].val[min_counter] = 0x80000001;

    return 1;
}


template<int bucket_num>
int HeavyPart<bucket_num>::query(const uint8_t *key)
{
    // uint64_t fp;
	KEY_TYPE fp;
    int pos = CalculateFP(key, fp);

    for(int i = 0; i < MAX_VALID_COUNTER; ++i)
        if(buckets[pos].key[i] == fp)
            return buckets[pos].val[i];

    return 0;
}

template<int bucket_num>
int HeavyPart<bucket_num>::get_memory_usage()
{
    return bucket_num * sizeof(Bucket);
}

template<int bucket_num>
int HeavyPart<bucket_num>::get_bucket_num()
{
    return bucket_num;
}

// HERE 参数
template<int bucket_num>
int HeavyPart<bucket_num>::CalculateFP(const uint8_t *key, KEY_TYPE &fp) //HERE
{
	fp = *((KEY_TYPE*)key);
    // return CalculateBucketPos(fp) % bucket_num;
	return fp % bucket_num;
}
#endif