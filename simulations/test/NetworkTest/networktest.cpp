#include "CMSketch.h"
#include "MeasurementNode.h"
#include "TraceSender.h"
#include "TraceReceiver.h"
#include <chrono> 
using namespace chrono;
#define THREAD_NUM  4
#define TOT_MEM_IN_BYTES 600 * 1024

#define START_TIME  Time(Second,1)
#define STOP_TIME   Time(Second,200000)

int main(){
    LOG_LEVEL = L_INFO;
    Logger::initLogger("network_test", "./log");

    DataTrace trace;
    trace.LoadFromFile("../data/WIDE/head1000.dat");
    // trace.LoadFromFile("../data/WIDE/one_sec_15.dat");
    // trace.LoadFromFile("../data/WIDE/five_sec_0.dat");

    // Topology
    // Sender --link1-- MN1 --link2-- MN2 --link3-- Recever
    NODE_ID node_id = 0;

    // Define Nodes
    shared_ptr<TraceSender> sender = make_shared<TraceSender>(node_id++, trace, Time(MicroSecond,100));
    shared_ptr<MeasurementNode> measure_node_1 = make_shared<MeasurementNode>(node_id++,  make_shared<CM_Sketch>(4, 4, TOT_MEM_IN_BYTES));
    shared_ptr<MeasurementNode> measure_node_2 = make_shared<MeasurementNode>(node_id++,  make_shared<CM_Sketch>(4, 4, TOT_MEM_IN_BYTES));
    shared_ptr<TraceReceiver> receiver = make_shared<TraceReceiver>(node_id++);

    // Define Links
    shared_ptr<Link> link1 = make_shared<Link>(Time(MicroSecond, 100), 1000*1024*1024);  //100us, 100G
    shared_ptr<Link> link2 = make_shared<Link>(Time(MicroSecond, 100), 1000*1024*1024);  //100us, 100G
    shared_ptr<Link> link3 = make_shared<Link>(Time(MicroSecond, 100), 1000*1024*1024);  //100us, 100G

    // Construct topo
    sender->addLink(Ipv4Address("10.0.1.1"), link1);
    measure_node_1->addLink(Ipv4Address("10.0.1.2"), link1);
    measure_node_1->addLink(Ipv4Address("10.0.2.1"), link2);
    measure_node_2->addLink(Ipv4Address("10.0.2.2"), link2);
    measure_node_2->addLink(Ipv4Address("10.0.3.1"), link3);
    receiver->addLink(Ipv4Address("10.0.3.1"), link3);

    // Add routing item
    measure_node_1->addRouteItem(Ipv4Address("0.0.0.0"), Ipv4Address("0.0.0.0"), link2);
    measure_node_2->addRouteItem(Ipv4Address("0.0.0.0"), Ipv4Address("0.0.0.0"), link3);

    // Start Application
    sender->setStartTime(START_TIME);
    sender->setStopTime(STOP_TIME);

    auto start = system_clock::now();
    Simulator::run(THREAD_NUM);
    auto end   = system_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    cout<<"Done. Cost real time: " << double(duration.count()) * microseconds::period::num / microseconds::period::den  << " seconds."<<endl; 

    unordered_map<string, int> real_receive = receiver->getSrcMap();
    int real_cnt = receiver->getPktCount();
    double temp_relation_error_sum = 0;
    for (auto item : real_receive){
        uint8_t key[4]; 
        TracePacket::ip_str_to_bytes(item.first, key);
 		int estimate = measure_node_1->query(key);
		double relative_error = abs(item.second - estimate) / (double)item.second;
		temp_relation_error_sum += relative_error;       
        // HOW_LOG(L_INFO, "Flow %s, Query Flow %s, real=%d, estimate=%d", item.first.c_str(), TracePacket::bytes_to_ip_str(key).c_str(), item.second, estimate); 
    }
    HOW_LOG(L_DEBUG, "Total %d packets, receive %d packets, %d flows, ARE = %f", trace.size(), real_cnt,
                     real_receive.size(), 
                     temp_relation_error_sum/real_receive.size());
    Simulator::destroy();
}