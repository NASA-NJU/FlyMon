total_second = 100

AVG_DELAY_PER_SEC = [0] * total_second
for i in range(total_second):
    fname = f"latency_sec_{i+1}.txt"
    f = open(fname, "r")
    lines = f.readlines()
    for line in lines:
        if "rtt" in line:
            items = line.split("/")
            avg = float(items[4])
            AVG_DELAY_PER_SEC[i] = avg

for idx, rtt in enumerate(AVG_DELAY_PER_SEC):
    print("%d, %.2f" % (idx+1, rtt))