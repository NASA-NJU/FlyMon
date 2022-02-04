#ifndef _EXECUTION_UNITS_P4_
#define _EXECUTION_UNITS_P4_

#include "mdata.p4"


control ExecutionUnit_0 (in header_t hdr,
                                 in ingress_intrinsic_metadata_t ig_intr_md,
                                 inout ingress_metadata_t ig_md) 
{ 
    action no_action(){}
    // ------------------------------
    // Initialization Stage
    // ------------------------------
    
    
    action set_key_hash0() {
        ig_md.eu_0.key[15:0] = ig_md.cu_0.hash_val0[15:0];
    }
    
    action set_key_hash1() {
        ig_md.eu_0.key[15:0] = ig_md.cu_0.hash_val1[15:0];
    }
    
    action set_key_hash2() {
        ig_md.eu_0.key[15:0] = ig_md.cu_0.hash_val2[15:0];
    }
    

    
    table tbl_set_key {
        key = {
            ig_md.eu_0.task_id : exact;
        }
        actions = {
            
            set_key_hash0;
            
            set_key_hash1;
            
            set_key_hash2;
            
        }
        size = 32;
    }

    action set_val_const(bit<16> const_val) {
        ig_md.eu_0.val = const_val; 
    }
    
    action set_val_hash0() {
        ig_md.eu_0.val =  ig_md.cu_0.hash_val0[15:0];
    }
    
    action set_val_hash1() {
        ig_md.eu_0.val =  ig_md.cu_0.hash_val1[15:0];
    }
    
    action set_val_hash2() {
        ig_md.eu_0.val =  ig_md.cu_0.hash_val2[15:0];
    }
    

    
    table tbl_set_val {
        key = {
            ig_md.eu_0.task_id : exact;
        }
        actions = {
            set_val_const;
            
            set_val_hash0;
            
            set_val_hash1;
            
            set_val_hash2;
            
        }
        size = 32;
    }

    //mmh-trick: add overflow
    action key_add_offset(bit<32> offset){
       ig_md.eu_0.key = ig_md.eu_0.key + offset;
    }
    // address isolution
    
    table tbl_process_key {
        key = {
            ig_md.eu_0.task_id : exact;
            ig_md.eu_0.key     : ternary;
        }
        actions = {
            key_add_offset;
            no_action;
        }
        const default_action = no_action();
        size = 64;
    }
    
    action val_one_hot(bit<16> code){
        ig_md.eu_0.val = code;
    }
    action val_sub_result(){
        // TODO: need to connect to another EU.
        // This will be implemented in the future.
        // ig_md.eu_0.val = ig_md.eu_0.val - ig_md.eu_0.result;
    }
    
    table tbl_process_val {
        key = {
            ig_md.eu_0.task_id : exact;
            ig_md.eu_0.val     : ternary;
        }
        actions = {
            no_action;
            val_one_hot;
            val_sub_result;
        }
        const default_action = no_action();
        size = 64;
    }

    // ------------------------------
    // Operation Stage
    // ------------------------------
    Register<bit<16>, bit<32>>(65536, 0) pages; 

    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            value = value |+| ig_md.eu_0.val;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < ig_md.eu_0.val){
                value = ig_md.eu_0.val;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_and = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_0.val & value;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_set = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_0.val;
            result = value;
        }
    };

    action op_add(){
        ig_md.eu_0.val = reg_op_add.execute(ig_md.eu_0.key);
    }
    action op_max(){
        ig_md.eu_0.val = reg_op_max.execute(ig_md.eu_0.key);
    }
    action op_and(){
        ig_md.eu_0.val = reg_op_and.execute(ig_md.eu_0.key);
    }
    action op_set(){
        ig_md.eu_0.val = reg_op_set.execute(ig_md.eu_0.key);
    }
    
    table tbl_select_op {
        key = {
            ig_md.eu_0.task_id : exact;
        }
        actions = {
            op_set;
            op_add;
            op_max;
            op_and;
        }
        size = 32;
    }
    apply {
        tbl_set_key.apply();
        tbl_set_val.apply();

        tbl_process_key.apply();
        tbl_process_val.apply();

        tbl_select_op.apply();
    }
}

control ExecutionUnit_1 (in header_t hdr,
                                 in ingress_intrinsic_metadata_t ig_intr_md,
                                 inout ingress_metadata_t ig_md) 
{ 
    action no_action(){}
    // ------------------------------
    // Initialization Stage
    // ------------------------------
    
    
    action set_key_hash0() {
        ig_md.eu_1.key[15:0] = ig_md.cu_0.hash_val0[19:4];
    }
    
    action set_key_hash1() {
        ig_md.eu_1.key[15:0] = ig_md.cu_0.hash_val1[19:4];
    }
    
    action set_key_hash2() {
        ig_md.eu_1.key[15:0] = ig_md.cu_0.hash_val2[16:1];
    }
    

    
    table tbl_set_key {
        key = {
            ig_md.eu_1.task_id : exact;
        }
        actions = {
            
            set_key_hash0;
            
            set_key_hash1;
            
            set_key_hash2;
            
        }
        size = 32;
    }

    action set_val_const(bit<16> const_val) {
        ig_md.eu_1.val = const_val; 
    }
    
    action set_val_hash0() {
        ig_md.eu_1.val =  ig_md.cu_0.hash_val0[15:0];
    }
    
    action set_val_hash1() {
        ig_md.eu_1.val =  ig_md.cu_0.hash_val1[15:0];
    }
    
    action set_val_hash2() {
        ig_md.eu_1.val =  ig_md.cu_0.hash_val2[15:0];
    }
    

    
    table tbl_set_val {
        key = {
            ig_md.eu_1.task_id : exact;
        }
        actions = {
            set_val_const;
            
            set_val_hash0;
            
            set_val_hash1;
            
            set_val_hash2;
            
        }
        size = 32;
    }

    //mmh-trick: add overflow
    action key_add_offset(bit<32> offset){
       ig_md.eu_1.key = ig_md.eu_1.key + offset;
    }
    // address isolution
    
    table tbl_process_key {
        key = {
            ig_md.eu_1.task_id : exact;
            ig_md.eu_1.key     : ternary;
        }
        actions = {
            key_add_offset;
            no_action;
        }
        const default_action = no_action();
        size = 64;
    }
    
    action val_one_hot(bit<16> code){
        ig_md.eu_1.val = code;
    }
    action val_sub_result(){
        // TODO: need to connect to another EU.
        // This will be implemented in the future.
        // ig_md.eu_1.val = ig_md.eu_1.val - ig_md.eu_1.result;
    }
    
    table tbl_process_val {
        key = {
            ig_md.eu_1.task_id : exact;
            ig_md.eu_1.val     : ternary;
        }
        actions = {
            no_action;
            val_one_hot;
            val_sub_result;
        }
        const default_action = no_action();
        size = 64;
    }

    // ------------------------------
    // Operation Stage
    // ------------------------------
    Register<bit<16>, bit<32>>(65536, 0) pages; 

    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            value = value |+| ig_md.eu_1.val;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < ig_md.eu_1.val){
                value = ig_md.eu_1.val;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_and = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_1.val & value;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_set = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_1.val;
            result = value;
        }
    };

    action op_add(){
        ig_md.eu_1.val = reg_op_add.execute(ig_md.eu_1.key);
    }
    action op_max(){
        ig_md.eu_1.val = reg_op_max.execute(ig_md.eu_1.key);
    }
    action op_and(){
        ig_md.eu_1.val = reg_op_and.execute(ig_md.eu_1.key);
    }
    action op_set(){
        ig_md.eu_1.val = reg_op_set.execute(ig_md.eu_1.key);
    }
    
    table tbl_select_op {
        key = {
            ig_md.eu_1.task_id : exact;
        }
        actions = {
            op_set;
            op_add;
            op_max;
            op_and;
        }
        size = 32;
    }
    apply {
        tbl_set_key.apply();
        tbl_set_val.apply();

        tbl_process_key.apply();
        tbl_process_val.apply();

        tbl_select_op.apply();
    }
}

control ExecutionUnit_2 (in header_t hdr,
                                 in ingress_intrinsic_metadata_t ig_intr_md,
                                 inout ingress_metadata_t ig_md) 
{ 
    action no_action(){}
    // ------------------------------
    // Initialization Stage
    // ------------------------------
    
    
    action set_key_hash0() {
        ig_md.eu_2.key[15:0] = ig_md.cu_0.hash_val0[23:8];
    }
    
    action set_key_hash1() {
        ig_md.eu_2.key[15:0] = ig_md.cu_0.hash_val1[23:8];
    }
    
    action set_key_hash2() {
        ig_md.eu_2.key[15:0] = ig_md.cu_0.hash_val2[17:2];
    }
    

    
    table tbl_set_key {
        key = {
            ig_md.eu_2.task_id : exact;
        }
        actions = {
            
            set_key_hash0;
            
            set_key_hash1;
            
            set_key_hash2;
            
        }
        size = 32;
    }

    action set_val_const(bit<16> const_val) {
        ig_md.eu_2.val = const_val; 
    }
    
    action set_val_hash0() {
        ig_md.eu_2.val =  ig_md.cu_0.hash_val0[15:0];
    }
    
    action set_val_hash1() {
        ig_md.eu_2.val =  ig_md.cu_0.hash_val1[15:0];
    }
    
    action set_val_hash2() {
        ig_md.eu_2.val =  ig_md.cu_0.hash_val2[15:0];
    }
    

    
    table tbl_set_val {
        key = {
            ig_md.eu_2.task_id : exact;
        }
        actions = {
            set_val_const;
            
            set_val_hash0;
            
            set_val_hash1;
            
            set_val_hash2;
            
        }
        size = 32;
    }

    //mmh-trick: add overflow
    action key_add_offset(bit<32> offset){
       ig_md.eu_2.key = ig_md.eu_2.key + offset;
    }
    // address isolution
    
    table tbl_process_key {
        key = {
            ig_md.eu_2.task_id : exact;
            ig_md.eu_2.key     : ternary;
        }
        actions = {
            key_add_offset;
            no_action;
        }
        const default_action = no_action();
        size = 64;
    }
    
    action val_one_hot(bit<16> code){
        ig_md.eu_2.val = code;
    }
    action val_sub_result(){
        // TODO: need to connect to another EU.
        // This will be implemented in the future.
        // ig_md.eu_2.val = ig_md.eu_2.val - ig_md.eu_2.result;
    }
    
    table tbl_process_val {
        key = {
            ig_md.eu_2.task_id : exact;
            ig_md.eu_2.val     : ternary;
        }
        actions = {
            no_action;
            val_one_hot;
            val_sub_result;
        }
        const default_action = no_action();
        size = 64;
    }

    // ------------------------------
    // Operation Stage
    // ------------------------------
    Register<bit<16>, bit<32>>(65536, 0) pages; 

    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            value = value |+| ig_md.eu_2.val;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < ig_md.eu_2.val){
                value = ig_md.eu_2.val;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_and = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_2.val & value;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_set = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_2.val;
            result = value;
        }
    };

    action op_add(){
        ig_md.eu_2.val = reg_op_add.execute(ig_md.eu_2.key);
    }
    action op_max(){
        ig_md.eu_2.val = reg_op_max.execute(ig_md.eu_2.key);
    }
    action op_and(){
        ig_md.eu_2.val = reg_op_and.execute(ig_md.eu_2.key);
    }
    action op_set(){
        ig_md.eu_2.val = reg_op_set.execute(ig_md.eu_2.key);
    }
    
    table tbl_select_op {
        key = {
            ig_md.eu_2.task_id : exact;
        }
        actions = {
            op_set;
            op_add;
            op_max;
            op_and;
        }
        size = 32;
    }
    apply {
        tbl_set_key.apply();
        tbl_set_val.apply();

        tbl_process_key.apply();
        tbl_process_val.apply();

        tbl_select_op.apply();
    }
}

control ExecutionUnit_3 (in header_t hdr,
                                 in ingress_intrinsic_metadata_t ig_intr_md,
                                 inout ingress_metadata_t ig_md) 
{ 
    action no_action(){}
    // ------------------------------
    // Initialization Stage
    // ------------------------------
    
    
    action set_key_hash0() {
        ig_md.eu_3.key[15:0] = ig_md.cu_0.hash_val0[31:16];
    }
    
    action set_key_hash1() {
        ig_md.eu_3.key[15:0] = ig_md.cu_0.hash_val1[31:16];
    }
    
    action set_key_hash2() {
        ig_md.eu_3.key[15:0] = ig_md.cu_0.hash_val2[18:3];
    }
    

    
    table tbl_set_key {
        key = {
            ig_md.eu_3.task_id : exact;
        }
        actions = {
            
            set_key_hash0;
            
            set_key_hash1;
            
            set_key_hash2;
            
        }
        size = 32;
    }

    action set_val_const(bit<16> const_val) {
        ig_md.eu_3.val = const_val; 
    }
    
    action set_val_hash0() {
        ig_md.eu_3.val =  ig_md.cu_0.hash_val0[15:0];
    }
    
    action set_val_hash1() {
        ig_md.eu_3.val =  ig_md.cu_0.hash_val1[15:0];
    }
    
    action set_val_hash2() {
        ig_md.eu_3.val =  ig_md.cu_0.hash_val2[15:0];
    }
    

    
    table tbl_set_val {
        key = {
            ig_md.eu_3.task_id : exact;
        }
        actions = {
            set_val_const;
            
            set_val_hash0;
            
            set_val_hash1;
            
            set_val_hash2;
            
        }
        size = 32;
    }

    //mmh-trick: add overflow
    action key_add_offset(bit<32> offset){
       ig_md.eu_3.key = ig_md.eu_3.key + offset;
    }
    // address isolution
    
    table tbl_process_key {
        key = {
            ig_md.eu_3.task_id : exact;
            ig_md.eu_3.key     : ternary;
        }
        actions = {
            key_add_offset;
            no_action;
        }
        const default_action = no_action();
        size = 64;
    }
    
    action val_one_hot(bit<16> code){
        ig_md.eu_3.val = code;
    }
    action val_sub_result(){
        // TODO: need to connect to another EU.
        // This will be implemented in the future.
        // ig_md.eu_3.val = ig_md.eu_3.val - ig_md.eu_3.result;
    }
    
    table tbl_process_val {
        key = {
            ig_md.eu_3.task_id : exact;
            ig_md.eu_3.val     : ternary;
        }
        actions = {
            no_action;
            val_one_hot;
            val_sub_result;
        }
        const default_action = no_action();
        size = 64;
    }

    // ------------------------------
    // Operation Stage
    // ------------------------------
    Register<bit<16>, bit<32>>(65536, 0) pages; 

    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_add = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            value = value |+| ig_md.eu_3.val;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_max = {
        void apply(inout bit<16> value, out bit<16> result) {
            result = 0;
            if(value < ig_md.eu_3.val){
                value = ig_md.eu_3.val;
                result = value;
            }
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_and = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_3.val & value;
            result = value;
        }
    };
    RegisterAction<bit<16>, bit<32>, bit<16>>(pages) reg_op_set = {
        void apply(inout bit<16> value, out bit<16> result) {
            value = ig_md.eu_3.val;
            result = value;
        }
    };

    action op_add(){
        ig_md.eu_3.val = reg_op_add.execute(ig_md.eu_3.key);
    }
    action op_max(){
        ig_md.eu_3.val = reg_op_max.execute(ig_md.eu_3.key);
    }
    action op_and(){
        ig_md.eu_3.val = reg_op_and.execute(ig_md.eu_3.key);
    }
    action op_set(){
        ig_md.eu_3.val = reg_op_set.execute(ig_md.eu_3.key);
    }
    
    table tbl_select_op {
        key = {
            ig_md.eu_3.task_id : exact;
        }
        actions = {
            op_set;
            op_add;
            op_max;
            op_and;
        }
        size = 32;
    }
    apply {
        tbl_set_key.apply();
        tbl_set_val.apply();

        tbl_process_key.apply();
        tbl_process_val.apply();

        tbl_select_op.apply();
    }
}

#endif