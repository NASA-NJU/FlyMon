
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include "EMFSD.h"
#include "CommonFunc.h"
#include <fstream>
#include <ctime>
#include <bitset>

// #define FILE_MRAC_DSITRIBUTION "flow_distribution0.02.txt"  //1MB
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 3;
const uint32_t SUB_BLOCK_NUM = 16;
const uint32_t m = 128000;
const int coin_level = 1; // 1/2
const double coff = 2;
const uint32_t BLOCK_SIZE = m * SUB_BLOCK_NUM;

using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

uint32_t get_max(const unordered_map<string, int>& data){
    uint32_t max = 0;
    for(auto& item : data){
        if(item.second > max) 
        {
            max = item.second;
        }
    }
    return max;
}

double calc_wmre(const vector<double>& gt_dist, const vector<double>& est_dist){
    uint32_t max_size = gt_dist.size() > est_dist.size() ? gt_dist.size()  : est_dist.size();
    double molecule = 0;
    double denominator = 0;
    for(int i=0; i<max_size; ++i){
        double gt_value = (i >= gt_dist.size())? 0 : gt_dist[i];
        double est_value = (i >= est_dist.size())? 0 : est_dist[i];
        molecule = molecule + abs(gt_value - est_value);
        denominator = denominator + (gt_value + est_value) / 2;
    }
    return molecule / denominator;
}

void recover_distribution_iter_uponmultiple_involve0(vector<double>& distribution, double in_coff, int iter_num);

double measure_main(DataTrace& trace, Manager& tbc_manager){
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int task_id = tbc_manager.allocate_cmsketch(1, m, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_CONST, coin_level);
    if(task_id < 0) {
        return -1;
    }
    unordered_map<string, int> Real_Freq;
    unordered_map<string, int> TBC_Gt;
    uint32_t max_size = 0;
    for (auto it=trace.begin(); it!=trace.end(); ++it){
        tbc_manager.apply(*it);
        string str((const char*)((*it)->getFlowKey_IPPair()), 8);
        Real_Freq[str]++;
    } 
    map<uint16_t, map<uint16_t, vector<uint16_t>>> sketch;
    tbc_manager.query(task_id, sketch);
    tbc_manager.getTaskStatistics(task_id, TBC_Gt);
    auto& mrac_data = sketch[0][0];
    vector<double> dist_groundtruth;
    vector<double> dist_sampled_zzc_0;  // sampled distribution always true.
    vector<double> dist_sampled_mrac;  // sample distribution from mrac.
    // get ground truth distribution.
    dist_groundtruth.resize(get_max(Real_Freq)+1, 0);
    for(auto& flow : Real_Freq){
        dist_groundtruth[flow.second] += 1;
    }
    // get dist sampled estimated.
    CalcDistribution(mrac_data, dist_sampled_mrac);
    dist_sampled_zzc_0.resize(get_max(TBC_Gt)+1, 0);
    for(auto& flow : TBC_Gt){
        dist_sampled_zzc_0[flow.second] += 1;  // get dist sampled ground truth.
    }
    double wmre_gt_wo_recover = calc_wmre(dist_groundtruth, dist_sampled_zzc_0);
    double wmre_mrac_wo_recover = calc_wmre(dist_groundtruth, dist_sampled_mrac);
    recover_distribution_iter_uponmultiple_involve0(dist_sampled_zzc_0, coff, 200000);
    recover_distribution_iter_uponmultiple_involve0(dist_sampled_mrac, coff, 200000);

    double wmre_gt_recover = calc_wmre(dist_groundtruth, dist_sampled_zzc_0);
    double wmre_mrac_recover = calc_wmre(dist_groundtruth, dist_sampled_mrac);
    HOW_LOG(L_INFO, "WMRE Gt w/o Recover %.2f, WMRE Gt Recover %.2f, WMRE MRAC w/o Recover %.2f, WMRE MRAC Recover %.2f", 
                     wmre_gt_wo_recover,
                     wmre_gt_recover, 
                     wmre_mrac_wo_recover,
                     wmre_mrac_recover);
    delete filter;
    return 0;
}


int main(int argc, char* argv[]){
    clock_t start = clock();
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    // trace.LoadFromFile("../data/WIDE/test.dat");
    // trace.LoadFromFile("../data/WIDE/ten_sec_1.dat");
    trace.LoadFromFile("../data/WIDE/fifteen1.dat");
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