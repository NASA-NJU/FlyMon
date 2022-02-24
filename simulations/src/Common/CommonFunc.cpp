#include "CommonFunc.h"

void Split_String(const string& str,  vector<string>& res, const string& splits)
{
	if (str == "")		return;
	//在字符串末尾也加入分隔符，方便截取最后一段
	string strs = str + splits;
	size_t pos = strs.find(splits);
	int step = splits.size();

	// 若找不到内容则字符串搜索函数返回 npos
	while (pos != strs.npos)
	{
		string temp = strs.substr(0, pos);
		res.push_back(temp);
		//去掉已分割的字符串,在剩下的字符串中进行分割
		strs = strs.substr(pos + step, strs.size());
		pos = strs.find(splits);
	}
}

void Split_String_Double(const string& str,  vector<double>& res, const string& splits){
	if (str == "")		return;
	//在字符串末尾也加入分隔符，方便截取最后一段
	string strs = str + splits;
	size_t pos = strs.find(splits);
	int step = splits.size();

	// 若找不到内容则字符串搜索函数返回 npos
	while (pos != strs.npos)
	{
		double temp = stod(strs.substr(0, pos));
		res.push_back(temp);
		//去掉已分割的字符串,在剩下的字符串中进行分割
		strs = strs.substr(pos + step, strs.size());
		pos = strs.find(splits);
	}
}

uint32_t HyperLogLogCalc(const vector<uint16_t>& data){
	double estimate = 0;                
	double V = 0;
	double dZ = 0;
	double Z = 0;
	double E = 0;
	double m = data.size();
	for(auto& bits : data){
		if(bits == 0){
			V+=1;
		}
		int p = 0;
		for(int i = 15; i >= 0; --i){
			uint16_t bit = (bits & (1<<i)) >> i;
			if(bit == 0){
				p = (15 - i) + 1;
				break;
			}
		}
		dZ += pow(2, -1*p);
	}
	Z = 1.0 / dZ;
	E = 0.679 * pow(m, 2) * Z;
	double E_star = 0;
	if (E < 2.5*m){
		E_star = (V != 0)? m * log2(m/V) : E;
	}
	double pow232 = pow(2, 32);
	E_star = (E <= pow232/30)? E : -1*pow232*log2(1-E/pow232);
	return E_star;
}

uint32_t CalcDistribution(vector<uint16_t>& blocks, vector<double>& dist){
    EMFSD * em_fsd_algo = new EMFSD();
	// em_fsd_algo->set_counters(blocks.size(), blocks.data());
	em_fsd_algo->set_counters(blocks.size(), blocks.data());
	for(int i=0; i<10; ++i){
		em_fsd_algo->next_epoch();
		printf("[EM] %d th epoch...with cardinality : %8.2f\n", i, em_fsd_algo->n_sum);
	}
	dist = em_fsd_algo->ns; // vector<double> dist
	delete em_fsd_algo;
}