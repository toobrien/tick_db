from struct import calcsize, Struct
from sys    import argv
from time   import time

def parse(fn: str):

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # struct spec:          https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

    header_fmt      = "4cIIHHI36c"
    header_len      = calcsize(header_fmt)

    ir_fmt      = "q4f4I"
    ir_len      = calcsize(ir_fmt)
    ir_unpack   = Struct(ir_fmt).unpack_from

    with open(fn, "rb") as fd:

        header_rec  = fd.read(header_len)
        header      = Struct(header_fmt).unpack_from(header_rec)

        pass

        while(True):

            ir_rec  = fd.read(ir_len)

            if not ir_rec:

                break

            ir      = ir_unpack(ir_rec)

            pass


if __name__ == "__main__":

    contract = argv[1]

    start = time()

    parse(f"/Volumes/[C] Windows 10/SierraChart/Data/{contract}.scid")

    print(f"finished: {time() - start:0.1f}s")