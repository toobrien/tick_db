from datetime   import datetime
from json       import loads
from numpy      import datetime64, timedelta64
from parsers    import parse_tas, parse_tas_header, transform_tas, tas_rec
from pytz       import timezone
from sys        import argv
from time       import sleep


CONFIG      = loads(open("./config.json").read())
SC_ROOT     = CONFIG["sc_root"] 
SLEEP_INT   = CONFIG["sleep_int"]
SC_EPOCH    = datetime64("1899-12-30")


if __name__=="__main__":

    fn          = argv[1]
    price_adj   = float(argv[2])
    loop        = int(argv[3])
    to_seek     = int(argv[4])

    with open(f"{SC_ROOT}/Data/{fn}.scid", "rb") as fd:

        _ = parse_tas_header(fd)

        while True:

            res = parse_tas(fd, to_seek)

            recs = transform_tas(res, price_adj)

            for r in recs:

                print(
                    (SC_EPOCH + timedelta64(r[tas_rec.timestamp], "us")).astype(datetime).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    f"{r[tas_rec.price]: 10.5f}",
                    f"{r[tas_rec.qty]: 10d}",
                    "bid".rjust(10) if r[tas_rec.side] == 0 else "ask".rjust(10),
                )

            if loop:

                sleep(SLEEP_INT)

                to_seek = 0
            
            else:

                break