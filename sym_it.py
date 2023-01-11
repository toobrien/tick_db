from bisect     import bisect_right
from json       import loads
from parsers    import depth_rec, tas_rec, parse_tas, parse_tas_header, parse_depth, parse_depth_header
from time       import time


SC_ROOT = loads(open("./config.json").read())["sc_root"]


class SymIt:


    def __init__(
        self,
        symbol:     str,
        date:       str,
        ts:         int = 0
    ):

        self.symbol     = symbol
        self.date       = date
        
        self.sync       = False
        self.ts         = ts
        self.tas_recs   = []
        self.lob_recs   = []
        self.tas_i      = 0
        self.lob_i      = 0
        self.tas_fd     = open(f"{SC_ROOT}/Data/{symbol}.scid", "rb")
        self.lob_fd     = open(f"{SC_ROOT}/Data/MarketDepthData/{symbol}.{date}.depth", "rb")

        parse_tas_header(self.tas_fd)
        parse_depth_header(self.lob_fd)


    def synchronize(self, update: bool):

        # t0 = time()

        if update:

            # obtain any new records

            self.tas_recs += parse_tas(self.tas_fd, 0)
            self.lob_recs += parse_depth(self.lob_fd, 0)

        self.lob_i = bisect_right(self.lob_recs, self.ts, key = lambda rec: rec[depth_rec.timestamp])
        
        if self.lob_i < len(self.lob_recs):
        
            self.ts = self.lob_recs[self.lob_i][depth_rec.timestamp]
        
        else:

            self.ts = self.lob_recs[-1][depth_rec.timestamp]
        
        self.tas_i = bisect_right(self.tas_recs, self.ts, key = lambda rec: rec[tas_rec.timestamp])

        # print(f"synchronize: {time() - t0: 0.2f}")


    # if you want to re-read the stream from the start, set ts to 0

    def set_ts(self, ts: int, update: bool = False):

        self.ts     = ts
        self.sync   = False

        self.synchronize(update)


    def __iter__(self):

        self.synchronize(update = True)
        
        return self


    def __next__(self):

        tas_i       = self.tas_i
        tas_recs    = self.tas_recs
        lob_i       = self.lob_i
        lob_recs    = self.lob_recs

        if  lob_i < len(lob_recs):
            
            if  tas_i >= len(tas_recs) or \
                lob_recs[lob_i][depth_rec.timestamp] < tas_recs[tas_i][tas_rec.timestamp]:

                res         =   lob_recs[lob_i]
                self.ts     =   res[depth_rec.timestamp]
                self.lob_i  +=  1

            else:

                res         =   tas_recs[tas_i]
                self.ts     =   res[tas_rec.timestamp]
                self.tas_i  +=  1

        else:

            raise StopIteration

        return res



