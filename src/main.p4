/*******************************************************************************
 * BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
 *
 * Copyright (c) 2019-present Barefoot Networks, Inc.
 *
 * All Rights Reserved.
 *
 * NOTICE: All information contained herein is, and remains the property of
 * Barefoot Networks, Inc. and its suppliers, if any. The intellectual and
 * technical concepts contained herein are proprietary to Barefoot Networks, Inc.
 * and its suppliers and may be covered by U.S. and Foreign Patents, patents in
 * process, and are protected by trade secret or copyright law.  Dissemination of
 * this information or reproduction of this material is strictly forbidden unless
 * prior written permission is obtained from Barefoot Networks, Inc.
 *
 * No warranty, explicit or implicit is provided, unless granted under a written
 * agreement with Barefoot Networks, Inc.
 *
 ******************************************************************************/

#include <core.p4>
#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "headers.p4"
#include "util.p4"
#include "task_registers.p4"
#include "compression_units.p4"
#include "execution_units.p4"
#include "reporting_units.p4"
#include "dupkey_filter.p4"


control SwitchIngress(
        inout header_t hdr,
        inout ingress_metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {

    // Create direct counters

    action hit(PortId_t port) {
        ig_intr_tm_md.ucast_egress_port = port;
    }

    action miss() {
        ig_intr_dprsr_md.drop_ctl = 0x1; // Drop packet.
    }

    table simple_fwd {
        key = {
            ig_intr_md.ingress_port : exact;
        }
        actions = {
            hit;
            miss;
        }
        const default_action = miss;
        size = 64;
    }
        
    TaskRegister_0() task_register_0;
    

    
        CompressionUnit_0() cu_0;
    

    
        ExecutionUnit_0() eu_0;
    
        ExecutionUnit_1() eu_1;
    
        ExecutionUnit_2() eu_2;
    
        ExecutionUnit_3() eu_3;
    

    
        ReportingUnit_0() ru_0;
    
        
        DupKeyFilter() dup_filter;
    apply {
        simple_fwd.apply();
        
        task_register_0.apply(hdr, ig_intr_md, ig_md);
            cu_0.apply(hdr, ig_intr_md, ig_md);
            
            eu_0.apply(hdr, ig_intr_md, ig_md);
            
            eu_1.apply(hdr, ig_intr_md, ig_md);
            
            eu_2.apply(hdr, ig_intr_md, ig_md);
            
            eu_3.apply(hdr, ig_intr_md, ig_md);
            
            ru_0.apply(hdr, ig_intr_md, ig_md);
        

        // digest is generated in the deparser.
        dup_filter.apply(hdr, ig_intr_md, ig_md, ig_intr_dprsr_md);
    
        ig_intr_tm_md.bypass_egress = 1w1;
    }
}


// ---------------------------------------------------------------------------
// Ingress Deparser
// ---------------------------------------------------------------------------
control SwitchIngressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in ingress_metadata_t ig_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {
    Digest<heavy_key_digest_t>() digest;
    apply {
        if (ig_intr_dprsr_md.digest_type == 1) {
            digest.pack({hdr.ipv4.src_addr, hdr.ipv4.dst_addr, ig_md.elements.src_port, ig_md.elements.dst_port, hdr.ipv4.protocol });
        }
        pkt.emit(hdr);
    }
}


// ---------------------------------------------------------------------------
// Ingress parser
// ---------------------------------------------------------------------------
parser SwitchIngressParser(
        packet_in pkt,
        out header_t hdr,
        out ingress_metadata_t ig_md,
        out ingress_intrinsic_metadata_t ig_intr_md) {

    TofinoIngressParser() tofino_parser;

    state start {
        tofino_parser.apply(pkt, ig_intr_md);

        ig_md.elements.src_port = 0;
        ig_md.elements.dst_port = 0;

        
            
                ig_md.cu_0.hash_val0 = 0;
            
                ig_md.cu_0.hash_val1 = 0;
            
                ig_md.cu_0.hash_val2 = 0;
            
        

        
        ig_md.eu_0.task_id = 0;
        ig_md.eu_0.key = 0;
        ig_md.eu_0.val = 0;
        
        ig_md.eu_1.task_id = 0;
        ig_md.eu_1.key = 0;
        ig_md.eu_1.val = 0;
        
        ig_md.eu_2.task_id = 0;
        ig_md.eu_2.key = 0;
        ig_md.eu_2.val = 0;
        
        ig_md.eu_3.task_id = 0;
        ig_md.eu_3.key = 0;
        ig_md.eu_3.val = 0;
        

        
        ig_md.ru_0.flag = 0;
        

        ig_md.dup_filter_meta.bit0 = 0;
        ig_md.dup_filter_meta.bit1 = 0;
        ig_md.dup_filter_meta.bit2 = 0;
        ig_md.dup_filter_meta.bit3 = 0;

        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select (hdr.ethernet.ether_type) {
            ETHERTYPE_IPV4 : parse_ipv4;
            default : reject;
        }
    }
    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select (hdr.ipv4.protocol) {
            IP_PROTOCOLS_TCP : parse_tcp;
            IP_PROTOCOLS_UDP : parse_udp;
            default : reject;
        }
    }
    state parse_tcp {
        pkt.extract(hdr.tcp);
        ig_md.elements.src_port = hdr.tcp.src_port;
        ig_md.elements.dst_port = hdr.tcp.dst_port;
        transition accept;
    }
    state parse_udp {
        pkt.extract(hdr.udp);
        ig_md.elements.src_port = hdr.udp.src_port;
        ig_md.elements.dst_port = hdr.udp.dst_port;
        transition accept;
    }
}


Pipeline(SwitchIngressParser(),
         SwitchIngress(),
         SwitchIngressDeparser(),
         EmptyEgressParser(),
         EmptyEgress(),
         EmptyEgressDeparser()) pipe;

Switch(pipe) main;