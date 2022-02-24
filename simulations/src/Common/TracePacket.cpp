#include "TracePacket.h"
#include "HowLog/HowLog.h"
#include <cstring>



TracePacket::TracePacket( const char* five_tuple)
    : Packet(five_tuple)
{
    // if (strlen(five_tuple) < 13){
    //     HOW_LOG(L_ERROR, "The five-tuple length is not valid.");
    //     return;
    // }
    //-------
    timestamp = (uint64_t)std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count();
    const_val = 0x12345678;
    memcpy(flowkey_ippair, five_tuple, 4);
    memcpy(flowkey_ippair+4, five_tuple+4+2, 4);
    memcpy(flowkey_ipsrcport, five_tuple, 6);
    memcpy(flowkey_5tuple, five_tuple, 13);
    
}

// struct sockaddr_in sa;
// char str[INET_ADDRSTRLEN];

// // store this IP address in sa:
// inet_pton(AF_INET, "192.0.2.33", &(sa.sin_addr));

// // now get it back and print it
// inet_ntop(AF_INET, &(sa.sin_addr), str, INET_ADDRSTRLEN);

string TracePacket::getDstString()const{
    return bytes_to_ip_str(_ipv4Dst.getAddrBytes());
}

string TracePacket::getSrcString()const{
    return bytes_to_ip_str(_ipv4Src.getAddrBytes());
}
uint64_t TracePacket::getTimestamp_ns()const{
    return timestamp;
}
uint64_t TracePacket::getTimestamp_us()const{
    return timestamp/1000;
}
const uint8_t* TracePacket::getDstBytes()const{
    return _ipv4Dst.getAddrBytes(); 
}

const uint8_t* TracePacket::getSrcBytes()const{
    return _ipv4Src.getAddrBytes(); 
}

const uint8_t* TracePacket::getSrcIpPort()const{
    return (uint8_t* )flowkey_ipsrcport;
}

const uint8_t* TracePacket::getFlowKey_IPPair()const {
    return (uint8_t* )flowkey_ippair; 
}

const uint8_t* TracePacket::getFlowKey_5Tuple()const {
    return (uint8_t* )flowkey_5tuple;
}


uint8_t TracePacket::getProtocol()const{
    return *((uint8_t*)_protocol);
}

uint16_t TracePacket::getSrcPort()const{
    return *((uint16_t*)_sport);
}

uint16_t TracePacket::getDstPort()const{
    return *((uint16_t*)_dport);
}
