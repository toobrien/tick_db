from asyncio    import gather, run, sleep
from db         import DB_CON, load_depth, load_tas
from json       import dumps, loads
from os         import walk
from parsers    import parse_depth, parse_depth_header, parse_tas, parse_tas_header, transform_tas, transform_depth
from re         import match
from sys        import argv
from time       import time


CONFIG      = loads(open("./config.json").read())
CONTRACTS   = CONFIG["contracts"]
SLEEP_INT   = CONFIG["sleep_int"]
SC_ROOT     = CONFIG["sc_root"]


################
# TIME AND SALES
################


async def etl_tas_coro(
    con_id:     str,
    checkpoint: int, 
    price_adj:  float,
    loop:       int
) -> int:

    fn      = f"{SC_ROOT}/Data/{con_id}.scid"
    to_seek = checkpoint
    
    with open(fn, "rb") as fd:

        parse_tas_header(fd)

        while(True):

            parsed = parse_tas(fd, to_seek)            
            parsed = transform_tas(parsed, price_adj)

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

    results = await gather(*coros)

    for res in results:

        con_id      = res[0]
        checkpoint  = res[1] 
        
        CONFIG["contracts"][con_id]["checkpoint_tas"] = checkpoint


##############
# MARKET DEPTH
##############


async def etl_depth_coro(
    con_id:     str,
    file:       str,
    checkpoint: int,
    price_adj:  float,
    loop:       int
):

    fn      = f"{SC_ROOT}/Data/MarketDepthData/{file}"
    to_seek = checkpoint
    
    with open(fn, "rb") as fd:

        parse_depth_header(fd)

        while(True):

            parsed = parse_depth(fd, to_seek)
            parsed = transform_depth(parsed, price_adj)

            load_depth(con_id, parsed)
            
            checkpoint  +=  len(parsed)
            to_seek     =   0

            if loop:

                await sleep(SLEEP_INT)
                
            else:

                break

    return ( file, checkpoint )


async def etl_depth(loop: int):

    _, _, files = next(walk(f"{SC_ROOT}/Data/MarketDepthData"))

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

        results = await gather(*coros)

        CONFIG["contracts"][con_id]["checkpoint_depth"]["rec"] = results[-1][1]


async def main():

    start = time()

    loop = int(argv[1])

    a = etl_tas(loop)
    b = etl_depth(loop)

    await gather(a, b)

    with open("./config.json", "w") as fd:

        fd.write(dumps(CONFIG, indent = 2))

    print(f"elapsed: {time() - start}")

    DB_CON.commit()
    DB_CON.close()

run(main())