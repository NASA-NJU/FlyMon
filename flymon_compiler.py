#!/usr/bin/env python
import jinja2
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--num_group", dest="group_num", type=int, required=True, help="How many cmu-groups in data plane?")
args = parser.parse_args()

# ===================================================
# P4 Path infomation.
# ===================================================
TEMPLATE_PATH = 'p4_templates/'
BUILD_PATH = 'p4src/'
CONTROL_PATHG = 'control_plane'

# ===================================================
# CMU Memory Config List.
# ===================================================
MEM_CONFIGS = {
    "memory_level_mini" : {"size" : 32,  "bit_width" :    5},   
    "memory_level_1" : {"size" : 512,     "bit_width" :   9},    
    "memory_level_2" : {"size" : 1024,    "bit_width" :  10},     
    "memory_level_3" : {"size" : 2048,    "bit_width" :  11},     
    "memory_level_4" : {"size" : 4096,    "bit_width" :  12},     
    "memory_level_5" : {"size" : 8192,    "bit_width" :  13},    
    "memory_level_6" : {"size" : 16384,   "bit_width" :  14},     
    "memory_level_7" : {"size" : 32768,   "bit_width" :  15},     
    "memory_level_8" : {"size" : 65536,   "bit_width" :  16},     
}

# ===================================================
# CMU_GROUPS configs.
# ===================================================
TOTAL_CMU_GROUP_NUM     = args.group_num
INGRESS_CMU_GROUP_NUM   = int(TOTAL_CMU_GROUP_NUM/2)
EGRESS_CMU_GROUP_NUM    = TOTAL_CMU_GROUP_NUM - INGRESS_CMU_GROUP_NUM

CMU_PER_GROUP   = 3
MEMORY_PER_CMU  = MEM_CONFIGS["memory_level_mini"]

CANDIDATE_KEY_LIST = {
    "hdr.ipv4.src_addr" : 32,
    "hdr.ipv4.dst_addr" : 32,
    "hdr.ports.src_port": 16,
    "hdr.ports.dst_port": 16,
    "hdr.ipv4.protocol" :  8
}
CANDIDATE_KEY_SET = ",".join(CANDIDATE_KEY_LIST.keys())

INGRESS_STDMETA_PARAM_SET = { 
    "timestamp" :  "intr_md.ingress_mac_tstamp[15:0]"
}

EGRESS_STDMETA_PARAM_SET  = { 
    "pkt_size" : "(bit<16>) intr_md.pkt_length",
    "queue_size" : "intr_md.enq_qdepth[15:0]",
    "timestamp" : "intr_md.enq_tstamp[15:0];"
}
                             
CMUG_GROUP_CONFIGS = []
CMUG_GROUP_CONFIGS += ([
    {
        "id" : id + 1,
        "type" : 1,
        "mau_start" : id,
        "cmu_num" : CMU_PER_GROUP,
        "cmu_size" : MEMORY_PER_CMU["size"],
        "key_bitw" : MEMORY_PER_CMU["bit_width"],
        "candidate_key_list" : CANDIDATE_KEY_LIST
    }
    for id in range(INGRESS_CMU_GROUP_NUM) 
])
CMUG_GROUP_CONFIGS += ([
    {
        "id" : id + INGRESS_CMU_GROUP_NUM + 1,
        "type" : 2,
        "mau_start" : id + INGRESS_CMU_GROUP_NUM,
        "cmu_num" : CMU_PER_GROUP,
        "cmu_size" : MEMORY_PER_CMU["size"],
        "key_bitw" : MEMORY_PER_CMU["bit_width"],
        "candidate_key_list" : CANDIDATE_KEY_LIST
    }
    for id in range(EGRESS_CMU_GROUP_NUM) 
])

for CMUG in CMUG_GROUP_CONFIGS:
    if CMUG["type"] == 1  and CMUG["id"] == 1:
        CMUG["std_params"] = INGRESS_STDMETA_PARAM_SET
    elif CMUG["type"] == 2 and CMUG["id"] == int(len(CMUG_GROUP_CONFIGS)/2) + 1:
        CMUG["std_params"] = EGRESS_STDMETA_PARAM_SET
    else:
        CMUG["std_params"] = {}

# ===================================================

if __name__ == "__main__":
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_PATH),  trim_blocks=True, lstrip_blocks=True)  
    # Generating headers.p4
    meta_template = env.get_template('headers.p4_template')
    meta_template_out = meta_template.render(CMUG_GROUP_CONFIGS = CMUG_GROUP_CONFIGS)
    with open(BUILD_PATH + 'headers.p4', 'w') as f:
        f.writelines(meta_template_out)
        f.close()

    # Generating cmu_groups.p4
    cmu_group_template = env.get_template('cmu_groups.p4_template')
    cmu_group_template_out = cmu_group_template.render(CMUG_GROUP_CONFIGS = CMUG_GROUP_CONFIGS)
    with open(BUILD_PATH + 'cmu_groups.p4', 'w') as f:
        f.writelines(cmu_group_template_out)
        f.close()
    
    # Generating flymon.p4
    flymon_template = env.get_template('flymon.p4_template')
    flymon_template_out = flymon_template.render(CMUG_GROUP_CONFIGS = CMUG_GROUP_CONFIGS)
    with open(BUILD_PATH + 'flymon.p4', 'w') as f:
        f.writelines(flymon_template_out)
        f.close()

    with open(CONTROL_PATHG+'/cmu_groups.json', 'w') as config:
        config.write(json.dumps(CMUG_GROUP_CONFIGS))