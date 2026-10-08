import numpy as np

def get_level(index):
    """
    Returns (name, coords, edges, par_colors) for the requested level.
    par_colors is the mathematically proven minimum colors needed.
    """
    h = np.sqrt(3) / 2
    
    if index == 0:
        name = "The Gem"
        # Two connected triangles forming a diamond
        coords = [(0, 0), (1, 0), (0.5, h), (0.5, -h)]
        edges = [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)]
        return name, coords, edges, 3

    elif index == 1:
        name = "The Lotus"
        # A center node surrounded by 6 nodes (Hexagon made of 6 triangles)
        coords = [(0, 0)]
        edges = []
        for i in range(6):
            angle = i * np.pi / 3
            coords.append((np.cos(angle), np.sin(angle)))
            edges.append((0, i + 1))
            edges.append((i + 1, (i + 1) % 6 + 1))
        return name, coords, edges, 3

    elif index == 2:
        name = "The Crown"
        # A row of 4 triangles
        coords = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            (0.5, h), (1.5, h), (2.5, h), (3.5, h)
        ]
        edges = [
            (0,1), (1,2), (2,3), (3,4),  # Bottom bases
            (0,5), (1,5), (1,6), (2,6), (2,7), (3,7), (3,8), (4,8), # Peaks to bases
            (5,6), (6,7), (7,8) # Peak to peak (unit distance!)
        ]
        return name, coords, edges, 3

    elif index == 3:
        name = "The Starfighter (Moser Spindle)"
        # The classic 4-chromatic graph
        theta = np.arccos(5.0 / 6.0)
        c, s = np.cos(theta), np.sin(theta)
        rot = np.array([[c, -s], [s, c]])
        
        p1 = np.array([1.0, 0.0])
        p2 = np.array([0.5, h])
        p3 = np.array([1.5, h])
        
        coords = [
            (0, 0), tuple(p1), tuple(p2), tuple(p3),
            tuple(rot @ p1), tuple(rot @ p2), tuple(rot @ p3)
        ]
        edges = [
            (0, 1), (0, 2), (1, 3), (2, 3), (1, 2),
            (0, 4), (0, 5), (4, 6), (5, 6), (4, 5),
            (3, 6)
        ]
        return name, coords, edges, 4
        
    return None, None, None, None
