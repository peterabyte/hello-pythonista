# ---------- CubeModel (sticker-based) ----------
# Faces order: U, R, F, D, L, B
# Colors are single-letter face ids for clarity ('U','R','F','D','L','B')
# You can map them to your FACE_COLORS in your UI if you later want to draw stickers.

from collections import deque
import copy

FACE_INDEX = {'U':0, 'R':1, 'F':2, 'D':3, 'L':4, 'B':5}
INDEX_FACE = {v:k for k,v in FACE_INDEX.items()}

def rot_cw(face):
    # Rotate a 3x3 face 90° clockwise
    return [
        face[6], face[3], face[0],
        face[7], face[4], face[1],
        face[8], face[5], face[2],
    ]

def rot_ccw(face):
    # 90° counter-clockwise
    return [
        face[2], face[5], face[8],
        face[1], face[4], face[7],
        face[0], face[3], face[6],
    ]

def rot_180(face):
    return [
        face[8], face[7], face[6],
        face[5], face[4], face[3],
        face[2], face[1], face[0],
    ]

class CubeModel:
    def __init__(self):
        # 6 faces × 9 stickers (row-major)
        self.faces = [
            ['U']*9,  # U
            ['R']*9,  # R
            ['F']*9,  # F
            ['D']*9,  # D
            ['L']*9,  # L
            ['B']*9,  # B
        ]
        self.rotate_x_180()  # Adjust to UI orientation

    def rotate_x_180(self):
        # Swap U and D faces
        self.faces[0], self.faces[3] = self.faces[3], self.faces[0]
        # You may also need to rotate the swapped faces to maintain orientation
        self.faces[0] = rot_180(self.faces[0])
        self.faces[3] = rot_180(self.faces[3])
        # Swap and rotate F/B faces as needed for correct orientation
        self.faces[2], self.faces[5] = rot_180(self.faces[5]), rot_180(self.faces[2])

    def clone(self):
        c = CubeModel()
        c.faces = copy.deepcopy(self.faces)
        return c

    def is_solved(self):
        return all(all(s == row[0] for s in row) for row in self.faces)

    # ---- Face turns (quarter-turn metric). Each mutates self.faces. ----
    # Notation: "U", "U'", "U2", ..., over standard Singmaster mapping.
    # The side cycles were hand-checked; they're standard.

    def U(self):  # Up face CW
        f = self.faces
        f[0] = rot_cw(f[0])
        # side ring: F row0 <- R row0 <- B row0 <- L row0
        (f[2][0], f[2][1], f[2][2],
         f[1][0], f[1][1], f[1][2],
         f[5][0], f[5][1], f[5][2],
         f[4][0], f[4][1], f[4][2]) = (
         f[1][0], f[1][1], f[1][2],
         f[5][0], f[5][1], f[5][2],
         f[4][0], f[4][1], f[4][2],
         f[2][0], f[2][1], f[2][2])

    def U_(self):
        for _ in range(3): self.U()

    def U2(self):
        for _ in range(2): self.U()

    def D(self):  # Down face CW
        f = self.faces
        f[3] = rot_cw(f[3])
        # F row2 -> L row2 -> B row2 -> R row2
        (f[2][6], f[2][7], f[2][8],
         f[4][6], f[4][7], f[4][8],
         f[5][6], f[5][7], f[5][8],
         f[1][6], f[1][7], f[1][8]) = (
         f[4][6], f[4][7], f[4][8],
         f[5][6], f[5][7], f[5][8],
         f[1][6], f[1][7], f[1][8],
         f[2][6], f[2][7], f[2][8])

    def D_(self):
        for _ in range(3): self.D()

    def D2(self):
        for _ in range(2): self.D()

    def R(self):
        f = self.faces
        f[1] = rot_cw(f[1])
        # U col2 -> F col2 -> D col2 -> B col0 (reversed)
        (f[0][2], f[0][5], f[0][8],
         f[2][2], f[2][5], f[2][8],
         f[3][2], f[3][5], f[3][8],
         f[5][6], f[5][3], f[5][0]) = (
         f[2][2], f[2][5], f[2][8],
         f[3][2], f[3][5], f[3][8],
         f[5][6], f[5][3], f[5][0],
         f[0][2], f[0][5], f[0][8])

    def R_(self):
        for _ in range(3): self.R()

    def R2(self):
        for _ in range(2): self.R()

    def L(self):
        f = self.faces
        f[4] = rot_cw(f[4])
        # U col0 -> B col2 (reversed) -> D col0 -> F col0
        (f[0][0], f[0][3], f[0][6],
         f[5][8], f[5][5], f[5][2],
         f[3][0], f[3][3], f[3][6],
         f[2][0], f[2][3], f[2][6]) = (
         f[5][8], f[5][5], f[5][2],
         f[3][0], f[3][3], f[3][6],
         f[2][0], f[2][3], f[2][6],
         f[0][0], f[0][3], f[0][6])

    def L_(self):
        for _ in range(3): self.L()

    def L2(self):
        for _ in range(2): self.L()

    def F(self):
        f = self.faces
        f[2] = rot_cw(f[2])
        # U row2 -> R col0 -> D row0 -> L col2
        (f[0][6], f[0][7], f[0][8],
         f[1][0], f[1][3], f[1][6],
         f[3][2], f[3][1], f[3][0],
         f[4][8], f[4][5], f[4][2]) = (
         f[4][8], f[4][5], f[4][2],
         f[0][6], f[0][7], f[0][8],
         f[1][0], f[1][3], f[1][6],
         f[3][2], f[3][1], f[3][0])

    def F_(self):
        for _ in range(3): self.F()

    def F2(self):
        for _ in range(2): self.F()

    def B(self):
        f = self.faces
        f[5] = rot_cw(f[5])
        # U row0 -> L col0 -> D row2 -> R col2
        (f[0][0], f[0][1], f[0][2],
         f[4][0], f[4][3], f[4][6],
         f[3][8], f[3][7], f[3][6],
         f[1][2], f[1][5], f[1][8]) = (
         f[1][2], f[1][5], f[1][8],
         f[0][0], f[0][1], f[0][2],
         f[4][0], f[4][3], f[4][6],
         f[3][8], f[3][7], f[3][6])

    def B_(self):
        for _ in range(3): self.B()

    def B2(self):
        for _ in range(2): self.B()

    # Apply a single move token
    def move(self, m):
        # m in {'U','U\'','U2', ...}
        base = m[0]
        suf = m[1:] if len(m) > 1 else ''
        fn = getattr(self, base)
        if suf == "'":
            fn = getattr(self, base + "_")
        elif suf == "2":
            fn2 = getattr(self, base + "2")
            fn2()
            return
        fn()

    def apply(self, seq):
        for m in seq:
            self.move(m)

    def as_string(self):
        # Simple string for debugging
        return ''.join(''.join(face) for face in self.faces)
