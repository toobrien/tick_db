from sys        import argv, path

path.append("../tick_db")

from bisect     import bisect_left
from enum       import IntEnum
from json       import loads
from parsers    import parse_tas, parse_tas_header, tas_rec, transform_tas
from time       import sleep, time
from typing     import List


class r_rot(IntEnum):

    side    = 0
    start   = 1
    length  = 2
    delta   = 3
    volume  = 4


CONFIG          = loads(open("./config.json").read())
SC_ROOT         = CONFIG["SC_ROOT"]
SLEEP_INT       = CONFIG["SLEEP_INT"]

ROTATION_SIDE       = 0
ROTATION_HIGH       = -float('inf')
ROTATION_LOW        = float('inf')
ROTATION_LENGTH     = 0
UP_ROTATION_DELTA   = 0
DN_ROTATION_DELTA   = 0
UP_ROTATION_VOLUME  = 0
DN_ROTATION_VOLUME  = 0


def get_rotations(
    recs:           List,
    min_rotation:   int,
    tick_size:      float
):

    res           = []
    prev_rotation = [ 0, "", 0, 0, 0 ]

    for rec in recs:

        price = rec[tas_rec.price]
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

    start = time()

    fn              = argv[1]
    rotation_ticks  = int(argv[2])
    tick_size       = float(argv[3])
    price_adj       = float(argv[4])
    start_date      = argv[5]
    to_seek         = int(argv[6])
    loop            = int(argv[7])

    rotations = []

    with open(f"{SC_ROOT}/SierraChart/Data/{fn}.scid", "rb") as fd:

        parse_tas_header(fd)

        while True:

            res = parse_tas(fd, to_seek)

            print(f"elapsed (parse): {time() - start:0.2f}")

            transform_tas(res, price_adj)

            print(f"elapsed (transform): {time() - start:0.2f}")

            start = bisect_left(res, start_date)

            rotations = get_rotations(res[start:], rotation_ticks, tick_size)

            print(f"elapsed (rotations): {time() - start:0.2f}")

            for rotation in rotations[-10:]:

                print(rotation)

            if (loop):

                sleep(SLEEP_INT)

                to_seek = 0
            
            else:

                break

    print(f"elapsed (all): {time() - start:0.2f}")
