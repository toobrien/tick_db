import plotly.graph_objects as go

from bisect     import bisect_left
from enum       import IntEnum
from json       import loads
from numpy      import datetime64, timedelta64
from parsers    import parse_tas, parse_tas_header, tas_rec
from sys        import argv
from time       import sleep, time
from typing     import List


class r_rot(IntEnum):

    side    = 0
    start   = 1
    length  = 2
    delta   = 3
    volume  = 4


CONFIG          = loads(open("./config.json").read())
SC_ROOT         = CONFIG["sc_root"]
SLEEP_INT       = CONFIG["sleep_int"]

ROTATION_SIDE       = 0
ROTATION_HIGH       = -float('inf')
ROTATION_LOW        = float('inf')
ROTATION_LENGTH     = 0
UP_ROTATION_DELTA   = 0
DN_ROTATION_DELTA   = 0
UP_ROTATION_VOLUME  = 0
DN_ROTATION_VOLUME  = 0


def to_sc_ts(ts: str):

    return ts + (datetime64("1899-12-30", unit = "us"))


def get_rotations(
    recs:           List,
    price_adj:      float,
    min_rotation:   int,
    tick_size:      float
):

    global ROTATION_SIDE
    global ROTATION_HIGH
    global ROTATION_LOW
    global ROTATION_LENGTH
    global UP_ROTATION_DELTA
    global DN_ROTATION_DELTA
    global UP_ROTATION_VOLUME
    global DN_ROTATION_VOLUME

    res           = []
    prev_rotation = [ 0, "", 0, 0, 0 ]

    for rec in recs:

        price = rec[tas_rec.price] * price_adj
        qty   = rec[tas_rec.qty]
        side  = rec[tas_rec.side]

        prev_rotation[r_rot.side]   = "up" if ROTATION_SIDE == 1 else "dn"
        prev_rotation[r_rot.start]  = ROTATION_LOW if ROTATION_SIDE == 1 else ROTATION_HIGH
        prev_rotation[r_rot.length] = ROTATION_LENGTH
        prev_rotation[r_rot.delta]  = UP_ROTATION_DELTA if ROTATION_SIDE == 1 else DN_ROTATION_DELTA
        prev_rotation[r_rot.volume] = UP_ROTATION_VOLUME if ROTATION_SIDE == 1 else DN_ROTATION_VOLUME

        if (price > ROTATION_HIGH):

            ROTATION_HIGH       = price
            DN_ROTATION_DELTA   = 0
            DN_ROTATION_VOLUME  = 0

        if (price < ROTATION_LOW):

            ROTATION_LOW        = price
            UP_ROTATION_DELTA   = 0
            UP_ROTATION_VOLUME  = 0

        signed_volume = -qty if side == 0 else qty
        
        UP_ROTATION_DELTA   += signed_volume
        DN_ROTATION_DELTA   += signed_volume
        UP_ROTATION_VOLUME  += qty
        DN_ROTATION_VOLUME  += qty

        from_rotation_high  = (ROTATION_HIGH - price) / tick_size
        from_rotation_low   = (price - ROTATION_LOW) / tick_size

        if (from_rotation_high >= min_rotation):

            # in down rotation

            if (ROTATION_SIDE > -1):

                # from up rotation

                res.append(
                    (
                        prev_rotation[r_rot.side],
                        prev_rotation[r_rot.start],
                        prev_rotation[r_rot.length],
                        prev_rotation[r_rot.delta],
                        prev_rotation[r_rot.volume]
                    )
                )

                ROTATION_SIDE   = -1
                ROTATION_LOW    = price
                ROTATION_LENGTH = from_rotation_high

                continue

            else:

                # continuing down rotation

                ROTATION_LENGTH = max(from_rotation_high, ROTATION_LENGTH)

        if (from_rotation_low >= min_rotation):

            # in up rotation

            if (ROTATION_SIDE < 1):

                # from down rotation

                res.append(
                    (
                        prev_rotation[r_rot.side],
                        prev_rotation[r_rot.start],
                        prev_rotation[r_rot.length],
                        prev_rotation[r_rot.delta],
                        prev_rotation[r_rot.volume]
                    )
                )

                ROTATION_SIDE   = 1
                ROTATION_HIGH   = price
                ROTATION_LENGTH = from_rotation_low

            else:

                # continuing up rotation

                ROTATION_LENGTH = max(from_rotation_low, ROTATION_LENGTH)

    return res


if __name__ == "__main__":

    t0 = time()

    fn              = argv[1]
    rotation_ticks  = int(argv[2])
    tick_size       = float(argv[3])
    price_adj       = float(argv[4])
    start_date      = argv[5]
    to_seek         = int(argv[6])
    loop            = int(argv[7])

    rotations = []

    adj_date = to_sc_ts(start_date) if start_date != "-" else None

    with open(f"{SC_ROOT}/SierraChart/Data/{fn}.scid", "rb") as fd:

        parse_tas_header(fd)

        while True:

            res = parse_tas(fd, to_seek)

            print(f"elapsed (parse): {time() - t0:0.2f}")

            start = bisect_left(res, adj_date, key = lambda r: r[tas_rec.timestamp]) if start_date != "-" else 0

            rotations.extend(get_rotations(res[start:], price_adj, rotation_ticks, tick_size))

            print(f"elapsed (rotations): {time() - t0:0.2f}")

            if loop:

                sleep(SLEEP_INT)

                to_seek = 0
            
            else:

                break
    
    # display summaries

    lengths = sorted(
        [ 
            r[r_rot.length] for r in rotations
            if r[r_rot.length] > 0 
        ]
    )

    fig = go.Figure(
        go.Histogram(
            x = lengths,
            nbinsx = int(max(lengths))# - rotation_ticks)  # 1 bin per tick
        )
    )

    fig.show()



    print("50%: ", f"{lengths[int(len(lengths) * 0.5)]}")
    print("70%: ", f"{lengths[int(len(lengths) * 0.75)]}")
    print("95%: ", f"{lengths[int(len(lengths) * 0.95)]}")

    print("\n")

    print(f"len(res): {len(res)}")
    print(f"started from: {start}")
    print(f"len(rotations): {len(rotations)}")
    print(f"elapsed (all): {time() - t0:0.2f}")
