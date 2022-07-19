from datetime   import datetime
from numpy      import datetime64, timedelta64
from parsers    import parse_tas, parse_tas_header, tas_rec
from sys        import argv
from time       import sleep
from typing     import List

sc_epoch = datetime64("1899-12-30")

def app(rs: List):

    # print time and sales records

    for r in rs:

        ts      = (sc_epoch + timedelta64(r[tas_rec.timestamp], "us")).astype(datetime)
        price   = r[tas_rec.price] / price_adj
        qty     = r[tas_rec.qty]
        side    = "bid" if r[tas_rec.side] == 0 else "ask"

        print(ts.strftime("%Y-%m-%d %H:%M:%S"), f"{price: 8.2f}", f"{qty:3}", side)


if __name__ == "__main__":

    sc_root     = argv[1]
    contract    = argv[2]
    price_adj   = int(argv[3])
    checkpoint  = int(argv[4])
    fn          = f"{sc_root}/SierraChart/Data/{contract}.scid"
      
    with open(fn, "rb") as fd:

        recs_read = 0
        parse_tas_header(fd)

        while(True):

            rs = parse_tas(fd, checkpoint)

            if len(rs) == 0:

                sleep(0.1)
                
                continue

            checkpoint  =   0
            recs_read   +=  len(rs)

            app(rs)
