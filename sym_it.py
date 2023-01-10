from bisect     import bisect_right
from json       import loads
from parsers    import depth_rec, tas_rec, parse_tas, parse_tas_header, parse_depth, parse_depth_header
from time       import time


SC_ROOT     = loads(open("./config.json").read())["sc_root"]


class SymIt:


    def __init__(
        self,
        symbol:     str,
        date:       str,
    ):

        self.symbol     = symbol
        self.date       = date
        
        self.sync       = False
        self.ts         = 0
        self.tas_recs   = []
        self.lob_recs   = []
        self.tas_i      = 0
        self.lob_i      = 0
        self.tas_fd     = open(f"{SC_ROOT}/Data/{symbol}.scid", "rb")
        self.lob_fd     = open(f"{SC_ROOT}/Data/MarketDepthData/{symbol}.{date}.depth", "rb")

        parse_tas_header(self.tas_fd)
        parse_depth_header(self.lob_fd)


    # if you want to re-read the stream from the start, set ts to 0

    def set_ts(self, ts: int):

        self.ts     = ts
        self.sync   = False


    def __iter__(self):

        # obtain any new reacord before each iteration

        # t0 = time()

        self.tas_recs += parse_tas(self.tas_fd, 0)
        self.lob_recs += parse_depth(self.lob_fd, 0)

        # print(f"read {len(self.tas_recs)} tas and {len(self.lob_recs)} lob in {time() - t0: 0.2f}")

        if not self.sync:

            self.lob_i  = bisect_right(self.lob_recs, self.ts, key = lambda rec: rec[depth_rec.timestamp])
            self.ts     = self.lob_recs[self.lob_i][depth_rec.timestamp]
            self.tas_i  = bisect_right(self.tas_recs, self.ts, key = lambda rec: rec[tas_rec.timestamp])
            self.sync   = True
        
        return self


    def __next__(self):

        tas_i       = self.tas_i
        tas_recs    = self.tas_recs
        lob_i       = self.lob_i
        lob_recs    = self.lob_recs

        if lob_i < len(lob_recs) and lob_recs[lob_i][depth_rec.timestamp] < tas_recs[tas_i][tas_rec.timestamp]:

            res         =   lob_recs[lob_i]
            self.ts     =   res[depth_rec.timestamp]
            self.lob_i  +=  1

        elif tas_i < len(tas_recs):

            res         =   tas_recs[tas_i]
            self.ts     =   res[tas_rec.timestamp]
            self.tas_i  +=  1

        else:

            raise StopIteration

        return res



