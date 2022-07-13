#include <core.p4>
#include <tna.p4>

#include "headers.p4"
#include "cmu_groups.p4"

// ---------------------------------------------------------------------------
// Ingress parser
// ---------------------------------------------------------------------------
parser FlyMonIngressParser(
        packet_in pkt,
        out header_t hdr,
        out ingress_metadata_t ig_md,
        out ingress_intrinsic_metadata_t ig_intr_md) {
    state start {
        pkt.extract(ig_intr_md);
        // Enable bridge CMU Groups.
        ig_md.cmu_group1.cmu1.param.setValid();
        ig_md.cmu_group1.cmu2.param.setValid();
        ig_md.cmu_group1.cmu3.param.setValid();
        ig_md.cmu_group2.cmu1.param.setValid();
        ig_md.cmu_group2.cmu2.param.setValid();
        ig_md.cmu_group2.cmu3.param.setValid();
        ig_md.cmu_group3.cmu1.param.setValid();
        ig_md.cmu_group3.cmu2.param.setValid();
        ig_md.cmu_group3.cmu3.param.setValid();
        ig_md.cmu_group4.cmu1.param.setValid();
        ig_md.cmu_group4.cmu2.param.setValid();
        ig_md.cmu_group4.cmu3.param.setValid();
        // Start parsing the packet.
        transition select(ig_intr_md.resubmit_flag) {
            1 : parse_resubmit;
            0 : parse_port_metadata;
        }
    }
    state parse_resubmit {
        // Parse resubmitted packet here.
        transition reject;
    }
    state parse_port_metadata {
        pkt.advance(PORT_METADATA_SIZE);
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select (hdr.ethernet.ether_type) {
            IPV4 : parse_ipv4;
            IPV6 : parse_ipv6;
            default : reject;
        }
    }
    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select (hdr.ipv4.protocol) {
            TCP : parse_tcp;
            UDP : parse_udp;
            default : reject;
        }
    }
    state parse_ipv6 {
        pkt.extract(hdr.ipv6);
        transition select (hdr.ipv6.next_hdr) {
            TCP : parse_tcp;
            UDP : parse_udp;
            default : reject;
        }
    }
    state parse_tcp {
        pkt.extract(hdr.ports);
        pkt.extract(hdr.tcp);
        transition accept;
    }
    state parse_udp {
        pkt.extract(hdr.ports);
        pkt.extract(hdr.udp);
        transition accept;
    }
}

control FlyMonIngress(
        inout header_t hdr,
        inout ingress_metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {

    action hit(PortId_t port) {
        ig_intr_tm_md.ucast_egress_port = port;
    }
    action miss() {
        ig_intr_dprsr_md.drop_ctl = 0x1; // Drop packet.
    }
    // Simple port-forwarding is used for testing.
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
    CMU_Group1() cmu_group1;
    CMU_Group2() cmu_group2;
    CMU_Group3() cmu_group3;
    CMU_Group4() cmu_group4;
    apply {
        simple_fwd.apply();
        cmu_group1.apply(hdr, ig_intr_md, ig_md);
        cmu_group2.apply(hdr, ig_intr_md, ig_md);
        cmu_group3.apply(hdr, ig_intr_md, ig_md);
        cmu_group4.apply(hdr, ig_intr_md, ig_md);
    }
}


// ---------------------------------------------------------------------------
// Ingress Deparser
// ---------------------------------------------------------------------------
control FlyMonIngressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in ingress_metadata_t ig_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {
    apply {
        // If needed, enable inter-group collaboration.
        // Pass the execution results from the upstream to the downstream.
        pkt.emit(ig_md.cmu_group1.cmu1.param);
        pkt.emit(ig_md.cmu_group1.cmu2.param);
        pkt.emit(ig_md.cmu_group1.cmu3.param);
        pkt.emit(ig_md.cmu_group2.cmu1.param);
        pkt.emit(ig_md.cmu_group2.cmu2.param);
        pkt.emit(ig_md.cmu_group2.cmu3.param);
        pkt.emit(ig_md.cmu_group3.cmu1.param);
        pkt.emit(ig_md.cmu_group3.cmu2.param);
        pkt.emit(ig_md.cmu_group3.cmu3.param);
        pkt.emit(ig_md.cmu_group4.cmu1.param);
        pkt.emit(ig_md.cmu_group4.cmu2.param);
        pkt.emit(ig_md.cmu_group4.cmu3.param);
        pkt.emit(hdr);
    }
}


// ---------------------------------------------------------------------------
// Egress parser
// ---------------------------------------------------------------------------
parser FlyMonEgressParser(
        packet_in pkt,
        out header_t hdr,
        out egress_metadata_t eg_md,
        out egress_intrinsic_metadata_t eg_intr_md) {

    state start {
        // Init intrinsic metadata.
        pkt.extract(eg_intr_md);
        transition parse_flymeta;
    }

    state parse_flymeta{
        // If needed, enable inter-group collaboration.
        // Pass the execution results from the upstream to the downstream.
        pkt.extract(eg_md.cmu_group5.cmu1.param);
        pkt.extract(eg_md.cmu_group5.cmu2.param);
        pkt.extract(eg_md.cmu_group5.cmu3.param);
        pkt.extract(eg_md.cmu_group6.cmu1.param);
        pkt.extract(eg_md.cmu_group6.cmu2.param);
        pkt.extract(eg_md.cmu_group6.cmu3.param);
        pkt.extract(eg_md.cmu_group7.cmu1.param);
        pkt.extract(eg_md.cmu_group7.cmu2.param);
        pkt.extract(eg_md.cmu_group7.cmu3.param);
        pkt.extract(eg_md.cmu_group8.cmu1.param);
        pkt.extract(eg_md.cmu_group8.cmu2.param);
        pkt.extract(eg_md.cmu_group8.cmu3.param);
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select (hdr.ethernet.ether_type) {
            IPV4 : parse_ipv4;
            IPV6 : parse_ipv6;
            default : reject;
        }
    }
    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select (hdr.ipv4.protocol) {
            TCP : parse_tcp;
            UDP : parse_udp;
            default : reject;
        }
    }
    state parse_ipv6 {
        pkt.extract(hdr.ipv6);
        transition select (hdr.ipv6.next_hdr) {
            TCP : parse_tcp;
            UDP : parse_udp;
            default : reject;
        }
    }
    state parse_tcp {
        pkt.extract(hdr.ports);
        pkt.extract(hdr.tcp);
        transition accept;
    }
    state parse_udp {
        pkt.extract(hdr.ports);
        pkt.extract(hdr.udp);
        transition accept;
    }
}

control FlyMonEgress(
        inout header_t hdr,
        inout egress_metadata_t eg_md,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_intr_from_prsr,
        inout egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr,
        inout egress_intrinsic_metadata_for_output_port_t eg_intr_md_for_oport) {

    CMU_Group5() cmu_group5;
    CMU_Group6() cmu_group6;
    CMU_Group7() cmu_group7;
    CMU_Group8() cmu_group8;
    CMU_Group9() cmu_group9;
    apply {
        cmu_group5.apply(hdr, eg_intr_md, eg_md);
        cmu_group6.apply(hdr, eg_intr_md, eg_md);
        cmu_group7.apply(hdr, eg_intr_md, eg_md);
        cmu_group8.apply(hdr, eg_intr_md, eg_md);
        cmu_group9.apply(hdr, eg_intr_md, eg_md);
    }
}

// ---------------------------------------------------------------------------
// Egress Deparser
// ---------------------------------------------------------------------------
control FlyMonEgressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in egress_metadata_t eg_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md) {
    apply {
        pkt.emit(hdr);
    }
}

Pipeline(FlyMonIngressParser(),
         FlyMonIngress(),
         FlyMonIngressDeparser(),
         FlyMonEgressParser(),
         FlyMonEgress(),
         FlyMonEgressDeparser()) pipe;
         
Switch(pipe) main;