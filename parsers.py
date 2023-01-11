from enum       import IntEnum
from numpy      import datetime64
from os         import fstat
from struct     import calcsize, Struct
from sys        import argv
from time       import time
from typing     import BinaryIO, List


SC_EPOCH = datetime64("1899-12-30")


# TIME AND SALES
# NOTE: sc must be configured to store tick data: 
# https://www.sierrachart.com/index.php?page=doc/TickbyTickDataConfiguration.php


class intraday_rec(IntEnum):

    timestamp   = 0
    open        = 1
    high        = 2
    low         = 3
    close       = 4
    num_trades  = 5
    total_vol   = 6
    bid_vol     = 7
    ask_vol     = 8


class tas_rec(IntEnum):

    timestamp   = 0
    price       = 1
    qty         = 2
    side        = 3


# format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
# file spec:            https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

INTRADAY_HEADER_FMT  = "4cIIHHI36c"
INTRADAY_HEADER_LEN  = calcsize(INTRADAY_HEADER_FMT)

INTRADAY_REC_FMT    = "q4f4I"
INTRADAY_REC_LEN    = calcsize(INTRADAY_REC_FMT)
INTRADAY_REC_UNPACK = Struct(INTRADAY_REC_FMT).unpack_from


def parse_tas_header(fd: BinaryIO)->tuple:
    
    header_bytes    = fd.read(INTRADAY_HEADER_LEN)
    header          = Struct(INTRADAY_HEADER_FMT).unpack_from(header_bytes)

    return header


def parse_tas(fd: BinaryIO, checkpoint: int) -> List:

    fstat(fd.fileno())

    tas_recs = []

    if checkpoint:
    
        fd.seek(INTRADAY_HEADER_LEN + checkpoint * INTRADAY_REC_LEN)

    while intraday_rec_bytes := fd.read(INTRADAY_REC_LEN):

        ir = INTRADAY_REC_UNPACK(intraday_rec_bytes)

        tas_rec = (
            ir[intraday_rec.timestamp],
            ir[intraday_rec.close],
            ir[intraday_rec.bid_vol] if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol],
            0 if ir[intraday_rec.bid_vol] > 0 else 1
        )

        tas_recs.append(tas_rec)

    return tas_recs


def transform_tas(rs: List, price_adj: float):

    # - truncate microsecond int64 to millisecond datestring (optional -- change schema to TEXT type)
    # - adjust price using "real-time price multiplier"

    return [
        (
            #(SC_EPOCH + timedelta64(r[tas_rec.timestamp], "us")).astype(datetime).strftime("%Y-%m-%d %H:%M:%S.%f"),
            r[tas_rec.timestamp],
            r[tas_rec.price] * price_adj,
            r[tas_rec.qty],
            r[tas_rec.side]
        )
        for r in rs
    ]


# MARKET DEPTH
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


DEPTH_HEADER_FMT  = "4I48c"
DEPTH_HEADER_LEN  = calcsize(DEPTH_HEADER_FMT)

DEPTH_REC_FMT    = "qBBHfII"
DEPTH_REC_LEN    = calcsize(DEPTH_REC_FMT)
DEPTH_REC_UNPACK = Struct(DEPTH_REC_FMT).unpack_from


def parse_depth_header(fd: BinaryIO)->tuple:
    
    header_bytes    = fd.read(DEPTH_HEADER_LEN)
    header          = Struct(DEPTH_HEADER_FMT).unpack_from(header_bytes)

    return header


def parse_depth(fd: BinaryIO, checkpoint: int) -> List:

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # file spec:            https://www.sierrachart.com/index.php?page=doc/MarketDepthDataFileFormat.html

    '''
    if !checkpoint:
    
        header_bytes    = fd.read(HEADER_LEN)
        header          = Struct(HEADER_FMT).unpack_from(header_bytes)
    '''

    fstat(fd.fileno())

    if checkpoint:
    
        fd.seek(DEPTH_HEADER_LEN + checkpoint * DEPTH_REC_LEN)

    depth_recs = []

    while depth_rec_bytes := fd.read(DEPTH_REC_LEN):

        dr = DEPTH_REC_UNPACK(depth_rec_bytes)

        depth_recs.append(dr)

    return depth_recs


def transform_depth(rs: List, price_adj: float):

    # - truncate microsecond int64 to millisecond datestring (optional -- change schema to TEXT type)
    # - adjust price using "real-time price multiplier"
    # - delete "reserved" value from record

    return [
        (
            #(SC_EPOCH + timedelta64(r[depth_rec.timestamp], "us")).astype(datetime).strftime("%Y-%m-%d %H:%M:%S.%f"),
            r[depth_rec.timestamp],
            r[depth_rec.command],
            r[depth_rec.flags],
            r[depth_rec.num_orders],
            r[depth_rec.price] * price_adj,
            r[depth_rec.quantity]
        )
        for r in rs
    ]


if __name__ == "__main__":

    # benchmark program

    start = time()

    mode = argv[1]

    if mode == "tas":

        sc_root     = argv[2]
        contract    = argv[3]
        checkpoint  = int(argv[4])
        fn          = f"{sc_root}/Data/{contract}.scid"

        with open(fn, "rb") as fd:
        
            parse_tas_header(fd)
            rs = parse_tas(fd, checkpoint)

            print(f"num_recs: {len(rs)}")


    elif mode == "depth":

        sc_root     = argv[2]
        contract    = argv[3]
        date        = argv[4]
        checkpoint  = int(argv[5])
        fn          = f"{sc_root}/Data/MarketDepthData/{contract}.{date}.depth"

        with open(fn, "rb") as fd:

            parse_depth_header(fd)
            rs = parse_depth(fd, checkpoint)

            print(f"num_recs: {len(rs)}")

    print(f"finished: {time() - start:0.1f}s")