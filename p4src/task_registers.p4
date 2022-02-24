#ifndef _TASK_REGISTER_P4_
#define _TASK_REGISTER_P4_

#include "headers.p4"
#include "util.p4"
#include "mdata.p4"




control TaskRegister_0 ( in header_t hdr,
                                  in ingress_intrinsic_metadata_t ig_intr_md,
                                  inout ingress_metadata_t ig_md ) 
{
    action set_task_id(
        
        bit<8> id0,
        
        bit<8> id1,
        
        bit<8> id2,
        
        bit<8> id3,
        
        bit<1> end
        )
    {
        
        ig_md.eu_0.task_id = id0;
        
        ig_md.eu_1.task_id = id1;
        
        ig_md.eu_2.task_id = id2;
        
        ig_md.eu_3.task_id = id3;
        
    }

    
    table tbl_set_task_id {
        key = {
            //hdr.ipv4.src_addr : ternary @name("src_addr");
            //hdr.ipv4.dst_addr : ternary @name("dst_addr");
            hdr.ipv4.src_addr : ternary;
            hdr.ipv4.dst_addr : ternary;
        }
        actions = {
            set_task_id;
        }
        size = 32;
    }
    apply {
        tbl_set_task_id.apply();
    }
}


#endif