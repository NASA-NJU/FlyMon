// This file defines some shared variables for all passive 
// measurement data structure.
#ifndef _MDATA_P4_
#define _MDATA_P4_


// elements_t is extract by looking up before extract;
// this can avoid phv-grouping with std packet header fields.
struct elements_t {
    bit<16> src_port;
    bit<16> dst_port;
}



struct cu0_metadata_t {
    
    bit<32>    hash_val0;
    
    bit<32>    hash_val1;
    
    bit<32>    hash_val2;
    
}




struct eu0_metadata_t {
    bit<8>     task_id;
    bit<32>    key;
    bit<16>    val;
	// bit<16>    result; // Output, use the `val` to act the function of the `result`, 
                          // since the `result` is always used after the `value` is invalid.
}


struct eu1_metadata_t {
    bit<8>     task_id;
    bit<32>    key;
    bit<16>    val;
	// bit<16>    result; // Output, use the `val` to act the function of the `result`, 
                          // since the `result` is always used after the `value` is invalid.
}


struct eu2_metadata_t {
    bit<8>     task_id;
    bit<32>    key;
    bit<16>    val;
	// bit<16>    result; // Output, use the `val` to act the function of the `result`, 
                          // since the `result` is always used after the `value` is invalid.
}


struct eu3_metadata_t {
    bit<8>     task_id;
    bit<32>    key;
    bit<16>    val;
	// bit<16>    result; // Output, use the `val` to act the function of the `result`, 
                          // since the `result` is always used after the `value` is invalid.
}




struct ru0_metadata_t {
    bit<1> flag;
}


struct dupkey_filter_metadata_t {
    bit<1> bit0;
    bit<1> bit1;
    bit<1> bit2;
    bit<1> bit3;
}

struct heavy_key_digest_t {
    bit<32> a;
    bit<32> b;
    bit<16> c;
    bit<16> d;
    bit<8>  e;
}


struct ingress_metadata_t {
    // elements_t is extract by looking up before extract;
    // this can avoid phv-grouping with std packet header fields.
    elements_t   elements;

    
        cu0_metadata_t cu_0;
    

    
        eu0_metadata_t eu_0;
    
        eu1_metadata_t eu_1;
    
        eu2_metadata_t eu_2;
    
        eu3_metadata_t eu_3;
    

    
        ru0_metadata_t ru_0;
    

    dupkey_filter_metadata_t dup_filter_meta;
}

struct egress_metadata_t {

}

#endif