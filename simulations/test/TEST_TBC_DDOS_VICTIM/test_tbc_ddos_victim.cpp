
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include "EMFSD.h"
#include "CommonFunc.h"
#include <fstream>
#include <ctime>
#include <bitset>
#include "Csver.h"
#include <any>

// #define FILE_MRAC_DSITRIBUTION "flow_distribution0.02.txt"  //1MB
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 5;
const uint32_t SUB_BLOCK_NUM = 16;

const uint32_t hll_block_num = 3;
const uint32_t hll_sub_block_num = 64;
const uint32_t hll_block_size = 51200;  // 87386 * 4 * 3 = 1MB.

const int coin_level_hll = 0 ; // 1/2
const int coff_hll = 1; // 1/2

const uint32_t DDoS_Threshold = 128;

const uint32_t BLOCK_SIZE = hll_block_size;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

double calc_alpha(const vector<double>& dist, double coff){
    if(coff == 1){
        return 1;
    }
    double alpha = 0.0;
    double s = 1/coff;
    double total_size = 0;
    for(auto& x : dist) total_size += x;
    for(uint32_t i=0; i<dist.size(); ++i){
        uint32_t n = i;
        double p = dist[i] / total_size;
        alpha += p * (1-pow((1-s), n));
    } 
    return alpha;
}

uint16_t get_max(const unordered_map<string, int>& data){
    uint16_t max = 0;
    for(auto& item : data){
        if(item.second > max) 
        {
            max = item.second;
        }
    }
    return max;
}

uint16_t count_mid( Manager& manager,
                    int task_id,
                    map<uint16_t, map<uint16_t, vector<uint16_t>>>& sketch,
                    const uint8_t* key,
                    int key_len)
{
    uint32_t sub_block_size = hll_block_size / hll_sub_block_num;
    vector<uint16_t> value_list;
    for(auto& tbc : sketch){ // tbc, block, coin, data.
        uint32_t tbc_id = tbc.first;
        uint32_t value = 0;
        for(auto& block : tbc.second){
            vector<uint16_t> single_block_re;
            uint32_t block_id = block.first;
            // cout <<"===================== Block " << block_id<<endl;
            // BOBHash32* hash_func = manager.get_hash_func(tbc_id, block_id);
            BOBHash32* hash_func = manager.get_hash_func(tbc_id);
            uint32_t hash_value = hash_func->run((const char*)key, key_len);
            uint32_t address = ( (hash_value & (0xfffff << 4*block_id)) >> (4*block_id) ) % hll_block_size;
            for(auto i=0; i<hll_sub_block_num; ++i){
                uint32_t real_address = address >> 5;  //16
                real_address += i * (hll_block_size/hll_sub_block_num);
                // cout <<"real address " <<real_address<<endl;
                single_block_re.push_back(block.second[real_address]);
                // cout <<"real address value " <<block.second[real_address]<<endl;
            }
            value_list.push_back(HyperLogLogCalc(single_block_re));
        }
    }
    sort(value_list.begin(), value_list.end());
    return static_cast<uint16_t>(value_list[0]);
}


void recover_distribution_iter_uponmultiple_involve0(vector<double>& distribution, double in_coff, int iter_num);

double measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("outputs_30/ddosvictims_new/ddosvictim_tmu_hll_3d_64m.csv");
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int hll_task = tbc_manager.allocate_multi_hll_new(hll_block_num, hll_sub_block_num, filter, ACTION_SET_KEY_IPDST, ACTION_SET_VAL_IPSRC_HASH, coin_level_hll);
    if(hll_task< 0) {
        return -1;
    }
    unordered_map<string, vector<string>> ground_truth;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string ipdst((const char*)((*it)->getDstBytes()), 4);
        string ipsrc((const char*)((*it)->getSrcBytes()), 4);
        if(find(ground_truth[ipdst].begin(), ground_truth[ipdst].end(), ipsrc) == ground_truth[ipdst].end()){
            ground_truth[ipdst].push_back(ipsrc);
        }
    }
    map<uint16_t, map<uint16_t, vector<uint16_t>>> hll_sketch;
    unordered_map<string, int> hll_task_gt;
    tbc_manager.query(hll_task, hll_sketch);
    // tbc_manager.getTaskStatistics(hll_task, hll_task_gt);
    // vector<double> gt_smp_distribution;  // sample distribution from mrac.
    // gt_smp_distribution.resize(get_max(hll_task_gt)+1, 0);
    // for(auto& flow : hll_task_gt){
    //     gt_smp_distribution[flow.second] += 1;
    // }
    // recover_distribution_iter_uponmultiple_involve0(gt_smp_distribution, coff_hll, 2);
    // double alpha = calc_alpha(gt_smp_distribution, coff_hll);
    vector<string> real_ddos;
    vector<string> esti_ddos;
    for(auto& ipdst : ground_truth){
        uint16_t src_num = ipdst.second.size();
        // uint32_t estimate = static_cast<uint32_t>(count_mid(tbc_manager, hll_task, hll_sketch, (const uint8_t *)ipdst.first.c_str(), 4) / alpha);
        uint16_t estimate = static_cast<uint16_t>(count_mid(tbc_manager, hll_task, hll_sketch, (const uint8_t *)ipdst.first.c_str(), 4));
        // uint32_t estimate = count_mid(tbc_manager, hll_task, hll_sketch, (const uint8_t *)ipdst.first.c_str(), 4);
        if(src_num >= DDoS_Threshold) real_ddos.push_back(TracePacket::bytes_to_ip_str((uint8_t*)ipdst.first.c_str()));
        if(estimate >= DDoS_Threshold) esti_ddos.push_back(TracePacket::bytes_to_ip_str((uint8_t*)ipdst.first.c_str()));
        // HOW_LOG(L_DEBUG, "Flow real-src num %u, estimate num %u.", src_num, estimate);
        // if(src_num > 1000){
        //     HOW_LOG(L_DEBUG, "Dst IP %s, Flow real-src num %u, estimate num %u.", TracePacket::bytes_to_ip_str((uint8_t*)ipdst.first.c_str()).c_str(), src_num, estimate);
        // }
    }
    // HOW_LOG(L_DEBUG, "Real DDoS victims: ");
    // for(auto& real : real_ddos){
    //     HOW_LOG(L_DEBUG, "%s", real.c_str());
    // }
    // HOW_LOG(L_DEBUG, "Estimate DDoS victims: ");
    // for(auto& esti : esti_ddos){
    //     HOW_LOG(L_DEBUG, "%s", esti.c_str());
    // }
    uint16_t estimate_right = 0;
    for(uint32_t i = 0; i < real_ddos.size(); ++i)
    {
        for(uint32_t j = 0; j < esti_ddos.size(); ++j)
        {   
            if(real_ddos[i] == esti_ddos[j]){
                estimate_right += 1;
                break;
            }
        }
    }
    double precision =  (double)estimate_right / (double)esti_ddos.size();
    double recall = (double)estimate_right / (double)real_ddos.size();
    double f1 = (2 * precision * recall) / (precision + recall);
    HOW_LOG(L_INFO, "[Result] MultiHll %d KB, Estimate precision %.2f, recall %.2f, f1 %.2f", 300, precision, recall, f1);
    csver.write(300, 3, 64, precision, recall, f1);
    delete filter;
    return 0;
}


int main(int argc, char* argv[]){
    LOG_LEVEL = L_DEBUG;
    clock_t start = clock();
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    trace.LoadFromFile("/home/hzheng/workSpace/SketchLab/data/WIDE/thirty_sec_0.dat");
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}


long permutationsC(int a, int b){
    // sorry for the func num
    return tgamma(a+1) / (tgamma(b+1)*tgamma(a-b));
}


void recover_distribution_iter_uponmultiple_involve0(vector<double>& distribution, double in_coff, int iter_num){
    if(in_coff == 1)
        return;
    // flows has pkts bigger than the upper bound will not included in the iteration
    const int upperbound = 10;
    const int sample_coefficient = static_cast<uint32_t>(in_coff);
    // good-turing, here we just use it as a initial value
    distribution[0] = 1;
    // the recovered distribution
    vector<double> new_distribution(distribution.size() * sample_coefficient, 0);
    // the distribution involed in the iterations
    vector<double> iter_distribution(upperbound * sample_coefficient, 0);
    // the flows aren't included in the iteration
    // vector<pair<int, double>> bigger_flows();
    // the probability of flow containing n pkt being sampled as i pkt flow
    vector<vector<double>> probability_n_i(upperbound * sample_coefficient, vector<double>(upperbound));  
    double s = 1/in_coff;  // sample rate
    long total_flow_num = 0;  // the total number of flows in the sample set
    long iter_flow_num = 0;  // the number of flows in iterations
    vector<double> factorial(upperbound * sample_coefficient, 0);
    
    // calc factorial
    factorial[0] = 1;
    for(int i = 1; i < upperbound * sample_coefficient; i++){
        factorial[i] = factorial[i-1] * i;
    }
     
    // calc p_n_i
    for(int n = 0; n < upperbound * sample_coefficient; n++){
        for(int i = 0; i < upperbound && i <= n; i++){
            // note that n and i here is the same meaning as in the formula
            probability_n_i[n][i] = pow(s, i) * pow(1-s, n-i) * factorial[n] / (factorial[i]*factorial[n-i]);
        }
    }
    // build the initial distribution by multiple
    for(int i = 0; i < upperbound; ++i){
        // number of even numbers in the gap of the sample_coefficient
        const int even_num = sample_coefficient/2;
        for(int j = 0; j < even_num; j++){
            iter_distribution[i*sample_coefficient + j*2] += distribution[i] / even_num; 
        }
    }
    iter_distribution[0] = 100; // ZERO RECOVER
          
    // calc the new distribution
    for (int __i = 0; __i < iter_num; __i++){
        // note that __i is a var that we don't want it to be used in anywhere
        // the fraction of i pkt flow in sample set
        // becaues the origin distribution is modified in each iteration, we recalc it in every iteration
        total_flow_num = 0;
        iter_flow_num = 0;
        vector<double> fraction_i(upperbound, 0);
        // the probability of i pkt flow in sample set represent n pkt flow in real set
        vector<vector<double>> probability_i_n(upperbound, vector<double>(upperbound * sample_coefficient)); 
        // double probability_i_n[100][200];
        // the total probability of i pkt flow in sample set
        vector<double> probability_i(upperbound, 0);

        // calc X_i and flow_number
        for(int i = 0; i < upperbound; i++){
            total_flow_num += distribution[i];
            iter_flow_num += distribution[i];
        }
        for(int i = upperbound; i < distribution.size(); i++){
            total_flow_num += distribution[i];
        }
        for(int i = 0; i < upperbound; i++){
            fraction_i[i] = distribution[i] / iter_flow_num;
        }
         
        // calc p_i
        for(int i = 0; i < upperbound; i++){
            for(int n = i; n < upperbound * sample_coefficient; n++){
                // note that n and i here is the same meaning as in the formula
                probability_i[i] += iter_distribution[n] * probability_n_i[n][i];
            }
        }
         
        // calc p_i_n
        for(int i = 0; i < upperbound; i++){
            for(int n = i; n < upperbound * sample_coefficient; n++){
                // note that n and i here is the same meaning as in the formula
                probability_i_n[i][n] = iter_distribution[n] * probability_n_i[n][i] / probability_i[i];
            }
        }
        // calc the new distribution
        for(int n = 0; n < upperbound * sample_coefficient; n++){
            double local_n_distribution = 0.0;
            for(int i = 0; i < upperbound && i <= n; i++){
                local_n_distribution += probability_i_n[i][n] * fraction_i[i];
            }
            iter_distribution[n] = local_n_distribution;
        }
         
        // note that we assume the biggest flow in the real set is twice bigger than the biggest flow in sample set
        double local_total_distribution = 0.0;
        for(int n = 0; n < upperbound * sample_coefficient; n++){
            local_total_distribution += iter_distribution[n];
        }
        // cout << local_total_distribution << endl;
        // HOW_LOG(L_INFO, "total distribution before correct: %.2f", local_total_distribution);
        iter_distribution[upperbound * sample_coefficient - 1] += 1-local_total_distribution;
        // modify the value of 0
        // frist calc p0
        double p0 = 0.0;
        for(int n = 0; n < upperbound * sample_coefficient; n++){
            p0 += iter_distribution[n] * probability_n_i[n][0];
        }
        distribution[0] = (iter_flow_num - distribution[0]) * (p0) / (1-p0);
    }
     
    // the sum of first upperbound flow's distribution is 1
    // so we should scale them to the original proportion
    for(int i = 0; i < upperbound * sample_coefficient; i++){
        new_distribution[i] = iter_distribution[i] * iter_flow_num / total_flow_num;
    }
    // the other flows will be multiple by sample_coefficient
    for(int i = upperbound; i < distribution.size(); i++){
        new_distribution[i*sample_coefficient] = distribution[i];
    }
    for(int i = 0; i < upperbound * sample_coefficient; i++){
        new_distribution[i] *= total_flow_num;
    }
    // distribution.clear();
    // distribution = std::move(new_distribution);
    distribution = new_distribution;
}