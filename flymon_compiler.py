#!/usr/bin/env python
import jinja2
import json
import argparse

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


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--num_group", dest="group_num", type=int, required=True, help="How many cmu-groups in data plane?")
parser.add_argument("-m", "--memory", dest="memory", type=str, required=True, help="What is the size of a single block of CMU memory?")

args = parser.parse_args()

if args.group_num < 1 or args.group_num > 9:
    print("Invalid Number of CMU-Groups, need to in [1, 9].")
    exit(1)
if args.memory not in MEM_CONFIGS.keys():
    print("Invalid Memory Type. Need in:")
    print(str(list(MEM_CONFIGS.keys())))
    exit(1)

# ===================================================
# CMU_GROUPS configs.
# ===================================================
GROUP_TYPES = [2, 1, 2, 1, 2, 1, 2, 1, 2]
TOTAL_CMU_GROUP_NUM  = args.group_num

CMU_PER_GROUP   = 3
MEMORY_PER_CMU  = MEM_CONFIGS[args.memory]

CANDIDATE_KEY_LIST = {
    "hdr.ipv4.src_addr" : 32,
    "hdr.ipv4.dst_addr" : 32,
    "hdr.ports.src_port": 16,
    "hdr.ports.dst_port": 16,
    "hdr.ipv4.protocol" :  8
}
CANDIDATE_KEY_SET = ",".join(CANDIDATE_KEY_LIST.keys())
                 
CMUG_GROUP_CONFIGS = []
# Definition for configurations of CMU Groups.
CMUG_GROUP_CONFIGS += (
    [{
            "id" : id + 1,
            "type" : GROUP_TYPES[id],
            "mau_start" : id,
            # Meta ID is used for specifing which metadata tu use. It has two functions:
                # a) Chain the two groups to enable inter-group collaboration.
                # b) Reuse PHV bits. 
            "meta_id" : (id % 4) + 1,
            "cmu_num" : CMU_PER_GROUP,
            "cmu_size" : MEMORY_PER_CMU["size"],
            "key_bitw" : MEMORY_PER_CMU["bit_width"],
            "candidate_key_list" : CANDIDATE_KEY_LIST,
            # Next non-overlay group.
            "next_group" : id + 1 + 4 if id + 1 + 4 < TOTAL_CMU_GROUP_NUM else 0
    }for id in range(TOTAL_CMU_GROUP_NUM)]
)

# Add std params configs.
for CMUG in CMUG_GROUP_CONFIGS:
    if CMUG["id"] == 1:
        CMUG["std_params"] = { 
                                "pkt_size" : "(bit<16>) intr_md.pkt_length",
                                "queue_size" : "intr_md.enq_qdepth[15:0]",
                                "timestamp" : "intr_md.enq_tstamp[15:0];"
                            }
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