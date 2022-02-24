import sys

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac

if len(sys.argv) < 4:
    exit()
m = int(sys.argv[1])
n = int(sys.argv[2])
p = convert_to_float(sys.argv[3])
print("M=%d, N=%d, P=%f" %(m, n, p))
target = 0
var = 0
for i in range(n):
    P = p * (m - i)
    target += 1/P
    var += (1-P)/(P**2)
std_var = pow(var, 0.5)
RE = std_var / target
print("M=%d, N=%d, P=%f, Target=%.2f, Var=%.2f, RE=%.2f" %(m, n, p, target, std_var, RE))
