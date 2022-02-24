# ifndef _MEASUREMENT_NODE_
# define _MEASUREMENT_NODE_

#include "HowLog/HowLog.h"
#include "StreamAlgorithm.h"
#include "TSP-NS/include/Common.h"
#include "TSP-NS/include/Network.h"
// #include "Common.h"
// #include "Network.h"
#include <memory>
using namespace std;
using namespace TSP_NS;

class MeasurementNode : public Node{
public:
    MeasurementNode(NODE_ID node_id, shared_ptr<StreamAlgorithm> alg)
        : Node(node_id)
    {
        _alg = alg;
    }
    virtual int receive(shared_ptr<Link> fromLink, shared_ptr<Packet> pktRecv){
        //转发
        int re = forward(pktRecv);
        if(re < 0)
            mark_to_drop(fromLink, pktRecv);
        return 0;
    }
    int forward(shared_ptr<Packet> pktRecv){
        shared_ptr<Link> outLink = route(pktRecv->getDstIpAddr());
        if(outLink == nullptr)
            return -1;  
        // uint8_t key[4]; 
        // TracePacket::ip_str_to_bytes(pktRecv->getSrcIpAddrStr(), key);
        _alg->insert(pktRecv->getSrcIpAddrBytes());     
        /*
        * MAC地址的修改暂不实现
        */
        return sendToLink(pktRecv, outLink);
    }

    int query(const uint8_t * key){
        return _alg->query(key);
    }
private:
    shared_ptr<StreamAlgorithm> _alg;
    void mark_to_drop(shared_ptr<Link> fromLink, shared_ptr<Packet> pktRecv){
        //向源发送一个ICMP通知
        shared_ptr<Packet> icmpReply = make_shared<Packet>(pktRecv->getDstIpAddr(), pktRecv->getSrcIpAddr(), 64, "ICMP:unreachable");
        sendToLink(icmpReply, fromLink);
    }
};

# endif