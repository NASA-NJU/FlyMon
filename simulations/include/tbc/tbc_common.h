#ifndef _TBC_COMMON_H_
#define _TBC_COMMON_H_

#define TABLE_KEY_INIT 0
#define TABLE_VAL_INIT 1
#define TABLE_PARAM_INIT 2
#define TABLE_KEY_MAPPING 3
#define TABLE_VAL_PROCESS 4
#define TABLE_OP_SELECT 5

#define ACTION_SET_KEY_IPPAIR   10
#define ACTION_SET_KEY_IPSRC    11
#define ACTION_SET_KEY_IPDST    12

#define ACTION_SET_VAL_CONST    20
#define ACTION_SET_VAL_IPPAIR_HASH   24
#define ACTION_SET_VAL_IPSRC_HASH    25
#define ACTION_SET_VAL_IPDST_HASH    26
#define ACTION_SET_VAL_TIMESTAMP     27

#define ACTION_SET_PARAM_CONST  30
#define ACTION_SET_PARAM_RESULT 31
#define ACTION_SET_PARAM_IPSRC  32
#define ACTION_SET_PARAM_IPPAIR  33
#define ACTION_SET_PARAM_TIMESTAMP  34


#define ACTION_SET_KEY_MAPPING_1          40
#define ACTION_SET_KEY_MAPPING_2          41
#define ACTION_SET_KEY_MAPPING_4          42
#define ACTION_SET_KEY_MAPPING_8          43
#define ACTION_SET_KEY_MAPPING_16         44
#define ACTION_SET_KEY_MAPPING_32         45
#define ACTION_SET_KEY_MAPPING_64         46
#define ACTION_SET_KEY_MAPPING_128        47


#define MEMROY_PARTITION  128
#define MAX_COIN_NUM    7  
// BUT MAX LEVEL NUM IS 8
#define MEMORY_1     ACTION_SET_KEY_MAPPING_1
#define MEMORY_2     ACTION_SET_KEY_MAPPING_2
#define MEMORY_4     ACTION_SET_KEY_MAPPING_4
#define MEMORY_8     ACTION_SET_KEY_MAPPING_8
#define MEMORY_16    ACTION_SET_KEY_MAPPING_16
#define MEMORY_32    ACTION_SET_KEY_MAPPING_32
#define MEMORY_64    ACTION_SET_KEY_MAPPING_64
#define MEMORY_128   ACTION_SET_KEY_MAPPING_128


#define ACTION_VAL_NO_ACTION      51
#define ACTION_VAL_SUB_RESULT     52
#define ACTION_VAL_ONE_HOT        53

#define ACTION_OP_CMP_ADD  60
#define ACTION_OP_MAX      61
#define ACTION_OP_SET      62
#define ACTION_OP_AND      63
#define ACTION_OP_OR       64
#define ACTION_OP_RANGE_COUNT  65

#define MEM_MODE_ACCURATE   0
#define MEM_MODE_EFFICIENT  1

#define COINS_DEAULT -1

#include <algorithm>
#include <cmath>

template<class T>
class BinaryTree{
private:
    int _level_num;
    vector<T>  _nodes;
public:
    BinaryTree(int level_num=5){
        _level_num = level_num;
        _nodes.resize(int(pow(2,_level_num))-1);
    }
    ~BinaryTree(){

    }
    void resize(int level_num=5){
        _level_num = level_num;
        _nodes.resize(int(pow(2,_level_num))-1);
    }
    void to_string()const{
        cout << "Current Status : "<<endl;
        for(int i=0; i<_level_num; ++i){
            for(int j=0; j< get_level_nodes_num(i); ++j){
                cout << read_by_level(i, j) <<" ";
            }
            cout << endl;
        }
    }
    T   read_by_idx(int idx){
        if(idx >= _nodes.size()){
            cout <<"Invalid idx"<<idx<<endl;
            exit(1);
        }
        return _nodes[idx];
    }
    T   write_by_idx(int idx, const T& value){
        if(idx >= _nodes.size()){
            cout <<"Invalid idx"<<idx<<endl;
            exit(1);
        }
        _nodes[idx] = value;
    }
    int get_level_num() const{
        return _level_num;
    }
    int get_level_nodes_num(int level) const{
        return int(pow(2,level));
    }
    int get_level_by_idx(int idx){
        return int(log2(idx+1));
    }
    int get_level_offset_by_idx(int idx) const{
        int level = get_level_by_idx(idx);
        return idx - (int(pow(2,level))-1);
    }
    int get_idx_by_level(int level, int offset) const{
        return int(pow(2,level))-1 + offset;
    }
    T read_by_level(int level, int offset) const{  // level = 0, 1, 2, 3.
        if(offset >= get_level_nodes_num(level)){
            // HOW_LOG(L_ERROR, "Invalid level idx.");
            cout <<"Invalid level offset"<<endl;
            exit(1);
        }
        return _nodes[int(pow(2,level))-1 + offset];
    }

    int locate_first_value(const T& value, int& level, int& offset){
        for(int i=0; i<_level_num; ++i){
            for(int j=0; j< get_level_nodes_num(i); ++j){
                if(read_by_level(i, j) == value){
                    level = i;
                    offset = j;
                    return 0;
                }
            }
        }
        return -1;
    }

    bool isAncestors(int upper_level, int uhpper_offset, int lower_level, int lower_offset){
        int upper_idx = get_idx_by_level(upper_level, uhpper_offset);
        int father_idx = get_father_idx(lower_level, lower_offset);
        while(father_idx != -1){
            if(upper_idx == father_idx){
                return true;
            }
            father_idx = get_father_idx(father_idx);
        }
        return false;
    }
    void get_all_leafs(int level, int offset, vector<T>& leafs){
        int last_level = _level_num -1;
        if(level == last_level){
            leafs.push_back(read_by_level(level, offset));
            return;
        }
        for(int last_offset=0; last_offset<get_level_nodes_num(last_level); ++last_offset){
            if(isAncestors(level, offset, last_level, last_offset)){
                leafs.push_back(read_by_level(last_level, last_offset));
            }
        }
    }
    void write_by_level(int level, int offset, const T& value){
        if(offset >= get_level_nodes_num(level)){
            // HOW_LOG(L_ERROR, "Invalid level idx.");
            cout <<"Invalid level offset"<<endl;
            exit(1);
        }
        _nodes[int(pow(2,level))-1 + offset] = value;
    }

    void populate_by_level(int level, int offset, const T& value){
        write_by_level(level, offset, value);
        int father_idx = get_father_idx(level, offset);
        while(father_idx != -1){
            write_by_idx(father_idx, value);
            father_idx = get_father_idx(father_idx);
        }
        populate_sons(get_idx_by_level(level, offset), value);
    }

    void populate_sons(int idx, const T& value){
        int left_child_idx = get_left_child_idx(idx);
        int right_child_idx = get_right_child_idx(idx);
        if(left_child_idx != -1 && right_child_idx != -1){
            write_by_idx(left_child_idx, value);
            write_by_idx(right_child_idx, value);
            populate_sons(left_child_idx, value);
            populate_sons(right_child_idx, value);
        }
    }

    int get_father_idx(int level, int offset){
        int phy_id = int(pow(2,level))-1 + offset;
        if(phy_id == 0){
            // HOW_LOG(L_ERROR, "No Father");
            // cout <<"No Father"<<endl;
            return -1;
        }
        return (phy_id-1)/2;
    }
    int get_father_idx(int idx){
        if(idx == 0){
            // HOW_LOG(L_ERROR, "No Father");
            // cout <<"No Father"<<endl;
            return -1;
        }
        return (idx-1)/2;
    }
    int get_left_child_idx(int level, int offset){
        int phy_id = int(pow(2,level))-1 + offset;
        if(level >= _level_num-1){
            // HOW_LOG(L_ERROR, "No Father");
            // cout <<"No Child"<<endl;
            return -1;
        }
        return phy_id*2 + 1;
    }
    int get_left_child_idx(int idx){
        if(get_level_by_idx(idx) >= _level_num-1) {
            // cout <<"No Child"<<endl;
            return -1;
        }
        return idx*2 + 1;
    }
    int get_right_child_idx(int level, int idx){
        int phy_id = int(pow(2,level))-1 + idx;
        if(level >= _level_num-1){
            // HOW_LOG(L_ERROR, "No Father");
            // cout <<"No Child"<<endl;
            return -1;
        }
        return phy_id*2 + 2;
    }
    int get_right_child_idx(int idx){
        if(get_level_by_idx(idx) >= _level_num-1) {
            // cout <<"No Child"<<endl;
            return -1;
        }
        return idx*2 + 2;
    }
};


#endif