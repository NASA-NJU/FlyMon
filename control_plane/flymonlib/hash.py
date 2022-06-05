import crcmod



class Hasher:
    """
    Hash Function instance.
    """
    def __init__(self, polynomial, bit_width, init_crc, is_reverse, final_xor):
        self._conf = {
            "polynomial" : polynomial,
            "bit_width"  : bit_width,
            "init_crc"   : init_crc,
            "is_reverse" : is_reverse,
            "final_xor"  : final_xor
        }
        self._func = crcmod.mkCrcFun(((1 << bit_width) | polynomial), initCrc=init_crc, rev=is_reverse)
        pass

    def compute(self, phy_bitw, input):
        """
        calcute the crc code for input.
        """
        return (self._func(input) ^ self._conf["final_xor"]) & int('0'*(32-phy_bitw) + '1'*phy_bitw, base=2)

    @property
    def polynomial(self):
        return self._conf["polynomial"]
    
    @property
    def bit_width(self):
        return self._conf["bit_width"]

    @property
    def init_crc(self):
        return self._conf["init_crc"]

    @property
    def is_reverse(self):
        return self._conf["is_reverse"]

    @property
    def final_xor(self):
        return self._conf["final_xor"]

    def __str__(self) -> str:
        return str(self._conf)


HASHES = [
    # reference: https://crccalc.com/
    Hasher(0x1021,     16,        0xFFFF,   False,      0x0000),
    Hasher(0x8005,     16,        0x0000,   True,       0x0000),
    Hasher(0x1021,     16,        0x1D0F,   False,      0x0000),

    Hasher(0xC867,     16,        0xFFFF,   False,      0x0000),
    Hasher(0x0589,     16,        0x0000,   False,      0x0001),
    Hasher(0x3D65,     16,        0x0000,   True,       0xFFFF),

    Hasher(0x8BB7,     16,        0xFFFF,   False,      0x0000),
    Hasher(0xA097,     16,        0x0000,   True,       0x0000),
    Hasher(0x1021,     16,        0x1D0F,   False,      0xFFFF),

    Hasher(0xC867,     16,        0xFFFF,   False,      0xFFFF),
    Hasher(0x0589,     16,        0x0000,   False,      0xFFFF),
    Hasher(0x3D65,     16,        0xFFFF,   True,       0x0000),

    Hasher(0x1021,     16,        0xFFFF,   False,      0x0000),
    Hasher(0x8005,     16,        0x0000,   True,       0x0000),
    Hasher(0x1021,     16,        0x1D0F,   False,      0x0000),

    Hasher(0xC867,     16,        0xFFFF,   False,      0x0000),
    Hasher(0x0589,     16,        0x0000,   False,      0x0001),
    Hasher(0x3D65,     16,        0x0000,   True,       0xFFFF),

    Hasher(0x8BB7,     16,        0xFFFF,   False,      0x0000),
    Hasher(0xA097,     16,        0x0000,   True,       0x0000),
    Hasher(0x1021,     16,        0x1D0F,   False,      0xFFFF),

    Hasher(0x04C11DB7, 32,    0xFFFFFFFF,   False,      0xFFFFFFFF),
    Hasher(0x1021,     16,        0xFFFF,   False,      0x0000),

    Hasher(0x04C11DB7, 32,    0xFFFFFFFF,   False,      0xFFFFFFFF),
    Hasher(0xC867,     16,        0xFFFF,   False,      0x0000),

    Hasher(0x04C11DB7, 32,    0xFFFFFFFF,   False,      0xFFFFFFFF),
    Hasher(0x0589,     16,        0xFFFF,   False,      0x0000),

    Hasher(0x04C11DB7, 32,    0xFFFFFFFF,   False,      0xFFFFFFFF),
    Hasher(0x3D65,     16,        0xFFFF,   False,      0x0000),

    Hasher(0x04C11DB7, 32,    0xFFFFFFFF,   False,      0xFFFFFFFF),
    Hasher(0xC867,     16,        0x0000,   False,      0x0000),
]
