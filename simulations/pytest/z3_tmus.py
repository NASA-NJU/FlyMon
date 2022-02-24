#!/usr/bin/python
# pip install z3-solver==4.5.1.0
from z3 import *
from multiprocessing import  Process, Queue

NUM_OF_MAUS = 12
PHV_BITS_PER_MAU = 32 * 14
HASH_PER_MAU = 6
SALU_PER_MAU = 4

def tmus_z3_solver(process_id, msg_queue, tmus_num, tmu_phv_config, tmu_hash_config, tmu_salu_config):
    print("Process id %d, solving tmus_num %d!" %(process_id, tmus_num))
    tmu_size = len(tmu_phv_config)
    tmu_phv_cost = Array ('phv', IntSort(), IntSort())
    tmu_hash_cost = Array ('hash', IntSort(), IntSort())
    tmu_salu_cost = Array ('salu', IntSort(), IntSort())
    for i in range(tmu_size):
        tmu_phv_cost = Store(tmu_phv_cost, i, tmu_phv_config[i])
        tmu_hash_cost = Store(tmu_hash_cost, i, tmu_hash_config[i])
        tmu_salu_cost = Store(tmu_salu_cost, i, tmu_salu_config[i])

    tmus_start = [ Int('tmu_%i_start' % (i + 1)) for i in range(tmus_num) ]
    tmus_end =   [ Int('tmu_%i_end' % (i + 1)) for i in range(tmus_num) ]
    # Constrains the tmus begin and end.
    pos_start_c  = [ And(1 < tmus_start[i], tmus_start[i] < NUM_OF_MAUS) for i in range(tmus_num) ]
    pos_end_c  = [ And(tmus_start[i] + tmu_size - 1 == tmus_end[i], tmus_end[i] < NUM_OF_MAUS) for i in range(tmus_num) ]

    tmus_bitmap = [ [ Int("x_%s_%s" % (i+1, j+1)) for j in range(NUM_OF_MAUS) ]
                    for i in range(tmus_num) ]

    # Constrains the tmus positions.
    bitmap_value_c = [ And(0 <= tmus_bitmap[i][j], tmus_bitmap[i][j] <= 1) 
                    for j in range(NUM_OF_MAUS) for i in range(tmus_num) ]
    bitmap_range_c = [ If(And(j >= tmus_start[i], j <= tmus_end[i]), tmus_bitmap[i][j] == 1, tmus_bitmap[i][j] == 0) 
                    for j in range(NUM_OF_MAUS) for i in range(tmus_num) ]

    # Constrains  resources per mau.
    phv_resources_c =  [ Sum([tmus_bitmap[j][i] * If(And(i >= tmus_start[j], i<=tmus_end[j]), Select(tmu_phv_cost, i - tmus_start[j]), 0) for j in range(tmus_num)]) <= PHV_BITS_PER_MAU 
                        for i in range(NUM_OF_MAUS) ]
    hash_resources_c = [ Sum([tmus_bitmap[j][i] * If(And(i >= tmus_start[j], i<=tmus_end[j]), Select(tmu_hash_cost, i - tmus_start[j]), 0)  for j in range(tmus_num) ]) <= HASH_PER_MAU 
                        for i in range(NUM_OF_MAUS) ]
    salu_resources_c = [ Sum([tmus_bitmap[j][i] * If(And(i >= tmus_start[j], i<=tmus_end[j]), Select(tmu_salu_cost, i - tmus_start[j]), 0)  for j in range(tmus_num) ]) <= SALU_PER_MAU 
                        for i in range(NUM_OF_MAUS)]

    s = Solver()
    s.add(pos_start_c + pos_end_c + bitmap_value_c + bitmap_range_c + phv_resources_c + hash_resources_c + salu_resources_c)
    s.set("timeout", 60 * 1000) ## ms
    # s.add(pos_start_c + pos_end_c + bitmap_value_c + bitmap_range_c)
    re = s.check()
    if re == sat:
        m = s.model()
        # r = [ [ m.evaluate(tmus_bitmap[i][j]) for j in range(NUM_OF_MAUS) ] for i in range(tmus_num) ]
        r = [ [ m[tmus_bitmap[i][j]].as_long() for j in range(NUM_OF_MAUS) ] for i in range(tmus_num) ]
        # print_matrix(r)
        msg_queue.put((True, tmus_num, r))
    else:
        msg_queue.put((False, tmus_num, None))
    print("Process id %d, solved tmus_num %d, result %s!" %(process_id, tmus_num, re))

def get_tmu_head(lst):
    f1 = 0
    for i in range(len(lst)):
        if lst[i] == 1:
            f1 = i
            break
    return f1

def get_tmu_tail(lst):
    f1 = 0
    for i in range(len(lst)-1, 0, -1):
        if lst[i] == 1:
            f1 = i
            break
    return f1
    
def cmp_tmu(lst1, lst2):
    f1 = get_tmu_head(lst1)
    f2 = get_tmu_head(lst2)
    if f1 > f2:
        return 1;
    if f1 == f2:
        return 0;
    if f1 < f2:
        return -1;

def get_cost(config, tmu, i):
    if i >= get_tmu_head(tmu) and i <= get_tmu_tail(tmu):
        return config[i-get_tmu_head(tmu)]
    else:
        return 0
    pass
if __name__ == "__main__":
    tmu_phv_config =  [96, 96, 96]
    tmu_hash_config = [1,   0,  0]
    tmu_salu_config = [0,   0,  1]
    ### Begin resolve.
    thread_num = 3
    results = []
    stop = False
    begin_tmus_num = 3
    while not stop:
        process_list = []
        tmus_placement = None
        msg_queue = Queue()
        for i in range(thread_num):  
            p = Process(target=tmus_z3_solver,args=(i, msg_queue, begin_tmus_num, tmu_phv_config, tmu_hash_config, tmu_salu_config)) 
            
            p.start()
            process_list.append(p)
            begin_tmus_num = begin_tmus_num + 1
        cnt = 0
        while cnt != thread_num and not stop:
            fit, tnums_num, placement = msg_queue.get()
            results.append((tnums_num, placement))
            cnt += 1
            if fit is False:
                stop = True
                for p in process_list:
                    p.terminate()
    max_tmus_num = 0
    max_tmus_placement = None
    for tnums_num, tmus_placement in results:
        if tmus_placement!=None and max_tmus_num < tnums_num:
            max_tmus_num = tnums_num
            max_tmus_placement = tmus_placement
    print("TMU PHV Cost:  %s" % (tmu_phv_config))
    print("TMU HASH Cost: %s" % (tmu_hash_config))
    print("TMU SALU Cost: %s" % (tmu_salu_config))
    print("Max tmus num:  %d" % (max_tmus_num))
    print("TMUs allocations:")
    print_matrix(sorted(max_tmus_placement, cmp_tmu))
    print("Pipeline MAU PHV resources (TOTAL %d): " %(PHV_BITS_PER_MAU))
    print([sum([max_tmus_placement[j][i] * get_cost(tmu_phv_config,  max_tmus_placement[j], i) for j in range(max_tmus_num)])
                        for i in range(NUM_OF_MAUS) ])
    print("Pipeline MAU HASH resources (TOTAL %d): " %(HASH_PER_MAU))
    print([sum([max_tmus_placement[j][i] * get_cost(tmu_hash_config, max_tmus_placement[j], i) for j in range(max_tmus_num)])
                        for i in range(NUM_OF_MAUS) ])
    print("Pipeline MAU SALU resources (TOTAL %d): " %(SALU_PER_MAU))
    print([sum([max_tmus_placement[j][i] * get_cost(tmu_salu_config, max_tmus_placement[j], i) for j in range(max_tmus_num)])
                        for i in range(NUM_OF_MAUS) ])