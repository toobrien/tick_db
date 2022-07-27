This repository contains tools building a database from time and sales as well as market depth records produced by Sierra Chart. Alternately, you can use the parsing module to read these directly from disk and into your program.

### Time and Sales

Sierra chart does not store time and sales records per se, but OHLC values. It stores these "intraday data files" in `/Data`. They have a `.scid` extension. When Sierra Chart is configured to store one trade per bar in these intraday files, they effectively become time and sales records. `parsers.parse_tas` converts these one-trade intraday records into time and sales records with a timestamp, price, quantity, and side (0 = at bid, 1 = at ask) fields.

Read more about the intraday data files here: 

https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

How far back can this data go? Sierra Chart's historical data service provides tick data through 2011 for CME group exchanges. For other exchanges, see: 

https://www.sierrachart.com/index.php?page=doc/SierraChartHistoricalData.php#Included

### Market Depth

Market depth files are stored in `/Data/MarketDepthData`. They have a `.depth` extension. One file is produced per symbol, per day. You must configure Sierra Chart to download market depth for any symbols you are interested in. To do so, follow steps 1-8 and 16-18: 

https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375#StepByStepInstructions

See also: 

https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375#DownloadingOfHistoricalMarketDepthData

Depth records contain commands to modify the state of an order book. For example, adding bids, deleting offers, and so on. Cumulatively applying the commands results in the correct state of the order book, up through the latest record processed. Sierra Chart allows you to download the last 30 days of market depth data. Depth records are parsed by `parsers.parse_depth`.

### Keeping .scid files up-to-date

You can keep `.scid` files up to date simply by connecting to a data feed once per day. Sierra Chart will download any missing records as far back as `Maximum Historical Intraday Days to Download`, provided the symbol you are interested in is open in a chart or DOM.

https://www.sierrachart.com/index.php?page=doc/DataSourceSettings.php#MaximumHistoricalIntradayDaysToDownloadSection

https://www.sierrachart.com/index.php?page=doc/HistoricalIntradayData.html#RetryingDownloadingOfIntradayData

After the download is complete, you can force Sierra Chart to flush new, incoming records to disk using the `Intraday File Flush Time in Milliseconds` setting. By default, they are written every five seconds:

https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html#GeneralInformation

### Configuration

To find this database useful, you will need to solve a few problems:

1. You need to edit `config.json` to include any contracts you are interested in adding to the database. You need to know the symbol name, as it appears in Sierra Chart, and the price multiplier. The latter is found under `Chart` -> `Chart Settings` -> `Real Time Price Multiplier`.

Note: while tick data is available for years, market depth is only available for 30 days. Basically, you have a 30 day window to get the configuration right if you don't want to miss records going forward.

2. You need to keep the data files updated. For `.scid` files, see the section above. For `.depth` files, ???TODO???.

### USAGE

1. Open `config.json` and add any contracts you are interested in loading. See the included example. The checkpoint fields are set automatically, and should be initialized to `0` (or `""` for `checkpoint_depth.date`). The boolean values set whether time and sales, depth, or both will be loaded into the database. Set `price_adj` according to the `Real Time Price Multiplier` value (see discussion in the section above).

2. Set the location of your Sierra Chart installation in `sc_root`.

3. Set the `sleep_int` equal or similar to `Intraday File Flush Time in Milliseconds`.

4. Load data with `python etl.py <loop>`. Where `loop` is 0 (to read and load once, then quite) or 1 (to read/load continuously, as the files are written). Usually 0 is better.


### SCHEMA

```
    <contract_name>_tas
        timestamp   INTEGER
        price       REAL
        qty         INTEGER
        side        INTEGER

    <contract_name>_depth
        timestamp   INTEGER
        command     INTEGER
        flags       INTEGER
        num_orders  INTEGER
        price       REAL
        quantity    INTEGER
```

The timestamps are 64-bit unsigned integers, denoting the number of microseconds since `1899-12-30"`. The prices have been adjusted to match what you would expect to see, but otherwise the records are similar to their original forms, which are described here:

time and sales: https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

market depth: https://www.sierrachart.com/index.php?page=doc/MarketDepthDataFileFormat.html