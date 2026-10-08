from pysat.solvers import Glucose42
from pysat.formula import CNF

def check_k_colorability(num_nodes: int, edges: list[tuple[int, int]], k_colors: int):
    if num_nodes == 0:
        return True, {}
    
    cnf = CNF()
    def var(node, color):
        return node * k_colors + color + 1

    for v in range(num_nodes):
        cnf.append([var(v, c) for c in range(k_colors)])

    for v in range(num_nodes):
        for c1 in range(k_colors):
            for c2 in range(c1 + 1, k_colors):
                cnf.append([-var(v, c1), -var(v, c2)])

    for u, v in edges:
        for c in range(k_colors):
            cnf.append([-var(u, c), -var(v, c)])

    with Glucose42(bootstrap_with=cnf) as solver:
        if solver.solve():
            model = set(solver.get_model())
            coloring = {}
            for v in range(num_nodes):
                for c in range(k_colors):
                    if var(v, c) in model:
                        coloring[v] = c + 1  # 1-indexed to match our palette
                        break
            return True, coloring
        return False, None
