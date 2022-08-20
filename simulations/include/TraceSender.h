# ifndef _TRACE_SENDER_H_
# define _TRACE_SENDER_H_

#include "HowLog/HowLog.h"
#include "TSP-NS/include/Common.h"
#include "TSP-NS/include/Network.h"
#include "TSP-NS/include/Simulator.h"
#include "StreamAlgorithm.h"
#include "DataTrace.h"
#include <memory>
using namespace std;
using namespace TSP_NS;

class TraceSender : public Node{
public:
    TraceSender(NODE_ID nodeId, DataTrace& trace, Time ingerval, int trunc_sz = 10000)
        : Node(nodeId), _trace(trace), _ingerval(ingerval), _trunck_sz(trunc_sz)
    { 
        _cursor = trace.begin();
    }
    void setStartTime(Time time)
    {
        Simulator::schedule(getNodeId(), Simulator::getTimestamp(getNodeId(), time), "start send trace",  &TraceSender::startEvent, this); 
    };
    void setStopTime(Time time)
    {
        Simulator::schedule(getNodeId(), Simulator::getTimestamp(getNodeId(), time), "stop send trace",  &TraceSender::stopEvent, this); 
    };
private: //Event
    void startEvent(){
        _state = 1;
        Simulator::schedule(getNodeId(), Simulator::getTimestamp(getNodeId(), Time(MilliSecond,100)), "Send Begin.",  &TraceSender::sentOnePacket, this); 

    }
    void stopEvent(){
        _state = 0;
    }
    void sentOnePacket(){
        Ipv4Address localAddr = getLocalAddress();
        // shared_ptr<Packet> pkt(&(*_cursor));
        shared_ptr<Packet> pkt(*_cursor);
        sendDefault(pkt);
        _cursor++;  // Next packet
        if(_state == 1 && _cursor != _trace.end()){
            Simulator::schedule(getNodeId(), Simulator::getTimestamp(getNodeId(), _ingerval), "Send Continue.",  &TraceSender::sentOnePacket, this); 
        }
        // HOW_LOG(L_DEBUG, "%s->%s", (pkt->getSrcIpAddrStr()).c_str(), (pkt->getDstIpAddrStr()).c_str());
    }
    int _state;
    Time _ingerval;
    DataTrace& _trace;
    int _trunck_sz;
    DataTrace::iterator _cursor;
};
#endif