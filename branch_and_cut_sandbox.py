from mip.model import Model, xsum
from mip.constants import BINARY
from itertools import product
from networkx import minimum_cut, DiGraph
from mip.model import *
import networkx as nx
from mip.callbacks import ConstrsGenerator, CutPool

class SubTourCutGenerator(ConstrsGenerator):
	def __init__(self, Fl: List[Tuple[int, int]]):
		self.F = Fl

	def generate_constrs(self, model: Model):
		G = nx.DiGraph()
		r = [(v, v.x) for v in model.vars if v.name.startswith('x(')]
		print(r)
		U = [int(v.name.split('(')[1].split(',')[0]) for v, f in r]
		V = [int(v.name.split(')')[0].split(',')[1]) for v, f in r]
		cp = CutPool()
		for i in range(len(U)):
			G.add_edge(U[i], V[i], capacity=r[i][1])
		for (u, v) in F:
			if u not in U or v not in V:
				continue
			val, (S, NS) = nx.minimum_cut(G, u, v)
			if val <= 0.99:
				arcsInS = [(v, f) for i, (v, f) in enumerate(r) if U[i] in S and V[i] in S]
				if sum(f for v, f in arcsInS) >= (len(S)-1)+1e-4:
					cut = xsum(1.0*v for v, fm in arcsInS) <= len(S)-1
					cp.add(cut)
					if len(cp.cuts) > 256:
						for cut in cp.cuts:
							model += cut
						return
		for cut in cp.cuts:
			model += cut
		return

N = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
A = {('a', 'd'): 56, ('d', 'a'): 67, ('a', 'b'): 49, ('b', 'a'): 50,
	('f', 'c'): 35, ('g', 'b'): 35, ('g', 'b'): 35, ('b', 'g'): 25,
	('a', 'c'): 80, ('c', 'a'): 99, ('e', 'f'): 20, ('f', 'e'): 20,
	('g', 'e'): 38, ('e', 'g'): 49, ('g', 'f'): 37, ('f', 'g'): 32,
	('b', 'e'): 21, ('e', 'b'): 30, ('a', 'g'): 47, ('g', 'a'): 68,
	('d', 'c'): 37, ('c', 'd'): 52, ('d', 'e'): 15, ('e', 'd'): 20,
	('d', 'b'): 39, ('b', 'd'): 37, ('c', 'f'): 35}
Aout = {n: [a for a in A if a[0] == n] for n in N}
Ain = {n: [a for a in A if a[1] == n] for n in N}

m = Model(sense=MINIMIZE, solver=CBC)
m.max_gap = 1
x = {a: m.add_var(name='x({},{})'.format(a[0], a[1]), var_type=BINARY) for a in A}

m.objective = xsum(c*x[a] for a, c in A.items())

for n in N:
	m += xsum(x[a] for a in Aout[n]) == 1, 'out({})'.format(n)
	m += xsum(x[a] for a in Ain[n]) == 1, 'in({})'.format(n)

a = len(A)
n = len(N)
F = []
for i in N:
	(md, dp) = (0, -1)
	for j in N:
		if i != j and (i, j) in A.keys() and A[(i, j)] > md:
			(md, dp) = (A[(i, j)], j)
	F.append((i, dp))

# m.cuts_generator = SubTourCutGenerator(F)
# m.optimize()

m.constrs_generator = SubTourCutGenerator(F)
m.constrs_generator.lazy_constraints = True
m.optimize()
m.optimize()

arcs = [(i, j) for i in N for j in N if x[i][j].x >= 0.99]
print('optimal route : {}'.format(arcs))

