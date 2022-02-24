#ifndef _TBC_RESOURCE_MANAGER_H_
#define _TBC_RESOURCE_MANAGER_H_

#include "tbc/tbc.h"
#include "tbc/tbc_common.h"
#include <map>
#include <string>
#include <iostream>
#include <vector>
#include <bitset>
using namespace std;


class TBC_Resource_Manager{ // Transformable Block Chain
private: 
    int _block_num;
    vector<BinaryTree<int>>             _coins_tasks; 
    vector<BinaryTree<int>>             _memory_tasks;  
    vector<BinaryTree<string>>          _coins;  
    vector<BinaryTree<pair<int, int>>>  _memory;   // <type, idx>
public:

    int get_block_num()const {
        return _block_num;
    }
    vector<int> check_coins(uint32_t block_id, uint32_t coin_level) {
        if(coin_level > MAX_COIN_NUM){
            return vector<int>();
        }
        vector<int> avalible_coins_idx;
        for(int j=0; j<_coins[block_id].get_level_nodes_num(coin_level); ++j){
            int status = _coins_tasks[block_id].read_by_level(coin_level, j);
            if(status == 0){
                avalible_coins_idx.push_back(j);
            }
        }
        return avalible_coins_idx;
    }
    int check_memory(uint32_t block_id, uint32_t memory_level) {
        if(memory_level > MAX_COIN_NUM){
            return -1;
        }
        for(int j=0; j<_memory[block_id].get_level_nodes_num(memory_level); ++j){
            int status = _memory_tasks[block_id].read_by_level(memory_level, j);
            if(status == 0){
                return j;
            }
        }
        return -1;
    }

    string acllocate_coins(uint32_t block_id, uint32_t level, uint32_t index, uint32_t task_id){
        _coins_tasks[block_id].populate_by_level(level, index, task_id);
        return _coins[block_id].read_by_level(level, index);
    }

    pair<int, int> acllocate_memory(uint32_t block_id, uint32_t level, uint32_t index, uint32_t task_id){
        _memory_tasks[block_id].populate_by_level(level, index, task_id);
        return _memory[block_id].read_by_level(level, index);
    }
    
    void get_possible_coins(const string& coins, vector<string>& coin_list){
        int level, offset;
        int re = _coins[0].locate_first_value(coins, level, offset);
        if(re == -1){
            cout <<"Invalid coins "<< coins << endl;
            return;
        }
        _coins[0].get_all_leafs(level, offset, coin_list);
    }

    string read_coins(uint32_t block_id, uint32_t level, uint32_t index){
        return _coins[block_id].read_by_level(level, index);
    }
    
    uint32_t memory_type(uint32_t level){
        uint32_t type = 0;
        switch(level){
            case 0:
                type = MEMORY_1;
                break;
            case 1:
                type = MEMORY_2;
                break;
            case 2:
                type = MEMORY_4;
                break;
            case 3:
                type = MEMORY_8;
                break;
            case 4:
                type = MEMORY_16;
                break;
            case 5:
                type = MEMORY_32;
                break;
            case 6:
                type = MEMORY_64;
                break;
            case 7:
                type = MEMORY_128;
                break;
        }
        return type;
    }
    TBC_Resource_Manager(int block_num, int level_num)
    {
        _block_num = block_num;
        _coins.resize(block_num);
        _coins_tasks.resize(block_num);
        _memory.resize(block_num);
        _memory_tasks.resize(block_num);
        for(int i=0; i<block_num; ++i) {
            auto& coin_tree = _coins[i];
            auto& memory_tree = _memory[i];
            auto& coin_task_tree = _coins_tasks[i];
            auto& memory_task_tree = _memory_tasks[i];
            coin_tree.resize(level_num);
            memory_tree.resize(level_num);
            coin_task_tree.resize(level_num);
            memory_task_tree.resize(level_num);
            coin_task_tree.populate_by_level(0,0,0);
            memory_task_tree.populate_by_level(0,0,0);
            if(level_num > 0){
                coin_tree.write_by_level(0, 0, "*******");
                memory_tree.write_by_level(0, 0, make_pair(memory_type(0), 0));
            }
            if(level_num > 1){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 1));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<1> bits_str(i);
                    string left_stars(MAX_COIN_NUM-1, '*');
                    coin_tree.write_by_level(1, i, bits_str.to_string() + left_stars);
                    memory_tree.write_by_level(1, i, make_pair(memory_type(1), i)); 
                }
            }
            if(level_num > 2){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 2));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<2> bits_str(i);
                    string left_stars(MAX_COIN_NUM-2, '*');
                    coin_tree.write_by_level(2, i, bits_str.to_string() + left_stars);
                    memory_tree.write_by_level(2, i, make_pair(memory_type(2), i)); 
                }
            }
            if(level_num > 3){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 3));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<3> bits_str(i);
                    string left_stars(MAX_COIN_NUM-3, '*');
                    coin_tree.write_by_level(3, i, bits_str.to_string() + left_stars);
                    memory_tree.write_by_level(3, i, make_pair(memory_type(3), i)); 
                }
            }
            if(level_num > 4){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 4));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<4> bits_str(i);
                    string left_stars(MAX_COIN_NUM-4, '*');
                    coin_tree.write_by_level(4, i, bits_str.to_string() + left_stars);
                    memory_tree.write_by_level(4, i, make_pair(memory_type(4), i)); 
                }
            }
            if(level_num > 5){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 5));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<5> bits_str(i);
                    string left_stars(MAX_COIN_NUM-5, '*');
                    coin_tree.write_by_level(5, i, bits_str.to_string() + left_stars);
                    memory_tree.write_by_level(5, i, make_pair(memory_type(5), i)); 
                }
            }
            if(level_num > 6){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 6));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<6> bits_str(i);
                    string left_stars(MAX_COIN_NUM-6, '*');
                    coin_tree.write_by_level(6, i, bits_str.to_string() + left_stars);
                    memory_tree.write_by_level(6, i, make_pair(memory_type(6), i)); 
                }
            }
            if(level_num > 7){
                uint32_t coin_num = static_cast<uint32_t>(pow(2, 7));
                for(uint32_t i = 0; i<coin_num; ++i){
                    bitset<7> bits_str(i);
                    coin_tree.write_by_level(7, i, bits_str.to_string());
                    memory_tree.write_by_level(7, i, make_pair(memory_type(7), i)); 
                }
            }
        }
    }
};
#endif
