"""Convert an X11 ``xwd`` dump to PNG without ImageMagick/netpbm.

PIL's XWD plugin rejects the 32-bit TrueColor dumps this X server produces, so parse the
100-byte header ourselves.

Usage: python scripts/xwd2png.py <in.xwd> <out.png> [--scale 0.6]
"""
from __future__ import annotations

import struct
import sys

from PIL import Image


def main() -> int:
    src, dst = sys.argv[1], sys.argv[2]
    scale = 1.0
    if "--scale" in sys.argv:
        scale = float(sys.argv[sys.argv.index("--scale") + 1])
    with open(src, "rb") as fh:
        head = fh.read(100)
        fields = struct.unpack(">25I", head[:100])
        # X11WDFileHeader: note there is an `xoffset` but NO `yoffset`, so every field after
        # it sits one slot earlier than a naive reading suggests.
        (header_size, _version, _fmt, _depth, width, height, _xoffset, byte_order,
         _bitmap_unit, _bitmap_bit_order, _bitmap_pad, bpp, bytes_per_line, _vclass,
         rmask, gmask, bmask, _bits_rgb, _colormap_entries, ncolors) = fields[:20]
        fh.seek(header_size + ncolors * 12)
        data = fh.read(bytes_per_line * height)
    if bpp not in (24, 32):
        print("unsupported bits_per_pixel", bpp)
        return 1
    stride = bytes_per_line
    out = bytearray(width * height * 3)
    def shift(mask):
        if mask == 0:
            return 0, 0
        s = (mask & -mask).bit_length() - 1
        return s, mask >> s
    rs, rn = shift(rmask); gs, gn = shift(gmask); bs, bn = shift(bmask)
    for y in range(height):
        row = data[y * stride: (y + 1) * stride]
        o = y * width * 3
        for x in range(width):
            px = int.from_bytes(row[x * (bpp // 8): x * (bpp // 8) + 4],
                                "little" if byte_order == 0 else "big")
            out[o + x * 3 + 0] = ((px & rmask) >> rs) * 255 // max(rn, 1)
            out[o + x * 3 + 1] = ((px & gmask) >> gs) * 255 // max(gn, 1)
            out[o + x * 3 + 2] = ((px & bmask) >> bs) * 255 // max(bn, 1)
    im = Image.frombytes("RGB", (width, height), bytes(out))
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))))
    im.save(dst)
    print("wrote", dst, im.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
