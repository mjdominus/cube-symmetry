#!/usr/bin/python3

from pprint import pprint

def flatten(ls):
    res = []
    for i in ls: res += i
    return res

# given a list, rearrange it **cyclically**
# so that the lexicographically-first element is first
def crudsort(ls):
    first = min(ls)
    for i in range(len(ls)):
        if ls[i] == first:
            return ls[i:] + ls[0:i]

def cycle_string(cyc, esep="", fmt="(%s)"):
    if len(cyc) < 2: return ""
    else: return fmt % esep.join(crudsort([ x.__str__() for x in cyc]))

def nonesum(a, b):
    if a is None: return None
    if b is None: return None
    return a + b

def gcd2(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def gcd(*v):
    g = 0
    for i in v:
        g = gcd2(g, i)
    return g

class wedge():
    def __init__(self, f, w):
        self.f = f
        self.w = w

    def face_of(self):
      return self.f

    def __str__(self):
      return self.f + self.w.lower()

    def __eq__(self, other):
        return self.f == other.f and self.w == other.w

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.f) * 100 + hash(self.w)

    __repr__ = __str__

  
# A permutation is just a dictionary mapping
class p10n():
    def __init__(self, d, form={"esep": "", "csep": ""}, name=None):
        self.p = d
        self.form = form
        self.name = name
        self._cycles = self.cycles()
        self._str = self.__str__()

    def __hash__(self):
        return hash(self._str)

    def __eq__(self, other):
        return self._str == other._str

    def shorten_name(self, new_name):
        if new_name is None: return
        if self.name is None or len(new_name) < len(self.name):
            self.name = new_name

    def keys(self): return self.p.keys()

    def mergekeys(self, p2):
        return set(list(self.keys()) + list(p2.keys()))

    # Find the image of x under a permutation
    def image(self, x):
        if x in self.p:
            return self.p[x]
        else: return x

    # For now, he weight is simply the product of the lengths of the cycles
    def weight(self):
        w = 1
        for cyc in self.cycles():
            w *= len(cyc)
        return w

    # Todo: russian peasant version
    # N == 0
    def pow(self, n):
        if n == 1:
            return self
        elif n > 1:
            return self.following(self.pow(n-1))
        elif n == 0:
            return p10n(dict([(x, x) for x in self.keys() ]), form=self.form)
        elif n == -1:
            return self.inverse()
        else:                   # n < -1
            return self.inverse().pow(-n)

    def identity(self):
        return self.pow(0)
        
    # Apply p to every element of a list
    def apply(self, xs):
        return [ self.p[x] for x in xs ]

    # New permutation: self.andthen(p2) means apply self, then
    # 
    def andthen(self, p2):
        return p10n(dict([(x, p2.image(self.image(x)))
                          for x in self.mergekeys(p2) ]),
                    form=self.form,
                    name=nonesum(self.name, p2.name)
        )

    def following(self, p2):
        return p10n(dict([(x, self.image(p2.image(x)))
                          for x in self.mergekeys(p2) ]),
                    form=self.form,
                    name=nonesum(self.name, p2.name),
        )

    def inverse(self):
        return p10n(dict([(self.p[x], x) for x in self.keys() ]), form=self.form)

    # Orbit of x

    def orbit(self, x):
        res = [x]
        x = self.image(x)
        while x != res[0]:
            res.append(x)
            x = self.image(x)
        return res

    def cycles(self):
        todo = list(self.keys())
        verbose = todo[0] is wedge
        if verbose: print("calculating cycles of", vars(self))
        res = []
        while todo:
            if verbose: print("  todo:", todo)
            cyc = self.orbit(todo[0])
            if verbose: print("  orbit of %s: %s" % (todo[0], cyc))
            for x in cyc:
                todo.remove(x)
            res.append(cyc)
            if verbose: print(" partial result:", res)
        return res

    def __str__(self):
        cycle_strings = [ cycle_string(x, esep=self.form["esep"])
                          for x in self._cycles ]
        z = self.form["csep"].join(sorted(cycle_strings))
        if z: return z
        else: return "()"

    @classmethod
    def from_cycles(cls, ls, **kwargs):
        d = {}
        for cyc in ls:
            for i in range(len(cyc)-1):
              d[cyc[i]] = cyc[i+1]
            d[cyc[-1]] = cyc[0]
        return cls(d, **kwargs)

    def order(self):
        return gcd(*[ len(cyc) for cyc in self.cycles() ])

    @classmethod
    # Better to use DFS, but only because
    # that makes the auto-generated permutation names
    # shorter
    def closure(cls, ps):
        todo = [ (a, b) for a in ps for b in ps ]
        res = set(ps)
        while todo:
            i, j = todo.pop()
            k = i.following(j)
            seen = False
            for s in res:
                if s._str == k._str:
                    s.shorten_name(k.name)
                    seen = True
            if not seen:
                todo += [ (a, k) for a in res ]
                todo += [ (k, b) for b in res ]
                todo += [ (k, k) ]
                res.add(k)
        return res
        
# a cube has six faces called T D   L R   F B
# each has four wedges called Tf Tl TB Tr  etc.
# A cube is a mapping from 24 wedges to 6 colors
class cube():

    @classmethod
    def __class_setup__(cls):
        # Additional class member setup
        # A wedge looks like ("T", "F") for the front wedge on th
        # top face
        cls.wedges = [ wedge(f, w)
                       for f in cls.faces 
                       for w in cls.wedge_list(f) ]
        
        
    opposite = {"T": "D", "D": "T",
                "L": "R", "R": "L",
                "F": "B", "B": "F",
    }
    faces = list(opposite.keys())

    @staticmethod
    def is_opposite_to(f1, f2):
        return f1 is opposite[f2]

    @classmethod
    def wedge_list(cls, face):
        res = []
        for f in cls.faces:
            if f is face or f is cls.opposite[face]: continue
            res.append(f)
        return res
    

    colors = [ "Cr", "Co", "Cy", "Cg", "Cb", "Cw" ]

    cmap = { "T": "Co", "D": "Cr",
             "L": "Cb", "R": "Cg",
             "F": "Cw", "B": "Cy",
    }

    # given a permutation of cube faces,
    # turn it into a permutation of wedges
    @classmethod
    def lift(cls, p):
        z = [(wedge(s, w),
              wedge(p.image(s), p.image(w)))
             for s in p.keys() for w in cls.wedge_list(s)]
        p = p10n(dict(z), form={"esep": " ", "csep": ""})
        return p

    def __init__(self):
        print("self.wedges", self.wedges)
        self.c = dict([(w, self.cmap[self.face_of(w)])
                       for w in self.wedges ])


cube.__class_setup__()

## Cube motions
cmTB = p10n.from_cycles([["T", "B", "D", "F"], ["L"], ["R"]], name="back---")
cmTR = p10n.from_cycles([["T", "R", "D", "L"], ["F"], ["B"]], name="right--")
cmFR = p10n.from_cycles([["F", "R", "B", "L"], ["T"], ["D"]], name="around-")
cube_motions = p10n.closure([cmTB, cmTR])
assert(len(cube_motions) == 24)

#import pdb; pdb.set_trace()
x = cube.lift(cmTB)



## Twists
twist = p10n.from_cycles([[wedge("T", "F"),
                           wedge("R", "T"),
                           wedge("F", "R")],
                          [wedge("T", "R"),
                           wedge("R", "F"),
                           wedge("F", "T")]],
                         form={"csep": "", "esep": " "})
twist2 = twist.pow(2)
twist4 = twist2.pow(2)

#import pdb; pdb.set_trace()
print(twist)
print(twist2)
print(twist4)
assert(hash(twist) == hash(twist4))
assert(len({twist, twist2, twist4}) == 2)
assert(twist.weight() == 9)

all_twists = {
    cm.inverse().following(t.following(cm))
    for t in (twist, twist2)
    for cm in [ cube.lift(m) for m in cube_motions ]
}
# print("\n".join(sorted([str(x) for x in all_twists])))
assert(len(all_twists) == 16)

## What's the plan?  We're going to try various sequences ## of moves
## looking for ones that produce unexpectedly simple configurations

d4 =p10n.closure({
    p10n.from_cycles([["A", "B", "C", "D"]], name="R"),
    p10n.from_cycles([["A", "B"], ["C", "D"]], name="H")})
assert(len(d4) == 8)

# This is a sequence of twists, plus the resulting permutation
class move_sequence():
    def __init__(self, result, seq=None):
        if seq is None: seq = []
        self.seq = seq
        # Start in the identity configuration
        if result is None: raise Exception("result is required")
        self.result = result
        
    def compose(self, move):
        return self.__class__(move.following(self.result),
                              self.seq + [move])

a = move_sequence(twist.identity())
b = a.compose(twist)

import time
last_announce = 0
def announce(strs):
    global last_announce
    if time.monotonic() - last_announce > 6:
        last_announce = time.monotonic()
        print(int(last_announce), *strs)

def generate_moves(basic_moves, is_good, initial_config=None):
    if initial_config is None:
        initial_config = list(basic_moves)[0].identity()
    todo = [ move_sequence(initial_config) ]
    # Cube configurations already seen
    seen = { initial_config }
    while todo:
        ann = ["todo length %d" % len(todo) ]
        next_todo = todo[0]
        todo = todo[1:]
        if len(next_todo.seq) < 8:
            ann.append("item len %d" % len(next_todo.seq))
            new = list(filter(lambda s: s.result not in seen,
                              [ next_todo.compose(basic_move)
                                for basic_move in basic_moves
                              ]))
            ann.append("new items %d" % len(new))
            todo += new
            seen = seen.union([n.result for n in new])
            ann.append("seen: %d" % len(seen))
        announce(ann)
        if is_good(next_todo):
            yield next_todo

def low_weight(maxwt):
    def pred(m):
        wt = m.result.weight()
#        print("weight is " , wt)
        return wt > 1 and wt <= maxwt
    return pred

print("----")
g = generate_moves(all_twists,low_weight(8), initial_config=twist)

found = 0
for z in g:
    print(z.result)
    for m in z.seq:
        if m.name: print(m.name)
        else: print(m)
    print("--")
    found += 1
    if found > 5: break


