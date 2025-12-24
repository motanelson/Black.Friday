import struct
import sys

SECTOR_SIZE = 512
CLUSTER_SIZE = 4096   # MYSYS usa clusters grandes normalmente

def u16(x): return struct.pack("<H", x)
def u32(x): return struct.pack("<I", x)
def u64(x): return struct.pack("<Q", x)

def mkfs_ntfs(img, size_mb):
    total_bytes = size_mb * 1024 * 1024
    total_sectors = total_bytes // SECTOR_SIZE
    sectors_per_cluster = CLUSTER_SIZE // SECTOR_SIZE
    total_clusters = total_sectors // sectors_per_cluster

    with open(img, "wb+") as f:
        f.seek(total_bytes - 1)
        f.write(b"\x00")

        boot = bytearray(SECTOR_SIZE)

        # Jump
        boot[0:3] = b'\xEB\x52\x90'
        boot[3:11] = b'MYSYS   '

        boot[11:13] = u16(SECTOR_SIZE)
        boot[13] = sectors_per_cluster
        boot[14:16] = u16(0)
        boot[16] = 0
        boot[17:19] = u16(0)
        boot[19:21] = u16(0)
        boot[21] = 0xF8
        boot[22:24] = u16(0)
        boot[24:26] = u16(63)
        boot[26:28] = u16(255)
        boot[28:32] = u32(0)

        boot[40:48] = u64(total_sectors)
        boot[48:56] = u64(4)   # $MFT cluster
        boot[56:64] = u64(8)   # $MFTMirr cluster

        boot[64] = 0xF6        # clusters per MFT record (-10 = 1024 bytes)
        boot[68] = 0x01        # clusters per index record

        boot[72:80] = u64(0x12345678ABCDEF00)
        boot[510:512] = b'\x55\xAA'

        f.seek(0)
        f.write(boot)

    print("Imagem MYSYS didática criada.")
    print("Tamanho:", size_mb, "MB")
    print("Clusters:", total_clusters)
    print("⚠️  Não montável – apenas para estudo.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python mini_mkfs_ntfs.py disco.img tamanho_MB")
        sys.exit(1)

    mkfs_ntfs(sys.argv[1], int(sys.argv[2]))
