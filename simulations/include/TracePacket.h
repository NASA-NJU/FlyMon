#ifndef _FLOW_KEY_H_
#define _FLOW_KEY_H_
#include <arpa/inet.h>
#include <string>
#include <cstdint>
#include <vector>
#include <stdexcept>
#include <map>
#include "Packet.h"
#include <chrono>

using namespace std;

#define FIELD_CONST  0
#define FIELD_IPSRC  1
#define FIELD_IPDST  2
#define FIELD_IPPAIR 3
#define FIELD_FTUPLE 4
#define FIELD_TSTAMP 5

// This is a packet trunck
class TracePacket  : public Packet{
  public:
    TracePacket( const char* five_tuple);
    ~TracePacket(){}
    string getDstString()const;
    string getSrcString()const;
    const uint8_t* getDstBytes()const;
    const uint8_t* getSrcBytes()const;
    const uint8_t* getSrcIpPort()const;
    uint16_t getSrcPort()const;
    uint16_t getDstPort()const;
    uint8_t getProtocol()const;
    uint64_t getTimestamp_ns()const;
    uint64_t getTimestamp_us()const;
    const uint8_t* getFlowKey_IPPair()const;
    const uint8_t* getFlowKey_5Tuple()const;

    int readFeld(uint32_t fieldId, pair<const uint8_t*, uint32_t>& field_info){
      int re = 0;
      switch(fieldId){
        case FIELD_CONST:
          field_info = make_pair((uint8_t* )(&const_val), 4);
          break;
        case FIELD_IPSRC:
          field_info = make_pair(_ipv4Src.getAddrBytes(), 4);
          break;
        case FIELD_IPDST:
          field_info = make_pair(_ipv4Dst.getAddrBytes(), 4); 
          break;
        case FIELD_IPPAIR:
          field_info = make_pair((uint8_t* )flowkey_ippair, 8); 
          break;
        case FIELD_FTUPLE:
          field_info = make_pair((uint8_t* )flowkey_5tuple, 13);
          break;
        case FIELD_TSTAMP:
          field_info = make_pair((uint8_t* )(&timestamp), 8);
          break;
        default:
          re = -1;
      }
      return re;
    }
    
    static string bytes_to_ip_str(const uint8_t* bytes){
        return to_string(bytes[0]) 
              + "." + to_string(bytes[1])
              + "." + to_string(bytes[2])
              + "." + to_string(bytes[3]);
    }
    static string uint32_to_ip_str(uint32_t ip){
        char buffer[INET_ADDRSTRLEN + 1];
        auto result = inet_ntop(AF_INET, &ip, buffer, sizeof(buffer));
        if (result == nullptr) throw std::runtime_error("Can't convert IP4 address");
        return string(buffer);
    }

    static void ip_str_to_bytes(const string& addr, uint8_t* bytes){ // with dot
      sscanf(addr.c_str(), "%hhu.%hhu.%hhu.%hhu", bytes, bytes+1, bytes+2, bytes+3);
    }

  private:
    //--------
    uint32_t const_val;
    uint64_t timestamp;
    char flowkey_ippair[8];
    char flowkey_ipsrcport[6];
    char flowkey_5tuple[13];
};

#endif
