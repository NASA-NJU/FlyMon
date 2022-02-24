#ifndef _DUP_KEY_FILTER_P4_
#define _DUP_KEY_FILTER_P4_

#include "mdata.p4"


control DupKeyFilter ( in header_t hdr,
                        in ingress_intrinsic_metadata_t ig_intr_md,
                        inout ingress_metadata_t ig_md,
                        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_md_for_dprsr) 
{
    

    Register<bit<1>, bit<16>>(65536, 0) bloom_filter_part0;
    Hash<bit<16>>(HashAlgorithm_t.CRC16) hash_unit_0;
    Register<bit<1>, bit<16>>(65536, 0) bloom_filter_part1;
    Hash<bit<16>>(HashAlgorithm_t.CRC16) hash_unit_1;
    Register<bit<1>, bit<16>>(65536, 0) bloom_filter_part2;
    Hash<bit<16>>(HashAlgorithm_t.CRC16) hash_unit_2;
    Register<bit<1>, bit<16>>(65536, 0) bloom_filter_part3;
    Hash<bit<16>>(HashAlgorithm_t.CRC16) hash_unit_3;

    RegisterAction<bit<1>, bit<16>, bit<1>>(bloom_filter_part0) reg_op_filter0 = {
        void apply(inout bit<1> value, out bit<1> result) {
            result = value;
            value = 1;
        }
    };
    RegisterAction<bit<1>, bit<16>, bit<1>>(bloom_filter_part1) reg_op_filter1 = {
        void apply(inout bit<1> value, out bit<1> result) {
            result = value;
            value = 1;
        }
    };
    RegisterAction<bit<1>, bit<16>, bit<1>>(bloom_filter_part2) reg_op_filter2 = {
        void apply(inout bit<1> value, out bit<1> result) {
            result = value;
            value = 1;
        }
    };
    
    RegisterAction<bit<1>, bit<16>, bit<1>>(bloom_filter_part3) reg_op_filter3 = {
        void apply(inout bit<1> value, out bit<1> result) {
            result = value;
            value = 1;
        }
    };

    action filter0(){
        ig_md.dup_filter_meta.bit0 = reg_op_filter0.execute(
            hash_unit_0.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol })  // change the order to get different hash in the data plane.
        );
    }
    action filter1(){
        ig_md.dup_filter_meta.bit1 = reg_op_filter1.execute(
            hash_unit_1.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol })
        );
    }
    action filter2(){
        ig_md.dup_filter_meta.bit2 = reg_op_filter2.execute(
            hash_unit_2.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol })
        );
    }
    action filter3(){
        ig_md.dup_filter_meta.bit3 = reg_op_filter3.execute(
            hash_unit_3.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol })
        );
    }
    @pragma stage 10
    table tbl_bloom_part0{
        actions = {
            filter0;
        }
        const default_action=filter0;
        size = 1;
    }
    @pragma stage 10
    table tbl_bloom_part1{
        actions = {
            filter1;
        }
        const default_action=filter1;
        size = 1;
    }
    @pragma stage 10
    table tbl_bloom_part2{
        actions = {
            filter2;
        }
        const default_action=filter2;
        size = 1;
    }
    @pragma stage 10
    table tbl_bloom_part3{
        actions = {
            filter3;
        }
        const default_action=filter3;
        size = 1;
    }

    action mark_as_report(){
        ig_intr_md_for_dprsr.digest_type = 1;
    }
    @pragma stage 11
    table tbl_judge_dupkey{
        key = {
            
            ig_md.ru_0.flag : ternary;
            
            ig_md.dup_filter_meta.bit0 : exact;
            ig_md.dup_filter_meta.bit1 : exact;
            ig_md.dup_filter_meta.bit2 : exact;
            ig_md.dup_filter_meta.bit3 : exact;
        }
        actions = {
            mark_as_report;
        }
        size = 32;
    }
    apply {
        tbl_bloom_part0.apply();
        tbl_bloom_part1.apply();
        tbl_bloom_part2.apply();
        tbl_bloom_part3.apply();
        tbl_judge_dupkey.apply();
    }
}

#endif