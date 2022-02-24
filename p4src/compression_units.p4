#ifndef _COMPRESSION_UNITS_P4_
#define _COMPRESSION_UNITS_P4_

#include "headers.p4"
#include "util.p4"
#include "mdata.p4"


control CompressionUnit_0 ( in header_t hdr,
                          in ingress_intrinsic_metadata_t ig_intr_md,
                          inout ingress_metadata_t ig_md) 
{
    
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit0;
    action hash0(){
        ig_md.cu_0.hash_val0 = hash_unit0.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol });
    }
    
    table tbl_hash_0{
        actions = {
            hash0;
        }
        const default_action = hash0(); 
        size = 1;
    }
    
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit1;
    action hash1(){
        ig_md.cu_0.hash_val1 = hash_unit1.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol });
    }
    
    table tbl_hash_1{
        actions = {
            hash1;
        }
        const default_action = hash1(); 
        size = 1;
    }
    
    Hash<bit<32>>(HashAlgorithm_t.CRC32) hash_unit2;
    action hash2(){
        ig_md.cu_0.hash_val2 = hash_unit2.get({ hdr.ethernet.src_addr,hdr.ethernet.src_addr,hdr.tcp.window,hdr.ipv4.src_addr,hdr.ipv4.dst_addr,ig_md.elements.src_port,ig_md.elements.dst_port,hdr.ipv4.protocol });
    }
    
    table tbl_hash_2{
        actions = {
            hash2;
        }
        const default_action = hash2(); 
        size = 1;
    }
    
    apply {
        
        tbl_hash_0.apply();
        
        tbl_hash_1.apply();
        
        tbl_hash_2.apply();
        
    }
}


#endif