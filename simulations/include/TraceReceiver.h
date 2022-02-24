# ifndef _TRACE_RECEIVER_H_
# define _TRACE_RECEIVER_H_

#include "HowLog/HowLog.h"
#include "TSP-NS/include/Common.h"
#include "TSP-NS/include/Network.h"
#include "TSP-NS/include/Simulator.h"
#include "StreamAlgorithm.h"
#include "DataTrace.h"
#include <memory>
#include <unordered_map>
using namespace std;
using namespace TSP_NS;

class TraceReceiver : public Node{
public:
    TraceReceiver(NODE_ID nodeId)
        : Node(nodeId)
    { 
        _state = 0;
        _pktCnt = 0;
    }
    virtual int receive(shared_ptr<Link> fromLink, shared_ptr<Packet> pktRecv){
        string srcAddr = pktRecv->getSrcIpAddrStr();
        // HOW_LOG(L_DEBUG, "SRC : %s", srcAddr.c_str());
        string dstAddr = pktRecv->getDstIpAddrStr();
        _pktCnt += 1;
        if (_ipSrcMap.find(srcAddr) != _ipSrcMap.end())
            _ipSrcMap[srcAddr]++;
        else
            _ipSrcMap[srcAddr] = 1;
    }
    unordered_map<string, int> getSrcMap(){
        return _ipSrcMap;
    }
    unordered_map<string, int> getPairMap(){
        return _ipPairMap;
    }
    int getPktCount(){
        return _pktCnt;
    }
private: //Event
    int _state;
    int _pktCnt;
    unordered_map<string, int> _ipSrcMap;  // src
    unordered_map<string, int> _ipPairMap; // src:dst
};

#endif