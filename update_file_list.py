from sys import argv


# python update_file_list.py N23 Z23


SYMBOLS = [

    ( "CL{MYY}_FUT_CME",                "FGHJKMNQUVXZ",     True    ),
    ( "RB{MYY}_FUT_CME",                "FGHJKMNQUVXZ",     True    ),
    ( "HO{MYY}_FUT_CME",                "FGHJKMNQUVXZ",     True    ),
    ( "NG{MYY}_FUT_CME",                "FGHJKMNQUVXZ",     True    ),
    ( "ZC{MYY}_FUT_CME",                "HKNUZ",            True    ),
    ( "ZR{MYY}_FUT_CME",                "FHKNUX",           True    ),
    ( "ZS{MYY}_FUT_CME",                "FHNQUX",           True    ),
    ( "ZM{MYY}_FUT_CME",                "FHKNQUVZ",         True    ),
    ( "ZL{MYY}_FUT_CME",                "FHKNQUVZ",         True    ),
    ( "ZW{MYY}_FUT_CME",                "HKNUZ",            True    ),
    ( "KE{MYY}_FUT_CME",                "HKNUZ",            True    ),
    ( "ZO{MYY}_FUT_CME",                "HKNUZ",            True    ),
    ( "HE{MYY}_FUT_CME",                "GJKMNQVZ",         True    ),
    ( "LE{MYY}_FUT_CME",                "GJMQVZ",           True    ),
    ( "GF{MYY}_FUT_CME",                "FHJKQUVX",         True    ),
    ( "GC{MYY}_FUT_CME",                "GJMQZ",            True    ),
    ( "SI{MYY}_FUT_CME",                "HKNUZ",            True    ),
    ( "HG{MYY}_FUT_CME",                "HKNUZ",            True    ),
    ( "VX{MYY}_FUT_CFE",                "FGHJKMNQUVXZ",     True    ),
    ( "ES{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "NQ{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "YM{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "RTY{MYY}_FUT_CME",               "HMUZ",             True    ),
    ( "ZB{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "ZN{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "ZF{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "ZT{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "SR1{MYY}_FUT_CME",               "HMUZ",             True    ),
    ( "SR3{MYY}_FUT_CME",               "HMUZ",             True    ),
    ( "6E{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "6B{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "6J{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "6M{MYY}_FUT_CME",                "HMUZ",             True    ),
    ( "LNE{MYY} {T}{S}.FUT_OPT.NYMEX",  "FGHJKMNQUVXZ",     "1000:12000:50:0",  True    ),
    ( "LO{MYY} {T}{S}.FUT_OPT.NYMEX",   "FGHJKMNQUVXZ",     "3000:10000:50:0",  True    ),
    ( "LO1{MYY} {T}{S}.FUT_OPT.NYMEX",  "FGHJKMNQUVXZ",     "3000:10000:50:0",  True    ),
    ( "LO2{MYY} {T}{S}.FUT_OPT.NYMEX",  "FGHJKMNQUVXZ",     "3000:10000:50:0",  True    ),
    ( "LO3{MYY} {T}{S}.FUT_OPT.NYMEX",  "FGHJKMNQUVXZ",     "3000:10000:50:0",  True    ),
    ( "LO4{MYY} {T}{S}.FUT_OPT.NYMEX",  "FGHJKMNQUVXZ",     "3000:10000:50:0",  True    ),
    ( "OCD{MYY} {T}{S}.FUT_OPT.CBOT",   "FGHJKMNQUVXZ",     "200:900:5:4",      True    ),  # short-dated new crop
    ( "OZC{MYY} {T}{S}.FUT_OPT.CBOT",   "FGHJKMNQUVXZ",     "200:900:5:4",      True    ),  # american
    ( "OSD{MYY} {T}{S}.FUT_OPT.CBOT",   "FGHJKMNQUVXZ",     "700:1800:10:4",    True    ),  # short-dated new crop
    ( "OZS{MYY} {T}{S}.FUT_OPT.CBOT",   "FGHJKMNQUVXZ",     "700:1800:10:4",    True    ),  # american
    ( "OZW{MYY} {T}{S}.FUT_OPT.CBOT",   "FGHJKMNQUVXZ",     "350:1400:5:4",     True    ),
    ( "HE{MYY} {T}{S}.FUT_OPT.CME",     "GJKMNQVZ",         "300:1300:10:4",    True    ),
    ( "LE{MYY} {T}{S}.FUT_OPT.CME",     "GJMQVZ",           "750:2000:10:4",    False   )

]


if __name__ == "__main__":

    start   = ( argv[1][0], argv[1][1:] )
    end     = ( argv[2][0], argv[2][1:] )
    years   = [ str(i) for i in range(int(start[1]), int(end[1]) + 1) ]

    for symbol in SYMBOLS:

        if not symbol[-1]:

            continue

        pattern         = symbol[0]
        months          = symbol[1]
        opt             = "OPT" in pattern

        for year in years:
        
            for month in months:

                myy = month + year

                if  ( year == start[1] and month < start[0]) or \
                    ( year == end[1]  and month > end[0] ):

                    continue

                if not opt:

                    contract_id = pattern.format(MYY = myy)

                    print(contract_id)
                
                else:

                    strike_def  = symbol[2].split(":")
                    lo_strike   = int(strike_def[0])
                    hi_strike   = int(strike_def[1])
                    increment   = int(strike_def[2])
                    fill_width  = int(strike_def[3])

                    for type in [ "C", "P" ]:

                        for i in range(lo_strike, hi_strike + increment, increment):

                            contract_id = pattern.format(MYY = myy, T = type, S = str(i).rjust(fill_width, "0"))

                            print(contract_id)




