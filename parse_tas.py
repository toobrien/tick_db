from enum   import IntEnum
from struct import calcsize, Struct
from sys    import argv
from time   import time
from typing import BinaryIO, List


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


HEADER_FMT  = "4cIIHHI36c"
HEADER_LEN  = calcsize(HEADER_FMT)

INTRADAY_REC_FMT    = "q4f4I"
INTRADAY_REC_LEN    = calcsize(INTRADAY_REC_FMT)
INTRADAY_REC_UNPACK = Struct(INTRADAY_REC_FMT).unpack_from


def parse(fd: BinaryIO, checkpoint: int) -> List:

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # file spec:            https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

    tas_recs = []

    '''
    if (checkpoint <= 0):
    
        header_bytes    = fd.read(HEADER_LEN)
        header          = Struct(HEADER_FMT).unpack_from(header_bytes)
    '''

    fd.seek(HEADER_LEN + checkpoint * INTRADAY_REC_LEN)

    while intraday_rec_bytes := fd.read(INTRADAY_REC_LEN):

        ir = INTRADAY_REC_UNPACK(intraday_rec_bytes)

        tas_rec = (
            ir[intraday_rec.timestamp],
            ir[intraday_rec.close],
            ir[intraday_rec.bid_vol] if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol],
            0 if ir[intraday_rec.bid_vol] > 0 else 1
        )

        tas_recs.append(tas_rec)

    print(f"num_recs: {len(tas_recs)}")

    return tas_recs


if __name__ == "__main__":

    sc_root     = argv[1]
    contract    = argv[2]
    checkpoint  = int(argv[3])
    fn          = f"{sc_root}/SierraChart/Data/{contract}.scid"

    start = time()

    with open(fn, "rb") as fd:
    
        parse(fd, checkpoint)

    print(f"finished: {time() - start:0.1f}s")