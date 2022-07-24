from asyncio    import gather, run, sleep
from db         import load_depth, load_tas
from datetime   import datetime
from json       import dumps, loads
from numpy      import datetime64, timedelta64
from os         import walk
from parsers    import depth_rec, parse_depth, parse_depth_header, parse_tas, parse_tas_header, tas_rec
from re         import match
from sys        import argv
from typing     import List


SC_EPOCH    = datetime64("1899-12-30")
CONFIG      = loads(open("./config.json").read())
CONTRACTS   = CONFIG["CONTRACTS"]
SLEEP_INT   = CONFIG["SLEEP_INT"]
SC_ROOT     = CONFIG["SC_ROOT"]


################
# TIME AND SALES
################


def transform_tas(rs: List, price_adj: float):

    for r in rs:

        # truncate microsecond int64 to millisecond datestring

        r[tas_rec.timestamp]    = (SC_EPOCH + timedelta64(r[tas_rec.timestamp], "us")).astype(datetime).strftime("%Y-%m-%d %H:%M:%S.%f")
        r[tas_rec.price]        *= price_adj
        r[tas_rec.side]         = "bid" if r[tas_rec.side] == 0 else "ask"


async def etl_tas_coro(
    con_id:     str,
    checkpoint: int, 
    price_adj:  float,
    loop:       int
) -> int:

    fn      = f"{SC_ROOT}/SierraChart/Data/{con_id}.scid"
    to_seek = checkpoint
    
    with open(fn, "rb") as fd:

        parse_tas_header(fd)

        while(True):

            parsed = parse_tas(fd, to_seek)
            
            transform_tas(parsed, price_adj)
            load_tas(con_id, parsed)
            
            checkpoint  +=  len(parsed)
            to_seek     =   0

            if loop:

                await sleep(SLEEP_INT)
                
            else:

                break

    return ( con_id, checkpoint )


async def etl_tas(loop: int):

    for con_id, dfn in CONTRACTS.items():

        checkpoint  = dfn["checkpoint_tas"]
        price_adj   = dfn["price_adj"]
        tas         = dfn["tas"]
        coros       = []
        
        if tas:

            coros.append(etl_tas_coro(con_id, checkpoint, price_adj, loop))

    results = await gather(coros)

    for res in results:

        con_id      = res[0]
        checkpoint  = res[1] 
        
        CONFIG["contracts"][con_id]["checkpoint_tas"] = checkpoint


##############
# MARKET DEPTH
##############


def transform_depth(rs: List, price_adj: float):

    for r in rs:

        # truncate microsecond int64 to millisecond datestring
        # delete "reserved" value from record

        r[depth_rec.timestamp]  =   (SC_EPOCH + timedelta64(r[depth_rec.timestamp], "us")).astype(datetime).strftime("%Y-%m-%d %H:%M:%S.%f")
        r[depth_rec.price]      *=  price_adj
        del r[-1]


async def etl_depth_coro(
    con_id:     str,
    file:       str,
    checkpoint: int,
    price_adj:  float,
    loop:       int
):

    fn      = f"{SC_ROOT}/SierraChart/Data/MarketDepthData/{file}"
    to_seek = checkpoint
    
    with open(fn, "rb") as fd:

        parse_depth_header(fd)

        while(True):

            parsed = parse_depth(fd, to_seek)
            
            transform_depth(parsed, price_adj)
            load_depth(con_id, parsed)
            
            checkpoint  +=  len(parsed)
            to_seek     =   0

            if loop:

                await sleep(SLEEP_INT)
                
            else:

                break

    return ( con_id, checkpoint )


async def etl_depth(loop: int):

    _, _, files = walk(f"{SC_ROOT}/Data/MarketDepthData")

    for con_id, dfn in CONTRACTS.items():

        price_adj       = dfn["price_adj"]
        depth           = dfn["depth"]
        checkpoint_date = dfn["checkpoint_depth"]["date"]
        checkpoint_rec  = dfn["checkpoint_depth"]["rec"]
        coros           = []

        if depth:

            to_parse = []

            for file in files:

                parts = file.split(".")

                if match(con_id, parts[0]) and parts[1] >= checkpoint_date:

                    to_parse.append(file)

            to_parse = sorted(to_parse)

            for file in to_parse:

                # checkpoint record should only be used on first (earliest) file, and
                # looping should only be used on last (most recent) file

                checkpoint = checkpoint_rec if checkpoint_date in file else 0
                mode       = loop if file == to_parse[-1] else 0

                coros.append(etl_depth_coro(con_id, file, checkpoint, price_adj, mode))

            CONFIG["contracts"][con_id]["checkpoint_depth"]["date"] = to_parse[-1].split(".")[1]

        results = await gather(coros)

        for res in results:

            con_id = res[0]
            rec    = res[1]

            if rec != -1:

                CONFIG["contracts"][con_id]["checkpoint_depth"]["rec"] = rec


async def main():

    loop = int(argv[1])

    a = etl_tas(loop)
    b = etl_depth(loop)

    await gather(a, b)

    with open("./config.json", "w") as fd:

        fd.write(dumps(CONFIG))


run(main())


