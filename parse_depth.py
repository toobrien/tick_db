from enum   import IntEnum
from os     import SEEK_CUR
from struct import calcsize, Struct
from sys    import argv
from time   import time


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


def parse(fn: str, checkpoint: int):

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # file spec:            https://www.sierrachart.com/index.php?page=doc/MarketDepthDataFileFormat.html

    header_fmt  = "4I48c"
    header_len  = calcsize(header_fmt)

    depth_rec_fmt    = "qBBHfII"
    depth_rec_len    = calcsize(depth_rec_fmt)
    depth_rec_unpack = Struct(depth_rec_fmt).unpack_from

    with open(fn, "rb") as fd:

        header_bytes    = fd.read(header_len)
        header          = Struct(header_fmt).unpack_from(header_bytes)

        fd.seek(checkpoint * depth_rec_len, SEEK_CUR)

        num_recs = 0

        while depth_rec_bytes := fd.read(depth_rec_len):

            dr = depth_rec_unpack(depth_rec_bytes)

            num_recs += 1

    print(f"num_recs: {num_recs}")

if __name__ == "__main__":

    sc_root     = argv[1]
    contract    = argv[2]
    date        = argv[3]
    checkpoint  = int(argv[4])

    start = time()

    parse(f"{sc_root}/SierraChart/Data/MarketDepthData/{contract}.{date}.depth", checkpoint)

    print(f"finished: {time() - start:0.1f}s")