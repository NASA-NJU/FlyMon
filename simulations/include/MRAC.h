#ifndef STREAMMEASUREMENTSYSTEM_MRAC_H
#define STREAMMEASUREMENTSYSTEM_MRAC_H

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include "EMFSD.h"
#include "BOBHash/BOBHash32.h"
#include "HowLog/HowLog.h"

class MRAC {
    uint32_t w;
    uint32_t * counters;
    BOBHash32 * bob_hash;

    int iter;

    double est_cardinality = 0;

    EMFSD *em_fsd_algo = NULL;

  public:
    string name;

    MRAC(int TOT_MEM_IN_BYTES, int MRAC_EM_ITER) {
        w = TOT_MEM_IN_BYTES / 4;
        srand(time(0));
        counters = new uint32_t[w];
        memset(counters, 0, sizeof(uint32_t) * w);
        bob_hash = new BOBHash32(rand() % MAX_PRIME32);
        iter = MRAC_EM_ITER;
        HOW_LOG(L_DEBUG, "Alloc MRAC width : %d", w);
    }

    ~MRAC(){
        delete[] counters;
        delete bob_hash;
    }

    void insert(const uint8_t *item, int key_len) {
        uint32_t pos = bob_hash->run((const char *)item, key_len) % w;
        counters[pos] += 1;
    }

    void collect_fsd() {
        em_fsd_algo = new EMFSD();
        em_fsd_algo->set_counters(w, counters);
    }

    void next_epoch() { em_fsd_algo->next_epoch(); }
    void get_distribution(vector<double> &dist_est, int coff=1) {
        for(int i=0; i<w; ++i){
            counters[i] = counters[i] * coff;
        }
        collect_fsd();
        for (int i = 0; i < iter; ++i)
        {
            next_epoch();
            printf("[EM] %d th epoch...with cardinality : %8.2f\n", i, em_fsd_algo->n_sum);
        }
        dist_est = em_fsd_algo->ns; // vector<double> dist
        
    }

    double get_cardinality() {
        return em_fsd_algo->n_sum;
    }
};

#endif // STREAMMEASUREMENTSYSTEM_MRAC_H