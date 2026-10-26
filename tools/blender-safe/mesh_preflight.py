"""Pure-Python checks for proposed vertex/face data; no Blender imports."""
import math
from collections import defaultdict


def validate(data, max_vertices=5000, max_faces=10000, closed=True):
    errors = []
    vertices, faces = data.get("vertices", []), data.get("faces", [])
    if not vertices or not faces:
        return {"passed": False, "errors": ["Empty mesh"]}
    if len(vertices) > max_vertices or len(faces) > max_faces:
        return {"passed": False, "errors": ["Mesh exceeds workload budget"]}
    if any(not isinstance(v, list) or len(v) != 3 or
           any(type(x) not in (int, float) or not math.isfinite(x) for x in v)
           for v in vertices):
        return {"passed": False, "errors": ["Invalid or non-finite vertex"]}
    edges, seen = defaultdict(list), set()
    adjacency = defaultdict(set)
    used = set()
    for index, face in enumerate(faces):
        if (not isinstance(face, list) or len(face) < 3 or
                any(type(i) is not int or not 0 <= i < len(vertices) for i in face)):
            errors.append(f"Face {index}: invalid indices")
            continue
        if len(set(face)) != len(face):
            errors.append(f"Face {index}: repeated vertex")
            continue
        key = tuple(sorted(face))
        if key in seen:
            errors.append(f"Face {index}: duplicate vertex set")
        seen.add(key)
        # Newell area vector detects zero-area polygons; not a self-intersection test.
        normal = [0.0, 0.0, 0.0]
        for a, b in zip(face, face[1:] + face[:1]):
            p, q = vertices[a], vertices[b]
            for axis in range(3):
                normal[axis] += (p[(axis+1)%3] - q[(axis+1)%3]) * (p[(axis+2)%3] + q[(axis+2)%3])
            edges[tuple(sorted((a, b)))].append((a, b))
            adjacency[a].add(b)
            adjacency[b].add(a)
        if not all(math.isfinite(x) for x in normal) or not any(normal):
            errors.append(f"Face {index}: zero or non-finite area vector")
        used.update(face)
    boundary = sum(len(v) == 1 for v in edges.values())
    branching = sum(len(v) > 2 for v in edges.values())
    winding = sum(len(v) == 2 and v[0] == v[1] for v in edges.values())
    remaining, components = set(used), 0
    while remaining:
        components += 1
        pending = [remaining.pop()]
        while pending:
            for neighbor in adjacency[pending.pop()]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
    if branching:
        errors.append("Edges with more than two incident faces")
    if winding:
        errors.append("Inconsistent face winding")
    if closed and boundary:
        errors.append("Unexpected boundary edges")
    if components != 1:
        errors.append("Expected one connected component")
    if len(used) != len(vertices):
        errors.append("Loose vertices")
    return {"passed": not errors, "errors": errors, "vertices": len(vertices),
            "faces": len(faces), "components": components,
            "boundary_edges": boundary, "branching_edges": branching,
            "winding_errors": winding}
