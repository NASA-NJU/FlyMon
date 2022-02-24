#ifndef _MY_COMMON_FUNC_H_
#define _MY_COMMON_FUNC_H_
#include <vector>
#include <string>
#include <cmath>
#include "EMFSD.h"
using namespace std;

void Split_String(const string& str,  vector<string>& res, const string& splits);

void Split_String_Double(const string& str,  vector<double>& res, const string& splits);

uint32_t HyperLogLogCalc(const vector<uint16_t>& blocks);

uint32_t CalcDistribution(vector<uint16_t>& blocks, vector<double>& dist);

#endif