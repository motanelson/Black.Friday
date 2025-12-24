import struct
import sys
import os

SECTOR = 512
CLUSTER = 4096
MAGIC = b"MYSYS "

def u32(b,o): return struct.unpack_from("<I", b, o)[0]
def w32(b,o,v): struct.pack_into("<I", b, o, v)

# -------------------------------------------------
# NTFSX CORE
# -------------------------------------------------

class NTFSX:
    def __init__(self, img):
        self.f = open(img, "r+b")
        self.load_super()
        self.load_bitmap()

    def load_super(self):
        self.f.seek(0)
        sb = self.f.read(SECTOR)
        if sb[3:9] != MAGIC:
            raise RuntimeError("Não é NTFSX")
        self.total_clusters = u32(sb, 8)
        self.bitmap_cluster = 1
        self.mft_cluster = 2
        self.data_start = 3

    def load_bitmap(self):
        self.f.seek(self.bitmap_cluster * CLUSTER)
        self.bitmap = bytearray(self.f.read(CLUSTER))

    def save_bitmap(self):
        self.f.seek(self.bitmap_cluster * CLUSTER)
        self.f.write(self.bitmap)

    # ---------------- clusters ----------------

    def alloc_cluster(self):
        for i in range(self.data_start, self.total_clusters):
            byte = i // 8
            bit  = i % 8
            if not (self.bitmap[byte] & (1 << bit)):
                self.bitmap[byte] |= (1 << bit)
                self.save_bitmap()
                return i
        raise RuntimeError("Disco cheio")

    def read_cluster(self, c):
        self.f.seek(c * CLUSTER)
        return self.f.read(CLUSTER)

    def write_cluster(self, c, data):
        self.f.seek(c * CLUSTER)
        self.f.write(data.ljust(CLUSTER, b'\x00'))

    # ---------------- MFT ----------------

    def read_mft(self):
        data = self.read_cluster(self.mft_cluster)
        records = []
        for i in range(0, CLUSTER, 128):
            r = data[i:i+128]
            if r[0] == 0:
                continue
            name = r[0:32].split(b'\x00')[0].decode()
            typ  = r[32]
            size = u32(r,33)
            first = u32(r,37)
            records.append((name,typ,size,first,i))
        return records

    def add_mft(self, name, typ, size, first):
        data = bytearray(self.read_cluster(self.mft_cluster))
        for i in range(0, CLUSTER, 128):
            if data[i] == 0:
                data[i:i+32] = name.encode()[:32].ljust(32,b'\x00')
                data[i+32] = typ
                w32(data,i+33,size)
                w32(data,i+37,first)
                self.write_cluster(self.mft_cluster, data)
                return i
        raise RuntimeError("MFT cheia")

    # ---------------- files ----------------

    def write_chain(self, data):
        first = prev = 0
        for i in range(0, len(data), CLUSTER-4):
            c = self.alloc_cluster()
            blk = bytearray(CLUSTER)
            if prev:
                w32(prev_blk, 0, c)
                self.write_cluster(prev, prev_blk)
            if first == 0:
                first = c
            blk[4:] = data[i:i+CLUSTER-4]
            prev_blk = blk
            prev = c
        w32(prev_blk,0,0)
        self.write_cluster(prev, prev_blk)
        return first

    def read_chain(self, first):
        out = bytearray()
        c = first
        while c != 0:
            blk = self.read_cluster(c)
            nxt = u32(blk,0)
            out += blk[4:]
            c = nxt
        return out

# -------------------------------------------------
# SHELL
# -------------------------------------------------

def shell(img):
    fs = NTFSX(img)
    cwd = "/"

    while True:
        cmd = input(f"{cwd}> ").strip().split()
        if not cmd:
            continue

        if cmd[0] == "exit":
            break

        if cmd[0] == "dir":
            for n,t,s,f,_ in fs.read_mft():
                print(f"{n:20} {'<DIR>' if t else s}")

        elif cmd[0] == "type":
            for n,t,s,f,_ in fs.read_mft():
                if n == cmd[1] and t == 0:
                    data = fs.read_chain(f)
                    print(data[:s].decode(errors="ignore"))
                    break

        elif cmd[0] == "mkdir":
            c = fs.alloc_cluster()
            fs.write_cluster(c, b'\x00')
            fs.add_mft(cmd[1], 1, 0, c)

        elif cmd[0] == "copy":
            data = open(cmd[1],"rb").read()
            first = fs.write_chain(data)
            fs.add_mft(os.path.basename(cmd[1]), 0, len(data), first)

        else:
            print("Comandos: dir type mkdir copy exit")

# -------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Uso: python ntfsx_shell.py disco.img")
        sys.exit(1)
    shell(sys.argv[1])
