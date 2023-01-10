from parsers    import depth_rec, tas_rec
from sym_it     import SymIt
from sys        import argv
from time       import time

def process(it):

    tas_recs    = 0
    depth_recs  = 0

    t1 = time()

    for rec in it:

        if len(rec) == len(tas_rec):

            # process tas rec

            print(f"tas: {rec}")

            tas_recs += 1

        else:

            # process depth rec

            print(f"lob: {rec}")

            depth_recs += 1

    print(f"lob_recs, tas_recs: {depth_recs} , {tas_recs} ({time() - t1: 0.2f}s)")


if __name__ == "__main__":

    sym         = argv[1]
    date        = argv[2]

    it = SymIt(sym, date)

    process(it) # process records

    '''
    process(it) # nothing happens unless new market data; iterator at finish
    
    it.set_ts(0)

    process(it) # stream reprocessed
    '''
