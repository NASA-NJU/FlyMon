#ifndef _CMU_GROUP_P4_
#define _CMU_GROUP_P4_

#include "headers.p4"

/** Below are all definitions of CMU-Groups */

// Definition for CMU-Group1


control CMU_Group1 ( in header_t hdr,
                               in ingress_intrinsic_metadata_t intr_md,
                               inout ingress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit3;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group1.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group1.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash3(){
        meta.cmu_group1.compressed_key3 = hash_unit3.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 0
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 0
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }
    @pragma stage 0
    table tbl_hash3{
        actions = {
            hash3;
        }
        const default_action = hash3();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu1_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = (meta.cmu_group1.compressed_key1 ^ meta.cmu_group1.compressed_key2)[15:0];
            meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = (meta.cmu_group1.compressed_key1 ^ meta.cmu_group1.compressed_key3)[15:0];
            meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = (meta.cmu_group1.compressed_key2 ^ meta.cmu_group1.compressed_key3)[15:0];
            meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu1.param.p1 =  meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu1.param.p1 =  meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu1.param.p1 =  meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu1.param.p1 =  meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu1.param.p1 =  meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu1.task_id = task_id;
            meta.cmu_group1.cmu1.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu1.param.p1 =  meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu1.param.p2 = meta.cmu_group1.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 1
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;
            set_cmu1_hkey3_cparam;
            set_cmu1_hkey12_cparam;
            set_cmu1_hkey13_cparam;
            set_cmu1_hkey23_cparam;

            set_cmu1_hkey1_hparam2;
            set_cmu1_hkey1_hparam3;

            set_cmu1_hkey2_hparam1;
            set_cmu1_hkey2_hparam3;


            set_cmu1_hkey3_hparam1;
            set_cmu1_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group1.cmu1.key = meta.cmu_group1.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group1.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group1.cmu1.key = meta.cmu_group1.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group1.cmu1.param.p1;
          // meta.cmu_group1.cmu1.param.p1 = meta.cmu_group1.cmu1.param.p2;
          // meta.cmu_group1.cmu1.param.p2 = temp;
    //}
    @pragma stage 2
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group1.cmu1.task_id : exact;
            meta.cmu_group1.cmu1.key     : ternary;
            meta.cmu_group1.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group1.cmu1.param.p2){
                value = value |+| meta.cmu_group1.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group1.cmu1.param.p1){
                value = meta.cmu_group1.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group1.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group1.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group1.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group1.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group1.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group1.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group1.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group1.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group1.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group1.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group1.cmu1.key[4:0]);
    //}

    @pragma stage 3
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group1.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu2_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = (meta.cmu_group1.compressed_key1 ^ meta.cmu_group1.compressed_key2)[15:0];
            meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = (meta.cmu_group1.compressed_key1 ^ meta.cmu_group1.compressed_key3)[15:0];
            meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = (meta.cmu_group1.compressed_key2 ^ meta.cmu_group1.compressed_key3)[15:0];
            meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu2.param.p1 =  meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu2.param.p1 =  meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu2.param.p1 =  meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu2.param.p1 =  meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu2.param.p1 =  meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu2.task_id = task_id;
            meta.cmu_group1.cmu2.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu2.param.p1 =  meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu2.param.p2 = meta.cmu_group1.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 1
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;
            set_cmu2_hkey3_cparam;
            set_cmu2_hkey12_cparam;
            set_cmu2_hkey13_cparam;
            set_cmu2_hkey23_cparam;

            set_cmu2_hkey1_hparam2;
            set_cmu2_hkey1_hparam3;

            set_cmu2_hkey2_hparam1;
            set_cmu2_hkey2_hparam3;


            set_cmu2_hkey3_hparam1;
            set_cmu2_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group1.cmu2.key = meta.cmu_group1.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group1.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group1.cmu2.key = meta.cmu_group1.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group1.cmu2.param.p1;
          // meta.cmu_group1.cmu2.param.p1 = meta.cmu_group1.cmu2.param.p2;
          // meta.cmu_group1.cmu2.param.p2 = temp;
    //}
    @pragma stage 2
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group1.cmu2.task_id : exact;
            meta.cmu_group1.cmu2.key     : ternary;
            meta.cmu_group1.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group1.cmu2.param.p2){
                value = value |+| meta.cmu_group1.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group1.cmu2.param.p1){
                value = meta.cmu_group1.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group1.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group1.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group1.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group1.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group1.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group1.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group1.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group1.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group1.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group1.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group1.cmu2.key[4:0]);
    //}

    @pragma stage 3
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group1.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu3_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = (meta.cmu_group1.compressed_key1 ^ meta.cmu_group1.compressed_key2)[15:0];
            meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = (meta.cmu_group1.compressed_key1 ^ meta.cmu_group1.compressed_key3)[15:0];
            meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = (meta.cmu_group1.compressed_key2 ^ meta.cmu_group1.compressed_key3)[15:0];
            meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu3.param.p1 =  meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu3.param.p1 =  meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu3.param.p1 =  meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu3.param.p1 =  meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu3.param.p1 =  meta.cmu_group1.compressed_key1[15:0];
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group1.cmu3.task_id = task_id;
            meta.cmu_group1.cmu3.key[15:0] = meta.cmu_group1.compressed_key3[15:0];
            meta.cmu_group1.cmu3.param.p1 =  meta.cmu_group1.compressed_key2[15:0];
            meta.cmu_group1.cmu3.param.p2 = meta.cmu_group1.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 1
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;
            set_cmu3_hkey3_cparam;
            set_cmu3_hkey12_cparam;
            set_cmu3_hkey13_cparam;
            set_cmu3_hkey23_cparam;

            set_cmu3_hkey1_hparam2;
            set_cmu3_hkey1_hparam3;

            set_cmu3_hkey2_hparam1;
            set_cmu3_hkey2_hparam3;


            set_cmu3_hkey3_hparam1;
            set_cmu3_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group1.cmu3.key = meta.cmu_group1.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group1.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group1.cmu3.key = meta.cmu_group1.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group1.cmu3.param.p1;
          // meta.cmu_group1.cmu3.param.p1 = meta.cmu_group1.cmu3.param.p2;
          // meta.cmu_group1.cmu3.param.p2 = temp;
    //}
    @pragma stage 2
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group1.cmu3.task_id : exact;
            meta.cmu_group1.cmu3.key     : ternary;
            meta.cmu_group1.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group1.cmu3.param.p2){
                value = value |+| meta.cmu_group1.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group1.cmu3.param.p1){
                value = meta.cmu_group1.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group1.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group1.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group1.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group1.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group1.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group1.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group1.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group1.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group1.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group1.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group1.cmu3.key[4:0]);
    //}

    @pragma stage 3
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group1.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG1.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 
        tbl_hash3.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG1.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG1.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG1.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group2


control CMU_Group2 ( in header_t hdr,
                               in ingress_intrinsic_metadata_t intr_md,
                               inout ingress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit3;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group2.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group2.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash3(){
        meta.cmu_group2.compressed_key3 = hash_unit3.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 1
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 1
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }
    @pragma stage 1
    table tbl_hash3{
        actions = {
            hash3;
        }
        const default_action = hash3();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu1_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = (meta.cmu_group2.compressed_key1 ^ meta.cmu_group2.compressed_key2)[15:0];
            meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = (meta.cmu_group2.compressed_key1 ^ meta.cmu_group2.compressed_key3)[15:0];
            meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = (meta.cmu_group2.compressed_key2 ^ meta.cmu_group2.compressed_key3)[15:0];
            meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu1.param.p1 =  meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu1.param.p1 =  meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu1.param.p1 =  meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu1.param.p1 =  meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu1.param.p1 =  meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu1.task_id = task_id;
            meta.cmu_group2.cmu1.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu1.param.p1 =  meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu1.param.p2 = meta.cmu_group2.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 2
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;
            set_cmu1_hkey3_cparam;
            set_cmu1_hkey12_cparam;
            set_cmu1_hkey13_cparam;
            set_cmu1_hkey23_cparam;

            set_cmu1_hkey1_hparam2;
            set_cmu1_hkey1_hparam3;

            set_cmu1_hkey2_hparam1;
            set_cmu1_hkey2_hparam3;


            set_cmu1_hkey3_hparam1;
            set_cmu1_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group2.cmu1.key = meta.cmu_group2.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group2.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group2.cmu1.key = meta.cmu_group2.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group2.cmu1.param.p1;
          // meta.cmu_group2.cmu1.param.p1 = meta.cmu_group2.cmu1.param.p2;
          // meta.cmu_group2.cmu1.param.p2 = temp;
    //}
    @pragma stage 3
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group2.cmu1.task_id : exact;
            meta.cmu_group2.cmu1.key     : ternary;
            meta.cmu_group2.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group2.cmu1.param.p2){
                value = value |+| meta.cmu_group2.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group2.cmu1.param.p1){
                value = meta.cmu_group2.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group2.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group2.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group2.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group2.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group2.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group2.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group2.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group2.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group2.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group2.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group2.cmu1.key[4:0]);
    //}

    @pragma stage 4
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group2.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu2_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = (meta.cmu_group2.compressed_key1 ^ meta.cmu_group2.compressed_key2)[15:0];
            meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = (meta.cmu_group2.compressed_key1 ^ meta.cmu_group2.compressed_key3)[15:0];
            meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = (meta.cmu_group2.compressed_key2 ^ meta.cmu_group2.compressed_key3)[15:0];
            meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu2.param.p1 =  meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu2.param.p1 =  meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu2.param.p1 =  meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu2.param.p1 =  meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu2.param.p1 =  meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu2.task_id = task_id;
            meta.cmu_group2.cmu2.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu2.param.p1 =  meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu2.param.p2 = meta.cmu_group2.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 2
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;
            set_cmu2_hkey3_cparam;
            set_cmu2_hkey12_cparam;
            set_cmu2_hkey13_cparam;
            set_cmu2_hkey23_cparam;

            set_cmu2_hkey1_hparam2;
            set_cmu2_hkey1_hparam3;

            set_cmu2_hkey2_hparam1;
            set_cmu2_hkey2_hparam3;


            set_cmu2_hkey3_hparam1;
            set_cmu2_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group2.cmu2.key = meta.cmu_group2.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group2.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group2.cmu2.key = meta.cmu_group2.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group2.cmu2.param.p1;
          // meta.cmu_group2.cmu2.param.p1 = meta.cmu_group2.cmu2.param.p2;
          // meta.cmu_group2.cmu2.param.p2 = temp;
    //}
    @pragma stage 3
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group2.cmu2.task_id : exact;
            meta.cmu_group2.cmu2.key     : ternary;
            meta.cmu_group2.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group2.cmu2.param.p2){
                value = value |+| meta.cmu_group2.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group2.cmu2.param.p1){
                value = meta.cmu_group2.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group2.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group2.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group2.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group2.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group2.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group2.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group2.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group2.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group2.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group2.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group2.cmu2.key[4:0]);
    //}

    @pragma stage 4
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group2.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu3_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = (meta.cmu_group2.compressed_key1 ^ meta.cmu_group2.compressed_key2)[15:0];
            meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = (meta.cmu_group2.compressed_key1 ^ meta.cmu_group2.compressed_key3)[15:0];
            meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = (meta.cmu_group2.compressed_key2 ^ meta.cmu_group2.compressed_key3)[15:0];
            meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu3.param.p1 =  meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu3.param.p1 =  meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu3.param.p1 =  meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu3.param.p1 =  meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu3.param.p1 =  meta.cmu_group2.compressed_key1[15:0];
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group2.cmu3.task_id = task_id;
            meta.cmu_group2.cmu3.key[15:0] = meta.cmu_group2.compressed_key3[15:0];
            meta.cmu_group2.cmu3.param.p1 =  meta.cmu_group2.compressed_key2[15:0];
            meta.cmu_group2.cmu3.param.p2 = meta.cmu_group2.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 2
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;
            set_cmu3_hkey3_cparam;
            set_cmu3_hkey12_cparam;
            set_cmu3_hkey13_cparam;
            set_cmu3_hkey23_cparam;

            set_cmu3_hkey1_hparam2;
            set_cmu3_hkey1_hparam3;

            set_cmu3_hkey2_hparam1;
            set_cmu3_hkey2_hparam3;


            set_cmu3_hkey3_hparam1;
            set_cmu3_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group2.cmu3.key = meta.cmu_group2.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group2.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group2.cmu3.key = meta.cmu_group2.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group2.cmu3.param.p1;
          // meta.cmu_group2.cmu3.param.p1 = meta.cmu_group2.cmu3.param.p2;
          // meta.cmu_group2.cmu3.param.p2 = temp;
    //}
    @pragma stage 3
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group2.cmu3.task_id : exact;
            meta.cmu_group2.cmu3.key     : ternary;
            meta.cmu_group2.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group2.cmu3.param.p2){
                value = value |+| meta.cmu_group2.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group2.cmu3.param.p1){
                value = meta.cmu_group2.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group2.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group2.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group2.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group2.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group2.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group2.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group2.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group2.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group2.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group2.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group2.cmu3.key[4:0]);
    //}

    @pragma stage 4
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group2.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG2.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 
        tbl_hash3.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG2.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG2.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG2.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group3


control CMU_Group3 ( in header_t hdr,
                               in ingress_intrinsic_metadata_t intr_md,
                               inout ingress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit3;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group3.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group3.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash3(){
        meta.cmu_group3.compressed_key3 = hash_unit3.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 2
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 2
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }
    @pragma stage 2
    table tbl_hash3{
        actions = {
            hash3;
        }
        const default_action = hash3();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu1_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = (meta.cmu_group3.compressed_key1 ^ meta.cmu_group3.compressed_key2)[15:0];
            meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = (meta.cmu_group3.compressed_key1 ^ meta.cmu_group3.compressed_key3)[15:0];
            meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = (meta.cmu_group3.compressed_key2 ^ meta.cmu_group3.compressed_key3)[15:0];
            meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu1.param.p1 =  meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu1.param.p1 =  meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu1.param.p1 =  meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu1.param.p1 =  meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu1.param.p1 =  meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu1.task_id = task_id;
            meta.cmu_group3.cmu1.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu1.param.p1 =  meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu1.param.p2 = meta.cmu_group3.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 3
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;
            set_cmu1_hkey3_cparam;
            set_cmu1_hkey12_cparam;
            set_cmu1_hkey13_cparam;
            set_cmu1_hkey23_cparam;

            set_cmu1_hkey1_hparam2;
            set_cmu1_hkey1_hparam3;

            set_cmu1_hkey2_hparam1;
            set_cmu1_hkey2_hparam3;


            set_cmu1_hkey3_hparam1;
            set_cmu1_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group3.cmu1.key = meta.cmu_group3.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group3.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group3.cmu1.key = meta.cmu_group3.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group3.cmu1.param.p1;
          // meta.cmu_group3.cmu1.param.p1 = meta.cmu_group3.cmu1.param.p2;
          // meta.cmu_group3.cmu1.param.p2 = temp;
    //}
    @pragma stage 4
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group3.cmu1.task_id : exact;
            meta.cmu_group3.cmu1.key     : ternary;
            meta.cmu_group3.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group3.cmu1.param.p2){
                value = value |+| meta.cmu_group3.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group3.cmu1.param.p1){
                value = meta.cmu_group3.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group3.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group3.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group3.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group3.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group3.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group3.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group3.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group3.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group3.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group3.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group3.cmu1.key[4:0]);
    //}

    @pragma stage 5
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group3.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu2_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = (meta.cmu_group3.compressed_key1 ^ meta.cmu_group3.compressed_key2)[15:0];
            meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = (meta.cmu_group3.compressed_key1 ^ meta.cmu_group3.compressed_key3)[15:0];
            meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = (meta.cmu_group3.compressed_key2 ^ meta.cmu_group3.compressed_key3)[15:0];
            meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu2.param.p1 =  meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu2.param.p1 =  meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu2.param.p1 =  meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu2.param.p1 =  meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu2.param.p1 =  meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu2.task_id = task_id;
            meta.cmu_group3.cmu2.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu2.param.p1 =  meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu2.param.p2 = meta.cmu_group3.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 3
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;
            set_cmu2_hkey3_cparam;
            set_cmu2_hkey12_cparam;
            set_cmu2_hkey13_cparam;
            set_cmu2_hkey23_cparam;

            set_cmu2_hkey1_hparam2;
            set_cmu2_hkey1_hparam3;

            set_cmu2_hkey2_hparam1;
            set_cmu2_hkey2_hparam3;


            set_cmu2_hkey3_hparam1;
            set_cmu2_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group3.cmu2.key = meta.cmu_group3.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group3.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group3.cmu2.key = meta.cmu_group3.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group3.cmu2.param.p1;
          // meta.cmu_group3.cmu2.param.p1 = meta.cmu_group3.cmu2.param.p2;
          // meta.cmu_group3.cmu2.param.p2 = temp;
    //}
    @pragma stage 4
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group3.cmu2.task_id : exact;
            meta.cmu_group3.cmu2.key     : ternary;
            meta.cmu_group3.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group3.cmu2.param.p2){
                value = value |+| meta.cmu_group3.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group3.cmu2.param.p1){
                value = meta.cmu_group3.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group3.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group3.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group3.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group3.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group3.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group3.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group3.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group3.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group3.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group3.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group3.cmu2.key[4:0]);
    //}

    @pragma stage 5
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group3.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu3_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = (meta.cmu_group3.compressed_key1 ^ meta.cmu_group3.compressed_key2)[15:0];
            meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = (meta.cmu_group3.compressed_key1 ^ meta.cmu_group3.compressed_key3)[15:0];
            meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = (meta.cmu_group3.compressed_key2 ^ meta.cmu_group3.compressed_key3)[15:0];
            meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu3.param.p1 =  meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu3.param.p1 =  meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu3.param.p1 =  meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu3.param.p1 =  meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu3.param.p1 =  meta.cmu_group3.compressed_key1[15:0];
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group3.cmu3.task_id = task_id;
            meta.cmu_group3.cmu3.key[15:0] = meta.cmu_group3.compressed_key3[15:0];
            meta.cmu_group3.cmu3.param.p1 =  meta.cmu_group3.compressed_key2[15:0];
            meta.cmu_group3.cmu3.param.p2 = meta.cmu_group3.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 3
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;
            set_cmu3_hkey3_cparam;
            set_cmu3_hkey12_cparam;
            set_cmu3_hkey13_cparam;
            set_cmu3_hkey23_cparam;

            set_cmu3_hkey1_hparam2;
            set_cmu3_hkey1_hparam3;

            set_cmu3_hkey2_hparam1;
            set_cmu3_hkey2_hparam3;


            set_cmu3_hkey3_hparam1;
            set_cmu3_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group3.cmu3.key = meta.cmu_group3.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group3.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group3.cmu3.key = meta.cmu_group3.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group3.cmu3.param.p1;
          // meta.cmu_group3.cmu3.param.p1 = meta.cmu_group3.cmu3.param.p2;
          // meta.cmu_group3.cmu3.param.p2 = temp;
    //}
    @pragma stage 4
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group3.cmu3.task_id : exact;
            meta.cmu_group3.cmu3.key     : ternary;
            meta.cmu_group3.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group3.cmu3.param.p2){
                value = value |+| meta.cmu_group3.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group3.cmu3.param.p1){
                value = meta.cmu_group3.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group3.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group3.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group3.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group3.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group3.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group3.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group3.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group3.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group3.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group3.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group3.cmu3.key[4:0]);
    //}

    @pragma stage 5
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group3.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG3.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 
        tbl_hash3.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG3.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG3.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG3.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group4


control CMU_Group4 ( in header_t hdr,
                               in ingress_intrinsic_metadata_t intr_md,
                               inout ingress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit3;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group4.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group4.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash3(){
        meta.cmu_group4.compressed_key3 = hash_unit3.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 3
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 3
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }
    @pragma stage 3
    table tbl_hash3{
        actions = {
            hash3;
        }
        const default_action = hash3();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu1_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = (meta.cmu_group4.compressed_key1 ^ meta.cmu_group4.compressed_key2)[15:0];
            meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = (meta.cmu_group4.compressed_key1 ^ meta.cmu_group4.compressed_key3)[15:0];
            meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu1_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = (meta.cmu_group4.compressed_key2 ^ meta.cmu_group4.compressed_key3)[15:0];
            meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu1.param.p1 =  meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu1.param.p1 =  meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu1.param.p1 =  meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu1_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu1.param.p1 =  meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu1.param.p1 =  meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu1_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu1.task_id = task_id;
            meta.cmu_group4.cmu1.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu1.param.p1 =  meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu1.param.p2 = meta.cmu_group4.cmu1.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 4
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;
            set_cmu1_hkey3_cparam;
            set_cmu1_hkey12_cparam;
            set_cmu1_hkey13_cparam;
            set_cmu1_hkey23_cparam;

            set_cmu1_hkey1_hparam2;
            set_cmu1_hkey1_hparam3;

            set_cmu1_hkey2_hparam1;
            set_cmu1_hkey2_hparam3;


            set_cmu1_hkey3_hparam1;
            set_cmu1_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group4.cmu1.key = meta.cmu_group4.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group4.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group4.cmu1.key = meta.cmu_group4.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group4.cmu1.param.p1;
          // meta.cmu_group4.cmu1.param.p1 = meta.cmu_group4.cmu1.param.p2;
          // meta.cmu_group4.cmu1.param.p2 = temp;
    //}
    @pragma stage 5
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group4.cmu1.task_id : exact;
            meta.cmu_group4.cmu1.key     : ternary;
            meta.cmu_group4.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group4.cmu1.param.p2){
                value = value |+| meta.cmu_group4.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group4.cmu1.param.p1){
                value = meta.cmu_group4.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group4.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group4.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group4.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group4.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group4.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group4.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group4.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group4.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group4.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group4.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group4.cmu1.key[4:0]);
    //}

    @pragma stage 6
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group4.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu2_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = (meta.cmu_group4.compressed_key1 ^ meta.cmu_group4.compressed_key2)[15:0];
            meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = (meta.cmu_group4.compressed_key1 ^ meta.cmu_group4.compressed_key3)[15:0];
            meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu2_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = (meta.cmu_group4.compressed_key2 ^ meta.cmu_group4.compressed_key3)[15:0];
            meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu2.param.p1 =  meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu2.param.p1 =  meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu2.param.p1 =  meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu2_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu2.param.p1 =  meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu2.param.p1 =  meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu2_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu2.task_id = task_id;
            meta.cmu_group4.cmu2.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu2.param.p1 =  meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu2.param.p2 = meta.cmu_group4.cmu2.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 4
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;
            set_cmu2_hkey3_cparam;
            set_cmu2_hkey12_cparam;
            set_cmu2_hkey13_cparam;
            set_cmu2_hkey23_cparam;

            set_cmu2_hkey1_hparam2;
            set_cmu2_hkey1_hparam3;

            set_cmu2_hkey2_hparam1;
            set_cmu2_hkey2_hparam3;


            set_cmu2_hkey3_hparam1;
            set_cmu2_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group4.cmu2.key = meta.cmu_group4.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group4.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group4.cmu2.key = meta.cmu_group4.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group4.cmu2.param.p1;
          // meta.cmu_group4.cmu2.param.p1 = meta.cmu_group4.cmu2.param.p2;
          // meta.cmu_group4.cmu2.param.p2 = temp;
    //}
    @pragma stage 5
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group4.cmu2.task_id : exact;
            meta.cmu_group4.cmu2.key     : ternary;
            meta.cmu_group4.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group4.cmu2.param.p2){
                value = value |+| meta.cmu_group4.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group4.cmu2.param.p1){
                value = meta.cmu_group4.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group4.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group4.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group4.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group4.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group4.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group4.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group4.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group4.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group4.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group4.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group4.cmu2.key[4:0]);
    //}

    @pragma stage 6
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group4.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }

    action set_cmu3_hkey3_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey12_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = (meta.cmu_group4.compressed_key1 ^ meta.cmu_group4.compressed_key2)[15:0];
            meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey13_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = (meta.cmu_group4.compressed_key1 ^ meta.cmu_group4.compressed_key3)[15:0];
            meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }
    action set_cmu3_hkey23_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = (meta.cmu_group4.compressed_key2 ^ meta.cmu_group4.compressed_key3)[15:0];
            meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }


    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu3.param.p1 =  meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey1_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu3.param.p1 =  meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu3.param.p1 =  meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }

    action set_cmu3_hkey2_hparam3(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu3.param.p1 =  meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu3.param.p1 =  meta.cmu_group4.compressed_key1[15:0];
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }
    action set_cmu3_hkey3_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group4.cmu3.task_id = task_id;
            meta.cmu_group4.cmu3.key[15:0] = meta.cmu_group4.compressed_key3[15:0];
            meta.cmu_group4.cmu3.param.p1 =  meta.cmu_group4.compressed_key2[15:0];
            meta.cmu_group4.cmu3.param.p2 = meta.cmu_group4.cmu3.param.p2 + param2;   // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 4
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;
            set_cmu3_hkey3_cparam;
            set_cmu3_hkey12_cparam;
            set_cmu3_hkey13_cparam;
            set_cmu3_hkey23_cparam;

            set_cmu3_hkey1_hparam2;
            set_cmu3_hkey1_hparam3;

            set_cmu3_hkey2_hparam1;
            set_cmu3_hkey2_hparam3;


            set_cmu3_hkey3_hparam1;
            set_cmu3_hkey3_hparam2;

        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group4.cmu3.key = meta.cmu_group4.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group4.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group4.cmu3.key = meta.cmu_group4.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group4.cmu3.param.p1;
          // meta.cmu_group4.cmu3.param.p1 = meta.cmu_group4.cmu3.param.p2;
          // meta.cmu_group4.cmu3.param.p2 = temp;
    //}
    @pragma stage 5
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group4.cmu3.task_id : exact;
            meta.cmu_group4.cmu3.key     : ternary;
            meta.cmu_group4.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group4.cmu3.param.p2){
                value = value |+| meta.cmu_group4.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group4.cmu3.param.p1){
                value = meta.cmu_group4.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group4.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group4.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group4.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group4.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group4.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group4.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group4.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group4.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group4.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group4.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group4.cmu3.key[4:0]);
    //}

    @pragma stage 6
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group4.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG4.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 
        tbl_hash3.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG4.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG4.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG4.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group5


control CMU_Group5 ( in header_t hdr,
                               in egress_intrinsic_metadata_t intr_md,
                               inout egress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group5.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group5.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 4
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 4
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu1.param.p1 = meta.cmu_group5.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu1.param.p1 = meta.cmu_group5.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu1.param.p1 =  meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu1.param.p1 =  meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    action set_cmu1_hkey1_pkt_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu1.param.p1 =  (bit<16>) intr_md.pkt_length;
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2; 
    }
    action set_cmu1_hkey2_pkt_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu1.param.p1 =  (bit<16>) intr_md.pkt_length;
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2; 
    }
    action set_cmu1_hkey1_queue_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu1.param.p1 =  intr_md.enq_qdepth[15:0];
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2; 
    }
    action set_cmu1_hkey2_queue_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu1.param.p1 =  intr_md.enq_qdepth[15:0];
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2; 
    }
    action set_cmu1_hkey1_timestamp(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu1.param.p1 =  intr_md.enq_tstamp[15:0];;
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2; 
    }
    action set_cmu1_hkey2_timestamp(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu1.task_id = task_id;
            meta.cmu_group5.cmu1.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu1.param.p1 =  intr_md.enq_tstamp[15:0];;
            meta.cmu_group5.cmu1.param.p2 = meta.cmu_group5.cmu1.param.p2 + param2; 
    }
    
    @pragma stage 5
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;

            set_cmu1_hkey1_hparam2;

            set_cmu1_hkey2_hparam1;



            set_cmu1_hkey1_pkt_size;
            set_cmu1_hkey1_queue_size;
            set_cmu1_hkey1_timestamp;
        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group5.cmu1.key = meta.cmu_group5.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group5.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group5.cmu1.key = meta.cmu_group5.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group5.cmu1.param.p1;
          // meta.cmu_group5.cmu1.param.p1 = meta.cmu_group5.cmu1.param.p2;
          // meta.cmu_group5.cmu1.param.p2 = temp;
    //}
    @pragma stage 6
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group5.cmu1.task_id : exact;
            meta.cmu_group5.cmu1.key     : ternary;
            meta.cmu_group5.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group5.cmu1.param.p2){
                value = value |+| meta.cmu_group5.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group5.cmu1.param.p1){
                value = meta.cmu_group5.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group5.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group5.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group5.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group9.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group5.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        // chain the CMU Group 5 and CMU Group 9
        meta.cmu_group9.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group5.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group9.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group5.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group5.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group5.cmu1.key[4:0]);
    //}

    @pragma stage 7
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group5.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key1[23:8];
            meta.cmu_group5.cmu2.param.p1 = meta.cmu_group5.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu2.param.p1 = meta.cmu_group5.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key1[23:8];
            meta.cmu_group5.cmu2.param.p1 =  meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu2.param.p1 =  meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    action set_cmu2_hkey1_pkt_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key1[23:8];
            meta.cmu_group5.cmu2.param.p1 =  (bit<16>) intr_md.pkt_length;
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2; 
    }
    action set_cmu2_hkey2_pkt_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu2.param.p1 =  (bit<16>) intr_md.pkt_length;
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2; 
    }
    action set_cmu2_hkey1_queue_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key1[23:8];
            meta.cmu_group5.cmu2.param.p1 =  intr_md.enq_qdepth[15:0];
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2; 
    }
    action set_cmu2_hkey2_queue_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu2.param.p1 =  intr_md.enq_qdepth[15:0];
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2; 
    }
    action set_cmu2_hkey1_timestamp(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key1[23:8];
            meta.cmu_group5.cmu2.param.p1 =  intr_md.enq_tstamp[15:0];;
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2; 
    }
    action set_cmu2_hkey2_timestamp(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu2.task_id = task_id;
            meta.cmu_group5.cmu2.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu2.param.p1 =  intr_md.enq_tstamp[15:0];;
            meta.cmu_group5.cmu2.param.p2 = meta.cmu_group5.cmu2.param.p2 + param2; 
    }
    
    @pragma stage 5
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;

            set_cmu2_hkey1_hparam2;

            set_cmu2_hkey2_hparam1;



            set_cmu2_hkey1_pkt_size;
            set_cmu2_hkey1_queue_size;
            set_cmu2_hkey1_timestamp;
        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group5.cmu2.key = meta.cmu_group5.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group5.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group5.cmu2.key = meta.cmu_group5.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group5.cmu2.param.p1;
          // meta.cmu_group5.cmu2.param.p1 = meta.cmu_group5.cmu2.param.p2;
          // meta.cmu_group5.cmu2.param.p2 = temp;
    //}
    @pragma stage 6
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group5.cmu2.task_id : exact;
            meta.cmu_group5.cmu2.key     : ternary;
            meta.cmu_group5.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group5.cmu2.param.p2){
                value = value |+| meta.cmu_group5.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group5.cmu2.param.p1){
                value = meta.cmu_group5.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group5.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group5.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group5.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group9.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group5.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        // chain the CMU Group 5 and CMU Group 9
        meta.cmu_group9.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group5.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group9.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group5.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group5.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group5.cmu2.key[4:0]);
    //}

    @pragma stage 7
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group5.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key1[31:16];
            meta.cmu_group5.cmu3.param.p1 = meta.cmu_group5.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu3.param.p1 = meta.cmu_group5.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key1[31:16];
            meta.cmu_group5.cmu3.param.p1 =  meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu3.param.p1 =  meta.cmu_group5.compressed_key1[15:0];
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    action set_cmu3_hkey1_pkt_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key1[31:16];
            meta.cmu_group5.cmu3.param.p1 =  (bit<16>) intr_md.pkt_length;
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2; 
    }
    action set_cmu3_hkey2_pkt_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu3.param.p1 =  (bit<16>) intr_md.pkt_length;
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2; 
    }
    action set_cmu3_hkey1_queue_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key1[31:16];
            meta.cmu_group5.cmu3.param.p1 =  intr_md.enq_qdepth[15:0];
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2; 
    }
    action set_cmu3_hkey2_queue_size(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu3.param.p1 =  intr_md.enq_qdepth[15:0];
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2; 
    }
    action set_cmu3_hkey1_timestamp(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key1[31:16];
            meta.cmu_group5.cmu3.param.p1 =  intr_md.enq_tstamp[15:0];;
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2; 
    }
    action set_cmu3_hkey2_timestamp(bit<8> task_id, bit<16> param2) {
            meta.cmu_group5.cmu3.task_id = task_id;
            meta.cmu_group5.cmu3.key[15:0] = meta.cmu_group5.compressed_key2[15:0];
            meta.cmu_group5.cmu3.param.p1 =  intr_md.enq_tstamp[15:0];;
            meta.cmu_group5.cmu3.param.p2 = meta.cmu_group5.cmu3.param.p2 + param2; 
    }
    
    @pragma stage 5
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;

            set_cmu3_hkey1_hparam2;

            set_cmu3_hkey2_hparam1;



            set_cmu3_hkey1_pkt_size;
            set_cmu3_hkey1_queue_size;
            set_cmu3_hkey1_timestamp;
        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group5.cmu3.key = meta.cmu_group5.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group5.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group5.cmu3.key = meta.cmu_group5.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group5.cmu3.param.p1;
          // meta.cmu_group5.cmu3.param.p1 = meta.cmu_group5.cmu3.param.p2;
          // meta.cmu_group5.cmu3.param.p2 = temp;
    //}
    @pragma stage 6
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group5.cmu3.task_id : exact;
            meta.cmu_group5.cmu3.key     : ternary;
            meta.cmu_group5.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group5.cmu3.param.p2){
                value = value |+| meta.cmu_group5.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group5.cmu3.param.p1){
                value = meta.cmu_group5.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group5.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group5.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group5.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group9.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group5.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        // chain the CMU Group 5 and CMU Group 9
        meta.cmu_group9.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group5.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group9.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group5.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group5.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group5.cmu3.key[4:0]);
    //}

    @pragma stage 7
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group5.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG5.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG5.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG5.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG5.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group6


control CMU_Group6 ( in header_t hdr,
                               in egress_intrinsic_metadata_t intr_md,
                               inout egress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group6.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group6.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 5
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 5
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group6.cmu1.task_id = task_id;
            meta.cmu_group6.cmu1.key[15:0] = meta.cmu_group6.compressed_key1[15:0];
            meta.cmu_group6.cmu1.param.p1 = meta.cmu_group6.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group6.cmu1.param.p2 = meta.cmu_group6.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group6.cmu1.task_id = task_id;
            meta.cmu_group6.cmu1.key[15:0] = meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu1.param.p1 = meta.cmu_group6.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group6.cmu1.param.p2 = meta.cmu_group6.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group6.cmu1.task_id = task_id;
            meta.cmu_group6.cmu1.key[15:0] = meta.cmu_group6.compressed_key1[15:0];
            meta.cmu_group6.cmu1.param.p1 =  meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu1.param.p2 = meta.cmu_group6.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group6.cmu1.task_id = task_id;
            meta.cmu_group6.cmu1.key[15:0] = meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu1.param.p1 =  meta.cmu_group6.compressed_key1[15:0];
            meta.cmu_group6.cmu1.param.p2 = meta.cmu_group6.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 6
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;

            set_cmu1_hkey1_hparam2;

            set_cmu1_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group6.cmu1.key = meta.cmu_group6.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group6.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group6.cmu1.key = meta.cmu_group6.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group6.cmu1.param.p1;
          // meta.cmu_group6.cmu1.param.p1 = meta.cmu_group6.cmu1.param.p2;
          // meta.cmu_group6.cmu1.param.p2 = temp;
    //}
    @pragma stage 7
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group6.cmu1.task_id : exact;
            meta.cmu_group6.cmu1.key     : ternary;
            meta.cmu_group6.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group6.cmu1.param.p2){
                value = value |+| meta.cmu_group6.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group6.cmu1.param.p1){
                value = meta.cmu_group6.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group6.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group6.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group6.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group6.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group6.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group6.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group6.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group6.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group6.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group6.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group6.cmu1.key[4:0]);
    //}

    @pragma stage 8
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group6.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group6.cmu2.task_id = task_id;
            meta.cmu_group6.cmu2.key[15:0] = meta.cmu_group6.compressed_key1[23:8];
            meta.cmu_group6.cmu2.param.p1 = meta.cmu_group6.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group6.cmu2.param.p2 = meta.cmu_group6.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group6.cmu2.task_id = task_id;
            meta.cmu_group6.cmu2.key[15:0] = meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu2.param.p1 = meta.cmu_group6.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group6.cmu2.param.p2 = meta.cmu_group6.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group6.cmu2.task_id = task_id;
            meta.cmu_group6.cmu2.key[15:0] = meta.cmu_group6.compressed_key1[23:8];
            meta.cmu_group6.cmu2.param.p1 =  meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu2.param.p2 = meta.cmu_group6.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group6.cmu2.task_id = task_id;
            meta.cmu_group6.cmu2.key[15:0] = meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu2.param.p1 =  meta.cmu_group6.compressed_key1[15:0];
            meta.cmu_group6.cmu2.param.p2 = meta.cmu_group6.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 6
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;

            set_cmu2_hkey1_hparam2;

            set_cmu2_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group6.cmu2.key = meta.cmu_group6.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group6.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group6.cmu2.key = meta.cmu_group6.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group6.cmu2.param.p1;
          // meta.cmu_group6.cmu2.param.p1 = meta.cmu_group6.cmu2.param.p2;
          // meta.cmu_group6.cmu2.param.p2 = temp;
    //}
    @pragma stage 7
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group6.cmu2.task_id : exact;
            meta.cmu_group6.cmu2.key     : ternary;
            meta.cmu_group6.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group6.cmu2.param.p2){
                value = value |+| meta.cmu_group6.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group6.cmu2.param.p1){
                value = meta.cmu_group6.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group6.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group6.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group6.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group6.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group6.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group6.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group6.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group6.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group6.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group6.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group6.cmu2.key[4:0]);
    //}

    @pragma stage 8
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group6.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group6.cmu3.task_id = task_id;
            meta.cmu_group6.cmu3.key[15:0] = meta.cmu_group6.compressed_key1[31:16];
            meta.cmu_group6.cmu3.param.p1 = meta.cmu_group6.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group6.cmu3.param.p2 = meta.cmu_group6.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group6.cmu3.task_id = task_id;
            meta.cmu_group6.cmu3.key[15:0] = meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu3.param.p1 = meta.cmu_group6.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group6.cmu3.param.p2 = meta.cmu_group6.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group6.cmu3.task_id = task_id;
            meta.cmu_group6.cmu3.key[15:0] = meta.cmu_group6.compressed_key1[31:16];
            meta.cmu_group6.cmu3.param.p1 =  meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu3.param.p2 = meta.cmu_group6.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group6.cmu3.task_id = task_id;
            meta.cmu_group6.cmu3.key[15:0] = meta.cmu_group6.compressed_key2[15:0];
            meta.cmu_group6.cmu3.param.p1 =  meta.cmu_group6.compressed_key1[15:0];
            meta.cmu_group6.cmu3.param.p2 = meta.cmu_group6.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 6
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;

            set_cmu3_hkey1_hparam2;

            set_cmu3_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group6.cmu3.key = meta.cmu_group6.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group6.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group6.cmu3.key = meta.cmu_group6.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group6.cmu3.param.p1;
          // meta.cmu_group6.cmu3.param.p1 = meta.cmu_group6.cmu3.param.p2;
          // meta.cmu_group6.cmu3.param.p2 = temp;
    //}
    @pragma stage 7
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group6.cmu3.task_id : exact;
            meta.cmu_group6.cmu3.key     : ternary;
            meta.cmu_group6.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group6.cmu3.param.p2){
                value = value |+| meta.cmu_group6.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group6.cmu3.param.p1){
                value = meta.cmu_group6.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group6.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group6.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group6.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group6.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group6.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group6.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group6.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group6.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group6.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group6.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group6.cmu3.key[4:0]);
    //}

    @pragma stage 8
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group6.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG6.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG6.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG6.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG6.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group7


control CMU_Group7 ( in header_t hdr,
                               in egress_intrinsic_metadata_t intr_md,
                               inout egress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group7.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group7.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 6
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 6
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group7.cmu1.task_id = task_id;
            meta.cmu_group7.cmu1.key[15:0] = meta.cmu_group7.compressed_key1[15:0];
            meta.cmu_group7.cmu1.param.p1 = meta.cmu_group7.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group7.cmu1.param.p2 = meta.cmu_group7.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group7.cmu1.task_id = task_id;
            meta.cmu_group7.cmu1.key[15:0] = meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu1.param.p1 = meta.cmu_group7.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group7.cmu1.param.p2 = meta.cmu_group7.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group7.cmu1.task_id = task_id;
            meta.cmu_group7.cmu1.key[15:0] = meta.cmu_group7.compressed_key1[15:0];
            meta.cmu_group7.cmu1.param.p1 =  meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu1.param.p2 = meta.cmu_group7.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group7.cmu1.task_id = task_id;
            meta.cmu_group7.cmu1.key[15:0] = meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu1.param.p1 =  meta.cmu_group7.compressed_key1[15:0];
            meta.cmu_group7.cmu1.param.p2 = meta.cmu_group7.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 7
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;

            set_cmu1_hkey1_hparam2;

            set_cmu1_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group7.cmu1.key = meta.cmu_group7.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group7.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group7.cmu1.key = meta.cmu_group7.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group7.cmu1.param.p1;
          // meta.cmu_group7.cmu1.param.p1 = meta.cmu_group7.cmu1.param.p2;
          // meta.cmu_group7.cmu1.param.p2 = temp;
    //}
    @pragma stage 8
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group7.cmu1.task_id : exact;
            meta.cmu_group7.cmu1.key     : ternary;
            meta.cmu_group7.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group7.cmu1.param.p2){
                value = value |+| meta.cmu_group7.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group7.cmu1.param.p1){
                value = meta.cmu_group7.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group7.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group7.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group7.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group7.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group7.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group7.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group7.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group7.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group7.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group7.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group7.cmu1.key[4:0]);
    //}

    @pragma stage 9
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group7.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group7.cmu2.task_id = task_id;
            meta.cmu_group7.cmu2.key[15:0] = meta.cmu_group7.compressed_key1[23:8];
            meta.cmu_group7.cmu2.param.p1 = meta.cmu_group7.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group7.cmu2.param.p2 = meta.cmu_group7.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group7.cmu2.task_id = task_id;
            meta.cmu_group7.cmu2.key[15:0] = meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu2.param.p1 = meta.cmu_group7.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group7.cmu2.param.p2 = meta.cmu_group7.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group7.cmu2.task_id = task_id;
            meta.cmu_group7.cmu2.key[15:0] = meta.cmu_group7.compressed_key1[23:8];
            meta.cmu_group7.cmu2.param.p1 =  meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu2.param.p2 = meta.cmu_group7.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group7.cmu2.task_id = task_id;
            meta.cmu_group7.cmu2.key[15:0] = meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu2.param.p1 =  meta.cmu_group7.compressed_key1[15:0];
            meta.cmu_group7.cmu2.param.p2 = meta.cmu_group7.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 7
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;

            set_cmu2_hkey1_hparam2;

            set_cmu2_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group7.cmu2.key = meta.cmu_group7.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group7.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group7.cmu2.key = meta.cmu_group7.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group7.cmu2.param.p1;
          // meta.cmu_group7.cmu2.param.p1 = meta.cmu_group7.cmu2.param.p2;
          // meta.cmu_group7.cmu2.param.p2 = temp;
    //}
    @pragma stage 8
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group7.cmu2.task_id : exact;
            meta.cmu_group7.cmu2.key     : ternary;
            meta.cmu_group7.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group7.cmu2.param.p2){
                value = value |+| meta.cmu_group7.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group7.cmu2.param.p1){
                value = meta.cmu_group7.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group7.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group7.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group7.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group7.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group7.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group7.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group7.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group7.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group7.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group7.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group7.cmu2.key[4:0]);
    //}

    @pragma stage 9
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group7.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group7.cmu3.task_id = task_id;
            meta.cmu_group7.cmu3.key[15:0] = meta.cmu_group7.compressed_key1[31:16];
            meta.cmu_group7.cmu3.param.p1 = meta.cmu_group7.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group7.cmu3.param.p2 = meta.cmu_group7.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group7.cmu3.task_id = task_id;
            meta.cmu_group7.cmu3.key[15:0] = meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu3.param.p1 = meta.cmu_group7.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group7.cmu3.param.p2 = meta.cmu_group7.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group7.cmu3.task_id = task_id;
            meta.cmu_group7.cmu3.key[15:0] = meta.cmu_group7.compressed_key1[31:16];
            meta.cmu_group7.cmu3.param.p1 =  meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu3.param.p2 = meta.cmu_group7.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group7.cmu3.task_id = task_id;
            meta.cmu_group7.cmu3.key[15:0] = meta.cmu_group7.compressed_key2[15:0];
            meta.cmu_group7.cmu3.param.p1 =  meta.cmu_group7.compressed_key1[15:0];
            meta.cmu_group7.cmu3.param.p2 = meta.cmu_group7.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 7
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;

            set_cmu3_hkey1_hparam2;

            set_cmu3_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group7.cmu3.key = meta.cmu_group7.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group7.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group7.cmu3.key = meta.cmu_group7.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group7.cmu3.param.p1;
          // meta.cmu_group7.cmu3.param.p1 = meta.cmu_group7.cmu3.param.p2;
          // meta.cmu_group7.cmu3.param.p2 = temp;
    //}
    @pragma stage 8
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group7.cmu3.task_id : exact;
            meta.cmu_group7.cmu3.key     : ternary;
            meta.cmu_group7.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group7.cmu3.param.p2){
                value = value |+| meta.cmu_group7.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group7.cmu3.param.p1){
                value = meta.cmu_group7.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group7.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group7.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group7.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group7.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group7.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group7.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group7.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group7.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group7.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group7.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group7.cmu3.key[4:0]);
    //}

    @pragma stage 9
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group7.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG7.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG7.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG7.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG7.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group8


control CMU_Group8 ( in header_t hdr,
                               in egress_intrinsic_metadata_t intr_md,
                               inout egress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group8.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group8.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 7
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 7
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group8.cmu1.task_id = task_id;
            meta.cmu_group8.cmu1.key[15:0] = meta.cmu_group8.compressed_key1[15:0];
            meta.cmu_group8.cmu1.param.p1 = meta.cmu_group8.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group8.cmu1.param.p2 = meta.cmu_group8.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group8.cmu1.task_id = task_id;
            meta.cmu_group8.cmu1.key[15:0] = meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu1.param.p1 = meta.cmu_group8.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group8.cmu1.param.p2 = meta.cmu_group8.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group8.cmu1.task_id = task_id;
            meta.cmu_group8.cmu1.key[15:0] = meta.cmu_group8.compressed_key1[15:0];
            meta.cmu_group8.cmu1.param.p1 =  meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu1.param.p2 = meta.cmu_group8.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group8.cmu1.task_id = task_id;
            meta.cmu_group8.cmu1.key[15:0] = meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu1.param.p1 =  meta.cmu_group8.compressed_key1[15:0];
            meta.cmu_group8.cmu1.param.p2 = meta.cmu_group8.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 8
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;

            set_cmu1_hkey1_hparam2;

            set_cmu1_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group8.cmu1.key = meta.cmu_group8.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group8.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group8.cmu1.key = meta.cmu_group8.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group8.cmu1.param.p1;
          // meta.cmu_group8.cmu1.param.p1 = meta.cmu_group8.cmu1.param.p2;
          // meta.cmu_group8.cmu1.param.p2 = temp;
    //}
    @pragma stage 9
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group8.cmu1.task_id : exact;
            meta.cmu_group8.cmu1.key     : ternary;
            meta.cmu_group8.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group8.cmu1.param.p2){
                value = value |+| meta.cmu_group8.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group8.cmu1.param.p1){
                value = meta.cmu_group8.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group8.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group8.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group8.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group8.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group8.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group8.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group8.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group8.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group8.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group8.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group8.cmu1.key[4:0]);
    //}

    @pragma stage 10
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group8.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group8.cmu2.task_id = task_id;
            meta.cmu_group8.cmu2.key[15:0] = meta.cmu_group8.compressed_key1[23:8];
            meta.cmu_group8.cmu2.param.p1 = meta.cmu_group8.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group8.cmu2.param.p2 = meta.cmu_group8.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group8.cmu2.task_id = task_id;
            meta.cmu_group8.cmu2.key[15:0] = meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu2.param.p1 = meta.cmu_group8.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group8.cmu2.param.p2 = meta.cmu_group8.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group8.cmu2.task_id = task_id;
            meta.cmu_group8.cmu2.key[15:0] = meta.cmu_group8.compressed_key1[23:8];
            meta.cmu_group8.cmu2.param.p1 =  meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu2.param.p2 = meta.cmu_group8.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group8.cmu2.task_id = task_id;
            meta.cmu_group8.cmu2.key[15:0] = meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu2.param.p1 =  meta.cmu_group8.compressed_key1[15:0];
            meta.cmu_group8.cmu2.param.p2 = meta.cmu_group8.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 8
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;

            set_cmu2_hkey1_hparam2;

            set_cmu2_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group8.cmu2.key = meta.cmu_group8.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group8.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group8.cmu2.key = meta.cmu_group8.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group8.cmu2.param.p1;
          // meta.cmu_group8.cmu2.param.p1 = meta.cmu_group8.cmu2.param.p2;
          // meta.cmu_group8.cmu2.param.p2 = temp;
    //}
    @pragma stage 9
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group8.cmu2.task_id : exact;
            meta.cmu_group8.cmu2.key     : ternary;
            meta.cmu_group8.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group8.cmu2.param.p2){
                value = value |+| meta.cmu_group8.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group8.cmu2.param.p1){
                value = meta.cmu_group8.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group8.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group8.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group8.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group8.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group8.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group8.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group8.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group8.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group8.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group8.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group8.cmu2.key[4:0]);
    //}

    @pragma stage 10
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group8.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group8.cmu3.task_id = task_id;
            meta.cmu_group8.cmu3.key[15:0] = meta.cmu_group8.compressed_key1[31:16];
            meta.cmu_group8.cmu3.param.p1 = meta.cmu_group8.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group8.cmu3.param.p2 = meta.cmu_group8.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group8.cmu3.task_id = task_id;
            meta.cmu_group8.cmu3.key[15:0] = meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu3.param.p1 = meta.cmu_group8.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group8.cmu3.param.p2 = meta.cmu_group8.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group8.cmu3.task_id = task_id;
            meta.cmu_group8.cmu3.key[15:0] = meta.cmu_group8.compressed_key1[31:16];
            meta.cmu_group8.cmu3.param.p1 =  meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu3.param.p2 = meta.cmu_group8.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group8.cmu3.task_id = task_id;
            meta.cmu_group8.cmu3.key[15:0] = meta.cmu_group8.compressed_key2[15:0];
            meta.cmu_group8.cmu3.param.p1 =  meta.cmu_group8.compressed_key1[15:0];
            meta.cmu_group8.cmu3.param.p2 = meta.cmu_group8.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 8
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;

            set_cmu3_hkey1_hparam2;

            set_cmu3_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group8.cmu3.key = meta.cmu_group8.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group8.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group8.cmu3.key = meta.cmu_group8.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group8.cmu3.param.p1;
          // meta.cmu_group8.cmu3.param.p1 = meta.cmu_group8.cmu3.param.p2;
          // meta.cmu_group8.cmu3.param.p2 = temp;
    //}
    @pragma stage 9
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group8.cmu3.task_id : exact;
            meta.cmu_group8.cmu3.key     : ternary;
            meta.cmu_group8.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group8.cmu3.param.p2){
                value = value |+| meta.cmu_group8.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group8.cmu3.param.p1){
                value = meta.cmu_group8.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group8.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group8.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group8.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group8.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group8.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group8.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group8.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group8.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group8.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group8.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group8.cmu3.key[4:0]);
    //}

    @pragma stage 10
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group8.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG8.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG8.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG8.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG8.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
// Definition for CMU-Group9


control CMU_Group9 ( in header_t hdr,
                               in egress_intrinsic_metadata_t intr_md,
                               inout egress_metadata_t meta )
{
    action no_action(){}

    // Definition for Shared Compresstion Stage.
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit1;
    Hash<bit<16>>(HashAlgorithm_t.CRC32) hash_unit2;

    // The hash inputs are fixed here. There are two ways to generate different hash values.
    //  a) Firstly, use different sub-range in the initialization stage.
    //  b) Secondly, add salts to hash outputs in the control plane.
    action hash1(){
        meta.cmu_group9.compressed_key1 = hash_unit1.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }
    action hash2(){
        meta.cmu_group9.compressed_key2 = hash_unit2.get({ hdr.ipv4.src_addr,hdr.ipv4.dst_addr,hdr.ports.src_port,hdr.ports.dst_port,hdr.ipv4.protocol });
    }

    @pragma stage 8
    table tbl_hash1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    @pragma stage 8
    table tbl_hash2{
        actions = {
            hash2;
        }
        const default_action = hash2();
        size = 1;
    }

    // Definition for Other Stages of Each CMU (SALU).
    // Initialization stage of CMU0.
    action set_cmu1_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group9.cmu1.task_id = task_id;
            meta.cmu_group9.cmu1.key[15:0] = meta.cmu_group9.compressed_key1[15:0];
            meta.cmu_group9.cmu1.param.p1 = meta.cmu_group9.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group9.cmu1.param.p2 = meta.cmu_group9.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu1_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group9.cmu1.task_id = task_id;
            meta.cmu_group9.cmu1.key[15:0] = meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu1.param.p1 = meta.cmu_group9.cmu1.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group9.cmu1.param.p2 = meta.cmu_group9.cmu1.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu1_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group9.cmu1.task_id = task_id;
            meta.cmu_group9.cmu1.key[15:0] = meta.cmu_group9.compressed_key1[15:0];
            meta.cmu_group9.cmu1.param.p1 =  meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu1.param.p2 = meta.cmu_group9.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu1_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group9.cmu1.task_id = task_id;
            meta.cmu_group9.cmu1.key[15:0] = meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu1.param.p1 =  meta.cmu_group9.compressed_key1[15:0];
            meta.cmu_group9.cmu1.param.p2 = meta.cmu_group9.cmu1.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 9
    table tbl_cmu1_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu1_hkey1_cparam;
            set_cmu1_hkey2_cparam;

            set_cmu1_hkey1_hparam2;

            set_cmu1_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU0.
    action process_cmu1_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group9.cmu1.key = meta.cmu_group9.cmu1.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group9.cmu1.param.p1 = code;
    }
    action process_cmu1_key(bit<16> offset){
        meta.cmu_group9.cmu1.key = meta.cmu_group9.cmu1.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu1_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group9.cmu1.param.p1;
          // meta.cmu_group9.cmu1.param.p1 = meta.cmu_group9.cmu1.param.p2;
          // meta.cmu_group9.cmu1.param.p2 = temp;
    //}
    @pragma stage 10
    table tbl_cmu1_preprocessing {
        key = {
            meta.cmu_group9.cmu1.task_id : exact;
            meta.cmu_group9.cmu1.key     : ternary;
            meta.cmu_group9.cmu1.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu1_key;
            process_cmu1_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU0.
    Register<bit<16>, bit<16>>(32, 0) cmu1_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group9.cmu1.param.p2){
                value = value |+| meta.cmu_group9.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group9.cmu1.param.p1){
                value = meta.cmu_group9.cmu1.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group9.cmu1.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group9.cmu1.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group9.cmu1.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu1_buckets) cmu1_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu1_cond_add(){
        meta.cmu_group9.cmu1.param.p2 = cmu1_op_cond_add.execute((bit<16>)meta.cmu_group9.cmu1.key[4:0]);
    }
    action op_cmu1_and_or(){
        meta.cmu_group9.cmu1.param.p2 = cmu1_op_and_or.execute((bit<16>)meta.cmu_group9.cmu1.key[4:0]);
    }
    action op_cmu1_max(){
        meta.cmu_group9.cmu1.param.p2 = cmu1_op_max.execute((bit<16>)meta.cmu_group9.cmu1.key[4:0]);
    }

    //action op_cmu1_reserved(){
    //    meta.cmu_group9.cmu1.param.p2 = cmu1_op_reserved.execute((bit<16>)meta.cmu_group9.cmu1.key[4:0]);
    //}

    @pragma stage 11
    table tbl_cmu1_operation {
        key = {
            meta.cmu_group9.cmu1.task_id : exact;
        }
        actions = {
            op_cmu1_cond_add;
            op_cmu1_and_or;
            op_cmu1_max;
            // op_cmu1_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU1.
    action set_cmu2_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group9.cmu2.task_id = task_id;
            meta.cmu_group9.cmu2.key[15:0] = meta.cmu_group9.compressed_key1[23:8];
            meta.cmu_group9.cmu2.param.p1 = meta.cmu_group9.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group9.cmu2.param.p2 = meta.cmu_group9.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu2_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group9.cmu2.task_id = task_id;
            meta.cmu_group9.cmu2.key[15:0] = meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu2.param.p1 = meta.cmu_group9.cmu2.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group9.cmu2.param.p2 = meta.cmu_group9.cmu2.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu2_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group9.cmu2.task_id = task_id;
            meta.cmu_group9.cmu2.key[15:0] = meta.cmu_group9.compressed_key1[23:8];
            meta.cmu_group9.cmu2.param.p1 =  meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu2.param.p2 = meta.cmu_group9.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu2_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group9.cmu2.task_id = task_id;
            meta.cmu_group9.cmu2.key[15:0] = meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu2.param.p1 =  meta.cmu_group9.compressed_key1[15:0];
            meta.cmu_group9.cmu2.param.p2 = meta.cmu_group9.cmu2.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 9
    table tbl_cmu2_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu2_hkey1_cparam;
            set_cmu2_hkey2_cparam;

            set_cmu2_hkey1_hparam2;

            set_cmu2_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU1.
    action process_cmu2_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group9.cmu2.key = meta.cmu_group9.cmu2.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group9.cmu2.param.p1 = code;
    }
    action process_cmu2_key(bit<16> offset){
        meta.cmu_group9.cmu2.key = meta.cmu_group9.cmu2.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu2_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group9.cmu2.param.p1;
          // meta.cmu_group9.cmu2.param.p1 = meta.cmu_group9.cmu2.param.p2;
          // meta.cmu_group9.cmu2.param.p2 = temp;
    //}
    @pragma stage 10
    table tbl_cmu2_preprocessing {
        key = {
            meta.cmu_group9.cmu2.task_id : exact;
            meta.cmu_group9.cmu2.key     : ternary;
            meta.cmu_group9.cmu2.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu2_key;
            process_cmu2_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU1.
    Register<bit<16>, bit<16>>(32, 0) cmu2_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group9.cmu2.param.p2){
                value = value |+| meta.cmu_group9.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group9.cmu2.param.p1){
                value = meta.cmu_group9.cmu2.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group9.cmu2.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group9.cmu2.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group9.cmu2.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu2_buckets) cmu2_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu2_cond_add(){
        meta.cmu_group9.cmu2.param.p2 = cmu2_op_cond_add.execute((bit<16>)meta.cmu_group9.cmu2.key[4:0]);
    }
    action op_cmu2_and_or(){
        meta.cmu_group9.cmu2.param.p2 = cmu2_op_and_or.execute((bit<16>)meta.cmu_group9.cmu2.key[4:0]);
    }
    action op_cmu2_max(){
        meta.cmu_group9.cmu2.param.p2 = cmu2_op_max.execute((bit<16>)meta.cmu_group9.cmu2.key[4:0]);
    }

    //action op_cmu2_reserved(){
    //    meta.cmu_group9.cmu2.param.p2 = cmu2_op_reserved.execute((bit<16>)meta.cmu_group9.cmu2.key[4:0]);
    //}

    @pragma stage 11
    table tbl_cmu2_operation {
        key = {
            meta.cmu_group9.cmu2.task_id : exact;
        }
        actions = {
            op_cmu2_cond_add;
            op_cmu2_and_or;
            op_cmu2_max;
            // op_cmu2_reserved;
        }
        size = 32;
    }
    // Initialization stage of CMU2.
    action set_cmu3_hkey1_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group9.cmu3.task_id = task_id;
            meta.cmu_group9.cmu3.key[15:0] = meta.cmu_group9.compressed_key1[31:16];
            meta.cmu_group9.cmu3.param.p1 = meta.cmu_group9.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group9.cmu3.param.p2 = meta.cmu_group9.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.                                                                    
    }
    action set_cmu3_hkey2_cparam(bit<8> task_id, bit<16> param1, bit<16> param2) {
            meta.cmu_group9.cmu3.task_id = task_id;
            meta.cmu_group9.cmu3.key[15:0] = meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu3.param.p1 = meta.cmu_group9.cmu3.param.p1 + param1;  // NOTE: ADD is more flexible than SET.
            meta.cmu_group9.cmu3.param.p2 = meta.cmu_group9.cmu3.param.p2 + param2;  //       If we don't want to change params, we can add 0 to the params.     
    }



    action set_cmu3_hkey1_hparam2(bit<8> task_id, bit<16> param2) {
            meta.cmu_group9.cmu3.task_id = task_id;
            meta.cmu_group9.cmu3.key[15:0] = meta.cmu_group9.compressed_key1[31:16];
            meta.cmu_group9.cmu3.param.p1 =  meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu3.param.p2 = meta.cmu_group9.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    action set_cmu3_hkey2_hparam1(bit<8> task_id, bit<16> param2) {
            meta.cmu_group9.cmu3.task_id = task_id;
            meta.cmu_group9.cmu3.key[15:0] = meta.cmu_group9.compressed_key2[15:0];
            meta.cmu_group9.cmu3.param.p1 =  meta.cmu_group9.compressed_key1[15:0];
            meta.cmu_group9.cmu3.param.p2 = meta.cmu_group9.cmu3.param.p2 + param2;    // ADD is more flexible than SET.
    }


    // There are some special (i.e., from standard metadata) params here.
    // We support them fragmentary among CMU-Groups to save PHV resources.
    
    @pragma stage 9
    table tbl_cmu3_initialization {
        key = {
            // Here we use IP Pair as the filter.
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
            // Other fields can be added here.
            // We only use the filter in the initialization stage, and select a task id.
            // We use task_id to identify tasks to save TCAM resources in the initialization stage.
        }
        actions = {
            set_cmu3_hkey1_cparam;
            set_cmu3_hkey2_cparam;

            set_cmu3_hkey1_hparam2;

            set_cmu3_hkey2_hparam1;



        }
        size = 32;
    }

    // Pre-processing stage of CMU2.
    action process_cmu3_key_param(bit<16> offset, bit<16> code){
        meta.cmu_group9.cmu3.key = meta.cmu_group9.cmu3.key + offset; // Implementing '-' by '+' overflow.
        meta.cmu_group9.cmu3.param.p1 = code;
    }
    action process_cmu3_key(bit<16> offset){
        meta.cmu_group9.cmu3.key = meta.cmu_group9.cmu3.key + offset; // Implementing '-' by '+' overflow.
    }
    //action process_cmu3_param(){
          // swap param1 and param2.
          // bit<16> temp = meta.cmu_group9.cmu3.param.p1;
          // meta.cmu_group9.cmu3.param.p1 = meta.cmu_group9.cmu3.param.p2;
          // meta.cmu_group9.cmu3.param.p2 = temp;
    //}
    @pragma stage 10
    table tbl_cmu3_preprocessing {
        key = {
            meta.cmu_group9.cmu3.task_id : exact;
            meta.cmu_group9.cmu3.key     : ternary;
            meta.cmu_group9.cmu3.param.p1  : ternary;
        }
        actions = {
            no_action;
            process_cmu3_key;
            process_cmu3_key_param;
        }
        const default_action = no_action();
        size = 1024;
    }

    // Operation stage of CMU2.
    Register<bit<16>, bit<16>>(32, 0) cmu3_buckets; 
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_cond_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group9.cmu3.param.p2){
                value = value |+| meta.cmu_group9.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < meta.cmu_group9.cmu3.param.p1){
                value = meta.cmu_group9.cmu3.param.p1;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_and_or = {
        void apply(inout bit<16> value, out bit<16> result) {
            if(meta.cmu_group9.cmu3.param.p2 == 1) // bitwise_and
            {
                value = meta.cmu_group9.cmu3.param.p1 & value;
            }
            else{           // bitwise_or
                value = meta.cmu_group9.cmu3.param.p1 | value;
            }
            result = value;
        }
    };

    //RegisterAction<bit<16>, bit<16>, bit<16>>(cmu3_buckets) cmu3_op_reserved = {
    //    void apply(inout bit<16> value, out bit<16> result) {
    //        // Reserved stateful operation.
    //       result = value;
    //    }
    //};

    action op_cmu3_cond_add(){
        meta.cmu_group9.cmu3.param.p2 = cmu3_op_cond_add.execute((bit<16>)meta.cmu_group9.cmu3.key[4:0]);
    }
    action op_cmu3_and_or(){
        meta.cmu_group9.cmu3.param.p2 = cmu3_op_and_or.execute((bit<16>)meta.cmu_group9.cmu3.key[4:0]);
    }
    action op_cmu3_max(){
        meta.cmu_group9.cmu3.param.p2 = cmu3_op_max.execute((bit<16>)meta.cmu_group9.cmu3.key[4:0]);
    }

    //action op_cmu3_reserved(){
    //    meta.cmu_group9.cmu3.param.p2 = cmu3_op_reserved.execute((bit<16>)meta.cmu_group9.cmu3.key[4:0]);
    //}

    @pragma stage 11
    table tbl_cmu3_operation {
        key = {
            meta.cmu_group9.cmu3.task_id : exact;
        }
        actions = {
            op_cmu3_cond_add;
            op_cmu3_and_or;
            op_cmu3_max;
            // op_cmu3_reserved;
        }
        size = 32;
    }

    apply {
        // Shared Compression Stage for CMUG9.
        tbl_hash1.apply(); 
        tbl_hash2.apply(); 

        // Initialization, Pre-processing, operation stages for CMU1 in CMUG9.
        tbl_cmu1_initialization.apply();
        tbl_cmu1_preprocessing.apply();
        tbl_cmu1_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU2 in CMUG9.
        tbl_cmu2_initialization.apply();
        tbl_cmu2_preprocessing.apply();
        tbl_cmu2_operation.apply();
        // Initialization, Pre-processing, operation stages for CMU3 in CMUG9.
        tbl_cmu3_initialization.apply();
        tbl_cmu3_preprocessing.apply();
        tbl_cmu3_operation.apply();
    }
}
#endif