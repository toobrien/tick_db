from enum   import IntEnum
from struct import calcsize, Struct
from sys    import argv
from time   import time
from typing import BinaryIO, List


# NOTE: sc must be configured to record market depth data:
# https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375#DownloadingOfHistoricalMarketDepthData

# NOTE: sierra chart provides 30 days of historical market data: https://www.sierrachart.com/SupportBoard.php?PostID=279457#P279457


class depth_rec(IntEnum):

    timestamp   = 0
    command     = 1
    flags       = 2
    num_orders  = 3
    price       = 4
    quantity    = 5
    reserved    = 6


class depth_cmd(IntEnum):

    none        = 0
    clear_book  = 1
    add_bid_lvl = 2
    add_ask_lvl = 3
    mod_bid_lvl = 4
    mod_ask_lvl = 5
    del_bid_lvl = 6
    del_ask_lvl = 7


HEADER_FMT  = "4I48c"
HEADER_LEN  = calcsize(HEADER_FMT)

DEPTH_REC_FMT    = "qBBHfII"
DEPTH_REC_LEN    = calcsize(DEPTH_REC_FMT)
DEPTH_REC_UNPACK = Struct(DEPTH_REC_FMT).unpack_from


def parse(fd: BinaryIO, checkpoint: int) -> List:

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # file spec:            https://www.sierrachart.com/index.php?page=doc/MarketDepthDataFileFormat.html


    '''
    if (checkpoint <= 0):
    
        header_bytes    = fd.read(HEADER_LEN)
        header          = Struct(HEADER_FMT).unpack_from(header_bytes)
    '''

    fd.seek(HEADER_LEN + checkpoint * DEPTH_REC_LEN)

    depth_recs = []

    while depth_rec_bytes := fd.read(DEPTH_REC_LEN):

        dr = DEPTH_REC_UNPACK(depth_rec_bytes)

        depth_recs.append(dr)

    print(f"num_recs: {len(depth_recs)}")

if __name__ == "__main__":

    sc_root     = argv[1]
    contract    = argv[2]
    date        = argv[3]
    checkpoint  = int(argv[4])
    fn          = f"{sc_root}/SierraChart/Data/MarketDepthData/{contract}.{date}.depth"

    start = time()
    
    with open(fn, "rb") as fd:
        
        parse(fd, checkpoint)

    print(f"finished: {time() - start:0.1f}s")