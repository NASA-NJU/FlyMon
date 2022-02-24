#!/usr/bin/python
# pip install z3-solver==4.5.1.0
from z3 import *

def end():
    print("=======================================")
# solve basic equality with constrains.
x = Int('x')
y = Int('y')
solve(x > 2, y < 10, x + 2*y == 7)
end()

# simplify basic equality with constrains.
x = Int('x')
y = Int('y')
print (simplify(x + y + 2*x + 3))
print (simplify(x < y + x + 2))
print (simplify(And(x + 1 >= 3, x**2 + x**2 + y**2 + 2 >= 5)))
end()

# get Z3 tree attributes.
x = Int('x')
y = Int('y')
n = x + y >= 3
print ("num args: ", n.num_args())
print ("children: ", n.children())
print ("1st child:", n.arg(0))
print ("2nd child:", n.arg(1))
print ("operator: ", n.decl())
print ("op name:  ", n.decl().name())
end()

# ZE solve real number
x = Real('x')
y = Real('y')
solve(x**2 + y**2 > 3, x**3 + y < 5)
end()

x = Real('x')
y = Real('y')
solve(x**2 + y**2 == 3, x**3 == 2)

set_option(precision=30)
print( "Solving, and displaying result with 30 decimal places")
solve(x**2 + y**2 == 3, x**3 == 2)
end()

print (1/3)
print (RealVal(1)/3)
print (Q(1,3))

x = Real('x')
print (x + 1/3)
print (x + Q(1,3))
print (x + "1/3")
print (x + 0.25)
end()

x = Real('x')
solve(3*x == 1)

set_option(rational_to_decimal=True)
solve(3*x == 1)

set_option(precision=30)
solve(3*x == 1)
end()

x = Real('x')
solve(x > 4, x < 0)
end()


## Boolean Logic
p = Bool('p')
q = Bool('q')
r = Bool('r')
# Implies Or(Not(p), q), can not p only be true. If p is true, then q is true. p => q.
solve(Implies(p, q), r == Not(q), Or(Not(p), r))
end()

p = Bool('p')
q = Bool('q')
print (And(p, q, True))
print (simplify(And(p, q, True)))
print (simplify(And(p, False)))
end()

# Sover example
x = Int('x')
y = Int('y')
s = Solver()
print (s)

s.add(x > 10, y == x + 2)
print (s)
print ("Solving constraints in the solver s ...")
print (s.check())

print ("Create a new scope...")
s.push()
s.add(y < 11)
print (s)
print ("Solving updated set of constraints...")
print (s.check())

print ("Restoring state...")
s.pop()
print (s)
print ("Solving restored set of constraints...")
s.push()
s.add(y < 14)
print (s)
print (s.check())
end()

##
x, y = Reals('x y')
# Put expression in sum-of-monomials form
t = simplify((x + y)**3, som=True)
print (t)
# Use power operator
t = simplify(t, mul_to_power=True)
print (t)
end()


x = BitVec('x', 16)
y = BitVec('y', 16)
print (x + 2)
# Internal representation
print ((x + 2).sexpr())

# -1 is equal to 65535 for 16-bit integers 
print (simplify(x + y - 1))

# Creating bit-vector constants
a = BitVecVal(-1, 16)
b = BitVecVal(65535, 16)
print (simplify(a == b))

a = BitVecVal(-1, 32)
b = BitVecVal(65535, 32)
# -1 is not equal to 65535 for 32-bit integers 
print (simplify(a == b))
end()


# Create to bit-vectors of size 32
x, y = BitVecs('x y', 32)

solve(x + y == 2, x > 0, y > 0)

# Bit-wise operators
# & bit-wise and
# | bit-wise or
# ~ bit-wise not
solve(x & y == ~y)

solve(x < 0)

# using unsigned version of < 
solve(ULT(x, 0))

end()

x = [1,2,3,4,5]
s = Solver()
s.add(Sum(x) > 1000)
print (s)
print ("Solving constraints in the solver s ...")
print (s.check())