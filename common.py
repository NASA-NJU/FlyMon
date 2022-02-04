MEM_CONFIGS = {
    "unit_level_micro": {"size" : 64,  "bit_width" :   6},     # used for debug.
    "unit_level_mini" : {"size" : 128,  "bit_width" :  7},     # used for debug.
    "unit_level_0" : {"size" : 256,    "bit_width" :   8},     # used for debug.
    "unit_level_1" : {"size" : 512,    "bit_width" :   9},     # 6,144 B 
    "unit_level_2" : {"size" : 1024,   "bit_width" :  10},     # 12,288 B 
    "unit_level_3" : {"size" : 2048,   "bit_width" :  11},     # 24,576 B 
    "unit_level_4" : {"size" : 4096,   "bit_width" :  12},     # 49,152 B
    "unit_level_5" : {"size" : 8192,   "bit_width" :  13},     # 98,304 B
    "unit_level_6" : {"size" : 16384,  "bit_width" :  14},     # 196,608 B
    "unit_level_7" : {"size" : 32768,  "bit_width" :  15},     # 393,216 B
    "unit_level_8" : {"size" : 65536,  "bit_width" :  16},     # 
}

HASH_SEEDS = [
    {"id" : 0, "len" : 8, "val" :  0x02},
    {"id" : 1, "len" : 16, "val" : 0x0305},
    {"id" : 2, "len" : 8, "val" :  0xc5},
    {"id" : 3, "len" : 16, "val" : 0x7fff},
    {"id" : 4, "len" : 8, "val" :  0x43},
    {"id" : 5, "len" : 16, "val" : 0x0305},
    {"id" : 6, "len" : 8, "val" : 0x6b},
    {"id" : 7, "len" : 16, "val" : 0x21b5},
    {"id" : 8, "len" : 16, "val" : 0x89f5},
    {"id" : 9, "len" : 16, "val" : 0xb947},
    {"id" : 10, "len" : 16, "val" : 0x0115},
    {"id" : 11, "len" : 16, "val" : 0x7fff},
    {"id" : 12, "len" : 8, "val" :  0x47},
    {"id" : 14, "len" : 16, "val" : 0x35c3},
    {"id" : 15, "len" : 16, "val" : 0xc211},
    {"id" : 16, "len" : 16, "val" : 0x6ff5},
    {"id" : 17, "len" : 16, "val" : 0xa7fb},
    {"id" : 18, "len" : 16, "val" : 0x6343},
    {"id" : 19, "len" : 16, "val" : 0xc27d},
    {"id" : 20, "len" : 16, "val" : 0xa7fb},
    {"id" : 21, "len" : 16, "val" : 0x6343},
    {"id" : 22, "len" : 16, "val" : 0xc27d},
    {"id" : 23, "len" : 16, "val" : 0xa7fb},
    {"id" : 24, "len" : 16, "val" : 0x6343},
    {"id" : 25, "len" : 16, "val" : 0xc27d}
]

