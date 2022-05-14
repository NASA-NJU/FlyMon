#ifndef _FLYMON_HDR_P4_
#define _FLYMON_HDR_P4_

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------


/** Jinja2 variable list.
 * CMUG_GROUP_CONFIGS: [CMUG] ~ A list of CMU-Group configurations.
 * - CMUG: {id, type, mau_start, cmu_num, cmu_size, candidate_key_set}
 * - - id: identifier of CMU-Group.
 * - - type: 1~ ingress, 2~ egrss.
 * - - mau_start: start stage (compression stage) placement of the CMU-Group.
 * - - cmu_num: number of CMU in each CMU-Group.
 * - - candidate_key_set: candida
**/


// CMU with 2 paramters.
struct cmu_metadata_t{
    bit<8> task_id;
    bit<16>    key;
    bit<16>    param1;
    bit<16>    param2;  // also used as the output of SALU.
}



struct cmu_group_metadata_a_t{
    bit<16> compressed_key1; 
    bit<16> compressed_key2;  
    bit<16> compressed_key3;  
    cmu_metadata_t cmu1;
    cmu_metadata_t cmu2;
    cmu_metadata_t cmu3;
}

struct cmu_group_metadata_b_t{
    bit<32> compressed_key1;
    bit<16> compressed_key2;
    cmu_metadata_t cmu1;
    cmu_metadata_t cmu2;
    cmu_metadata_t cmu3;
}


struct ingress_metadata_t {
    cmu_group_metadata_a_t cmu_group1;
    cmu_group_metadata_a_t cmu_group2;
    cmu_group_metadata_a_t cmu_group3;
    cmu_group_metadata_a_t cmu_group4;
}

struct egress_metadata_t {
    cmu_group_metadata_b_t cmu_group5;
    cmu_group_metadata_b_t cmu_group6;
    cmu_group_metadata_b_t cmu_group7;
    cmu_group_metadata_b_t cmu_group8;
    cmu_group_metadata_b_t cmu_group9;
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

#define IPV4        0x0800 // ETHERTYPE_IPV4
#define IPV6        0x86DD// ETHERTYPE_IPV4
#define UDP         0x11  // PROTO_UDP
#define TCP         0x06  // PROTO_TCP

header ethernet_h {
    bit<48> dst_addr;
    bit<48> src_addr;
    bit<16> ether_type;
}

header ipv4_h {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> total_len;
    bit<16> identification;
    bit<3>  flags;
    bit<13> frag_offset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdr_checksum;
    bit<32> src_addr;
    bit<32> dst_addr;
}

header ipv6_h {
    bit<4>   version;
    bit<8>   traffic_class;
    bit<20>  flow_label;
    bit<16>  payload_len;
    bit<8>   next_hdr;
    bit<8>   hop_limit;
    bit<128> src_addr;
    bit<128> dst_addr;
}

// A common L4 Header for tcp and udp.
header l4port_h {
    bit<16> src_port;
    bit<16> dst_port;
}

// Move ports to transport_h.
header tcp_h {
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4> data_offset;
    bit<4> res;
    bit<8> flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

// Move ports to transport_h.
header udp_h {
    bit<16> hdr_length;
    bit<16> checksum;
}

struct header_t {
    ethernet_h ethernet;
    ipv4_h ipv4;
    ipv6_h ipv6;
    l4port_h ports;
    tcp_h tcp;
    udp_h udp;
}

#endif