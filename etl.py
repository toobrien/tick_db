from asyncio    import gather, run, sleep
from db         import load_tas
from datetime   import datetime
from json       import dumps, loads
from numpy      import datetime64, timedelta64
from parsers    import parse_tas, parse_tas_header, tas_rec
from sys        import argv
from typing     import List


CONFIG      = loads(open("./config.json").read())
CONTRACTS   = CONFIG["CONTRACTS"]
SLEEP_INT   = CONFIG["SLEEP_INT"]
SC_EPOCH    = datetime64("1899-12-30")
SC_ROOT     = CONFIG["SC_ROOT"]


def transform_tas(rs: List, price_adj: float):

    for r in rs:

        # ts    = (SC_EPOCH + timedelta64(r[tas_rec.timestamp], "us")).astype(datetime)
        # price = r[tas_rec.price]
        # qty   = r[tas_rec].qty
        # print(ts.strftime("%Y-%m-%d %H:%M:%S"), f"{price: 8.2f}", f"{qty:3}", side)

        r[tas_rec.timestamp]    = str(r[tas_rec.timestamp])
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
            load_tas(parsed)
            
            checkpoint  +=  len(parsed)
            to_seek     =   0

            if loop:

                await sleep(SLEEP_INT)
                
            else:

                break

    return ( con_id, checkpoint )


async def etl_tas(loop: int):

    for con_id, dfn in CONTRACTS.items():

        checkpoint  = dfn["checkpoint"]
        price_adj   = dfn["price_adj"]
        tas         = dfn["tas"]
        coros       = []
        
        if (tas):

            coros.append(etl_tas_coro(con_id, checkpoint, price_adj, loop))

        results = await gather(coros)

        for res in results:

            con_id      = res[0]
            checkpoint  = res[1] 
            
            CONFIG["contracts"][con_id]["checkpoint"] = checkpoint


async def main():

    loop = int(argv[1])

    await etl_tas(loop)
    # await etl_depth(loop)

    with open("./config.json", "w") as fd:

        fd.write(dumps(CONFIG))


run(main())


