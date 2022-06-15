process_num = 30
total_second = 60

THROUGHPUT_PER_SEC = [0] * total_second
for i in range(process_num):
    fname = f"server{i+1}.txt"
    f = open(fname, "r")
    lines = f.readlines()
    for sec in range(total_second):
        for line in lines:
            if f"{sec}.00-{sec+1}.00" in line:
                items = line.split(" ")
                for item in list(items):
                    if item == "":
                        items.remove(item)
                bitrate = float(items[6])
                if bitrate >= 100:
                    bitrate = bitrate / 1000
                THROUGHPUT_PER_SEC[sec] += bitrate
                print(bitrate)

for idx, rate in enumerate(THROUGHPUT_PER_SEC):
    print("%d, %.2f" % (idx+1, rate))