from bisect     import bisect_right
from json       import loads
from parsers    import depth_rec, tas_rec, parse_tas, parse_tas_header, parse_depth, parse_depth_header


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
        self.tas_fd     = None
        self.lob_fd     = None

        with open(f"{SC_ROOT}/Data/{symbol}.scid", "rb") as fd:

            self.tas_fd = fd

            parse_tas_header(self.tas_fd)

        with open(f"{SC_ROOT}/Data/MarketDepthData/{symbol}.{date}.depth", "rb") as fd:

            self.lob_fd = fd

            parse_depth_header(self.lob_fd)


    # if you want to re-read the stream from the start, set ts to 0

    def set_ts(self, ts: int):

        self.ts     = ts
        self.sync   = False


    def __iter__(self):

        self.tas_recs += parse_tas(self.tas_fd, 0)
        self.lob_recs += parse_depth(self.lob_fd, 0)

        if not self.sync:

            self.lob_i  = bisect_right(self.lob_recs, self.ts, lambda rec: rec[depth_rec.timestamp])
            self.ts     = self.lob_recs[self.lob_i][depth_rec.timestamp]
            self.tas_i  = bisect_right(self.tas_recs, self.ts, lambda rec: rec[tas_rec.timestamp])
            self.sync   = True


    def __next__(self):

        tas_i       = self.tas_i
        tas_recs    = self.tas_recs
        lob_i       = self.lob_i
        lob_recs    = self.lob_recs

        if lob_recs[lob_i][depth_rec.timestamp] < tas_recs[tas_i][tas_rec.timestamp] and lob_i < len(lob_recs):

            res     =   lob_recs[lob_i]
            self.ts =   res[depth_rec.timestamp]
            lob_i   +=  1

        elif tas_i < len(tas_recs):

            res     =   tas_recs[tas_i]
            self.ts =   res[tas_rec.timestamp]
            tas_i   +=  1

        else:

            raise StopIteration

        return res



