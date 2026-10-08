import numpy as np

def generate_mandala(seed, iterations=12):
    """
    Grows a random unit-distance graph using 6-fold symmetry 
    to create beautiful, complex procedural mandalas.
    """
    np.random.seed(seed)
    nodes = [(0.0, 0.0)]
    
    for _ in range(iterations):
        # Pick a random existing node to branch from
        idx = np.random.randint(len(nodes))
        base_x, base_y = nodes[idx]
        
        # Branch out at a random angle
        angle = np.random.uniform(0, 2 * np.pi)
        nx = base_x + np.cos(angle)
        ny = base_y + np.sin(angle)
        
        # Apply 6-fold symmetry to make it a Mandala
        for i in range(6):
            theta = i * (np.pi / 3)
            c, s = np.cos(theta), np.sin(theta)
            rx = nx * c - ny * s
            ry = nx * s + ny * c
            nodes.append((rx, ry))
            
    # Deduplicate nodes that land in the same spot (epsilon 1e-4)
    unique_nodes = []
    for n in nodes:
        is_dup = False
        for u in unique_nodes:
            if (n[0]-u[0])**2 + (n[1]-u[1])**2 < 1e-5:
                is_dup = True
                break
        if not is_dup:
            unique_nodes.append(n)
            
    # Map all edges that are exactly distance 1.0
    edges = []
    for i in range(len(unique_nodes)):
        for j in range(i + 1, len(unique_nodes)):
            d = np.sqrt((unique_nodes[i][0]-unique_nodes[j][0])**2 + (unique_nodes[i][1]-unique_nodes[j][1])**2)
            if abs(d - 1.0) < 1e-3:
                edges.append((i, j))
                
    return unique_nodes, edges
