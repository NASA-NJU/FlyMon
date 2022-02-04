#ifndef _HEAVY_KEY_REPORTER_P4_
#define _HEAVY_KEY_REPORTER_P4_

#include "mdata.p4"


control ReportingUnit_0 ( in header_t hdr,
                in ingress_intrinsic_metadata_t ig_intr_md,
                inout ingress_metadata_t ig_md) 
{
    
    DirectCounter<bit<32>>(CounterType_t.PACKETS) direct_counter;
    action hit(){
        ig_md.ru_0.flag = 1;
        direct_counter.count();
    }    
    
    table tbl_result_judge {
        key = {
            
            ig_md.eu_0.task_id : exact;
            ig_md.eu_0.val :  ternary;
            
            ig_md.eu_1.task_id : exact;
            ig_md.eu_1.val :  ternary;
            
            ig_md.eu_2.task_id : exact;
            ig_md.eu_2.val :  ternary;
            
            ig_md.eu_3.task_id : exact;
            ig_md.eu_3.val :  ternary;
            
        }
        actions = {
            hit;
        }
        size = 64;
        counters = direct_counter;
    }
    
    apply {
        tbl_result_judge.apply();
    }
}


#endif