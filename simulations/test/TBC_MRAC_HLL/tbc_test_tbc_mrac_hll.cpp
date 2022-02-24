
#include <unordered_map>
#include "tbc/tbc_manager.h"
#include "DataTrace.h"
#include "EMFSD.h"
#include "CommonFunc.h"
#include <fstream>
#include <ctime>
#include <bitset>
#include "Csver.h"


// #define FILE_MRAC_DSITRIBUTION "flow_distribution0.02.txt"  //1MB
const uint32_t TBC_NUM = 1;
const uint32_t BLOCK_NUM = 5;
const uint32_t SUB_BLOCK_NUM = 16;
const uint32_t m = 1024;  
const uint32_t n = 16384;
const int coin_level = 0; // 1/2
const double coff = 1;
const uint32_t BLOCK_SIZE = m * SUB_BLOCK_NUM;


using Manager = TBC_Manager<TBC_NUM, BLOCK_NUM, BLOCK_SIZE, SUB_BLOCK_NUM>;

double calc_alpha(const vector<double>& dist){
    if(coff == 1)  return 1;
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

long permutationsC(int a, int b){
    // sorry for the func num
    return tgamma(a+1) / (tgamma(b+1)*tgamma(a-b));
}


double gamma_1(vector<double>& distribution){
    double n = static_cast<double>(distribution.size());
    double C = 1-(distribution[1]/n);
    double D = 0;
    for(auto i=1; i<distribution.size(); ++i){
        D += distribution[i];
    }
    double N1 = D / C;
    double part1 = 0;
    for(auto i=1; i<distribution.size(); ++i){
        part1 += i * (i-1) * distribution[i];
    }
    part1 = part1 / (n * (n-1));
    double re = N1 * part1 -1;
    return  re > 0? re : 0;
}

double gamma_2(vector<double>& distribution){
    double n = static_cast<double>(distribution.size());
    double C = 1-(distribution[1]/n);
    double gamma = gamma_1(distribution);
    double part1 = 0;
    for(auto i=1; i<distribution.size(); ++i){
        part1 += i * (i-1) * distribution[i];
    }
    part1 = part1 * n  * (1 - C);
    double part2 = n * (n-1) * C;
    double re = (1 + part1 / part2) * gamma;
    // cout <<"Gmma 1 "<< gamma;
    return re > 0 ? re : 0;
}

double chao_estimator(vector<double>& distribution){
    double n = static_cast<double>(distribution.size());
    double C = 1-(distribution[1]/n);
    double D = 0;
    for(auto i=1; i<distribution.size(); ++i){
        D += distribution[i];
    }
    double part1 = D/C;
    double part2 = (n * (1-C)) / C;
    double gamma = gamma_2(distribution);
    // cout <<"Gmma 2 "<< gamma;
    return part1 + part2 * gamma;
    // return part1 + part2;
}

// the vector is too big to alloc, we should exchange time for space
// so there are many annotation in the code 
void recover_distribution_iteronce(vector<double>& distribution, double in_coff, int iter_num){
    // flows has pkts bigger than the upper bound will not included in the iteration
    const int upperbound = 10;
    const int sample_coefficient = static_cast<uint32_t>(in_coff);
    // good-turing
    distribution[0] = distribution[1]*2;
    // the recovered distribution
    vector<double> new_distribution(distribution.size() * sample_coefficient, 0);
    // the distribution involed in the iterations
    vector<double> iter_distribution(upperbound * sample_coefficient, 1 / (upperbound * in_coff));
    iter_distribution[0] = 0;
    // the flows aren't included in the iteration
    // vector<pair<int, double>> bigger_flows();
    // the probability of flow containing n pkt being sampled as i pkt flow
    vector<vector<double>> probability_n_i(upperbound * sample_coefficient, vector<double>(upperbound));  
    // the fraction of i pkt flow in sample set
    vector<double> fraction_i(upperbound, 0);
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
     
    // calc the new distribution
    for (int __i = 0; __i < iter_num; __i++){
        // note that __i is a var that we don't want it to be used in anywhere
        // the probability of i pkt flow in sample set represent n pkt flow in real set
        vector<vector<double>> probability_i_n(upperbound, vector<double>(upperbound * sample_coefficient)); 
        // double probability_i_n[100][200];
          
        // the total probability of i pkt flow in sample set
        vector<double> probability_i(upperbound, 0);
         
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
        HOW_LOG(L_INFO, "total distribution before correct: %.2f", local_total_distribution);
        iter_distribution[upperbound * sample_coefficient - 1] += 1-local_total_distribution;
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

void recover_distribution_iter_uponmultiple(vector<double>& distribution, double in_coff, int iter_num){
    // flows has pkts bigger than the upper bound will not included in the iteration
    const int upperbound = 10;
    const int sample_coefficient = static_cast<uint32_t>(in_coff);
    // good-turing
    distribution[0] = distribution[1]*2;
    // the recovered distribution
    vector<double> new_distribution(distribution.size() * sample_coefficient, 0);
    // the distribution involed in the iterations
    vector<double> iter_distribution(upperbound * sample_coefficient, 0);
    // the flows aren't included in the iteration
    // vector<pair<int, double>> bigger_flows();
    // the probability of flow containing n pkt being sampled as i pkt flow
    vector<vector<double>> probability_n_i(upperbound * sample_coefficient, vector<double>(upperbound));  
    // the fraction of i pkt flow in sample set
    vector<double> fraction_i(upperbound, 0);
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
    // build the initial distribution by multiple
    for(int i = 0; i < upperbound; ++i){
        // number of even numbers in the gap of the sample_coefficient
        const int even_num = sample_coefficient/2;
        for(int j = 0; j < even_num; j++){
            iter_distribution[i*sample_coefficient + j*2] += distribution[i] / even_num; 
        }
    }
    iter_distribution[0] = 0;
     
    // calc the new distribution
    for (int __i = 0; __i < iter_num; __i++){
        // note that __i is a var that we don't want it to be used in anywhere
        // the probability of i pkt flow in sample set represent n pkt flow in real set
        vector<vector<double>> probability_i_n(upperbound, vector<double>(upperbound * sample_coefficient)); 
        // double probability_i_n[100][200];
          
        // the total probability of i pkt flow in sample set
        vector<double> probability_i(upperbound, 0);
         
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
        HOW_LOG(L_INFO, "total distribution before correct: %.2f", local_total_distribution);
        iter_distribution[upperbound * sample_coefficient - 1] += 1-local_total_distribution;
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

void recover_distribution_simple(vector<double>& distribution, double in_coff){
    vector<double> new_distribution(distribution.size() * in_coff, 0);
    for(int i=0; i<distribution.size(); ++i){
        uint32_t new_idx = static_cast<uint32_t>(i * in_coff);
        new_distribution[new_idx] = distribution[i];
    }
    distribution = new_distribution;
}

void recover_distribution_simple4(vector<double>& distribution, double in_coff){
    vector<double> new_distribution(distribution.size() * in_coff, 0);
    for(int i=1; i<distribution.size(); ++i){
        uint32_t new_idx = static_cast<uint32_t>(i * in_coff);
        new_distribution[new_idx] = distribution[i]/2;
        new_idx = static_cast<uint32_t>(i * in_coff-2);
        new_distribution[new_idx] = distribution[i]/2;
    }
    distribution = new_distribution;
}

void recover_distribution2(vector<double>& distribution, double in_coff){
    vector<double> new_distribution(distribution.size() * in_coff, 0);
    for(int i=0; i<distribution.size(); ++i){
        uint32_t new_idx = static_cast<uint32_t>(i * in_coff);
        new_distribution[i] += distribution[i];
        new_distribution[new_idx] += distribution[i] / in_coff;
    }
    distribution = new_distribution;
}

double measure_main(DataTrace& trace, Manager& tbc_manager){
    CSVer csver("outputs/test_cardinality_30.csv");
    FTupleMatch* filter = new FTupleMatch("*.*.*.*", "*.*.*.*", "*", "*", "*");
    int hll_task_id = tbc_manager.allocate_mrachll(m, n, coin_level, filter, ACTION_SET_KEY_IPPAIR, ACTION_SET_VAL_IPPAIR_HASH);
    if(hll_task_id < 0) {
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
    map<uint16_t, map<uint16_t, vector<uint16_t>>> mrac_hll_sketch;
    tbc_manager.query(hll_task_id, mrac_hll_sketch);
    tbc_manager.getTaskStatistics(hll_task_id, TBC_Gt);
    auto& hll_data = mrac_hll_sketch[0][0];
    auto& mrac_data = mrac_hll_sketch[0][1];
    uint32_t estimate_distinct = HyperLogLogCalc(hll_data);

    vector<double> dist_groundtruth;
    vector<double> dist_sampled_simple;  // sampled distribution always true.
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
    double chao_result = chao_estimator(dist_sampled_zzc_0);
    // recover_distribution_iter_uponmultiple(dist_sampled_zzc, coff, 20);
    recover_distribution_iter_uponmultiple_involve0(dist_sampled_zzc_0, coff, 200000);
    recover_distribution_iter_uponmultiple_involve0(dist_sampled_mrac, coff, 200000);

    double alpha_with_groundtruth = calc_alpha(dist_groundtruth);
    double alpha_with_sampled_zzc_0 = calc_alpha(dist_sampled_zzc_0);
    double alpha_with_sampled_mrac_zzc = calc_alpha(dist_sampled_mrac);

    double real_distinct = static_cast<double>(Real_Freq.size());
    double estimated_distinct_gt = estimate_distinct / alpha_with_groundtruth;
    double estimated_distinct_sm_zzc_0 = estimate_distinct / alpha_with_sampled_zzc_0;
    double estimated_distinct_sm_mrac_zzc = estimate_distinct / alpha_with_sampled_mrac_zzc;
    // double estimated_distinct_mrac = estimate_distinct / alpha_with_sampled_mrac;

    // HOW_LOG(L_INFO, "Distinct Real : %.2f, HLL Original: %d, Estimate (GT): %.2f, Estimate (Sampled GT): %.2f, Estimate (Sampled MRAC): %.2f, Sample Chao: %.2f.", 
    //                  real_distinct, 
    //                  estimate_distinct,
    //                  estimated_distinct_gt, 
    //                  estimated_distinct_sm_zzc_0,
    //                  0, chao_result);
    HOW_LOG(L_INFO, "Distinct Real : %.2f, HLL Original: %d, Estimate (GT): %.2f, Estimate (Sampled GT): %.2f, Sample Chao: %.2f.", 
                     real_distinct, 
                     estimate_distinct,
                     estimated_distinct_gt, 
                     estimated_distinct_sm_zzc_0,
                     chao_result);
                      //  estimated_distinct_sm_mrac_zzc,
    // hll m, 
    // onst uint32_t m = 1024;  
    // const uint32_t n = 16384;
    // const int coin_level = 0; // 1/2
    // const double coff = 1;
    double re_before = abs(real_distinct - estimate_distinct) / real_distinct;
    double re_all_gt = abs(real_distinct - estimated_distinct_gt) / real_distinct;
    double re_smp_gt = abs(real_distinct - estimated_distinct_sm_zzc_0) / real_distinct;
    double re_smp_mrac = abs(real_distinct - estimated_distinct_sm_mrac_zzc) / real_distinct;
    csver.write(1024, 16384, 0, re_before, re_all_gt, re_smp_gt, re_smp_mrac);
    delete filter;
    return 0;
}

int main(int argc, char* argv[]){
    LOG_LEVEL = L_DEBUG;
    clock_t start = clock();
    DataTrace trace;
    // trace.LoadFromFile("../data/WIDE/head1000.dat");
    trace.LoadFromFile("/home/hzheng/workSpace/SketchLab/data/WIDE/head1000.dat");
    auto& tbc_manager = Manager::getDataplane();
    measure_main(trace, tbc_manager);
    clock_t ends = clock();
    cout <<"Running Time : "<<(double)(ends - start)/ CLOCKS_PER_SEC << endl;
}