from enum   import IntEnum
from os     import SEEK_CUR
from struct import calcsize, Struct
from sys    import argv
from time   import time


# NOTE: sc must be configured to store tick data: 
# https://www.sierrachart.com/index.php?page=doc/TickbyTickDataConfiguration.php


class intraday_rec(IntEnum):

    timestamp   = 0
    open        = 1
    high        = 2
    low         = 3
    close       = 4
    num_trades  = 5
    bid_vol     = 6
    ask_vol     = 7


class tas_rec(IntEnum):

    timestamp   = 0
    price       = 1
    qty         = 2
    side        = 3


def parse(fn: str, checkpoint: int):

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # file spec:            https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

    header_fmt  = "4cIIHHI36c"
    header_len  = calcsize(header_fmt)

    intraday_rec_fmt    = "q4f4I"
    intraday_rec_len    = calcsize(intraday_rec_fmt)
    intraday_rec_unpack = Struct(intraday_rec_fmt).unpack_from

    tas_recs = []

    with open(fn, "rb") as fd:

        header_bytes    = fd.read(header_len)
        header          = Struct(header_fmt).unpack_from(header_bytes)

        fd.seek(checkpoint * intraday_rec_len, SEEK_CUR)

        while intraday_rec_bytes := fd.read(intraday_rec_len):

            ir = intraday_rec_unpack(intraday_rec_bytes)

            tas_rec = (
                ir[intraday_rec.timestamp],
                ir[intraday_rec.close],
                ir[intraday_rec.bid_vol] if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol],
                0 if ir[intraday_rec.bid_vol] > 0 else 1
            )

            tas_recs.append(tas_rec)

    print(f"num_recs: {len(tas_recs)}")

if __name__ == "__main__":

    sc_root     = argv[1]
    contract    = argv[2]
    checkpoint  = int(argv[3])

    start = time()

    parse(f"{sc_root}/SierraChart/Data/{contract}.scid", checkpoint)

    print(f"finished: {time() - start:0.1f}s")