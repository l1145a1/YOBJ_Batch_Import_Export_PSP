class OBJ:
    def __init__(self, filename):
        self.vertex = []
        self.normal = []
        self.face = []
        self.uv = []  # Tambahkan UV
        self.load(filename)

    def load(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    parts = line.strip().split()
                    self.vertex.append([float(parts[1]), float(parts[2]), float(parts[3])])
                elif line.startswith('vn '):
                    parts = line.strip().split()
                    self.normal.append([float(parts[1]), float(parts[2]), float(parts[3])])
                elif line.startswith('vt '):
                    parts = line.strip().split()
                    self.uv.append([float(parts[1]), float(parts[2])])
                elif line.startswith('f '):
                    parts = line.strip().split()
                    self.face.append([tuple(map(lambda x: int(x.split('/')[0]) - 1, part.split('/'))) for part in parts[1:]])
