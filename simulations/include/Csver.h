#ifndef _CSVER_H_
#define _CSVER_H_

#include <iostream>
#include <fstream>
using namespace std;

template <class F, class First, class... Rest>
void do_for(F f, First first, Rest... rest) {
    f(first);
    do_for(f, rest...);
}
template <class F>
void do_for(F f) {
    // Parameter pack is empty.
}
class CSVer{
public:
    CSVer(const string& file_name){
        ofs.open(file_name, ios::app);
    }
    template <class... T>
    void write(T... args)
    {    
        do_for([&](auto arg) {
        // You can do something with arg here.
            ofs << arg << ",";
        }, args...);
        ofs << endl;
    }
    ~CSVer(){
        ofs.close();
    }
private:
     std::ofstream ofs;
};

#endif