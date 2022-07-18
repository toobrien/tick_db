This repository contains tools for parsing time and sales records as well as market depth records from Sierra Chart.

### Time and Sales

Sierra chart does not store time and sales records per se, but OHLC values. It stores these "intraday data files" in `/Data`. They have a `.scid` extension. When Sierra Chart is configured to store one trade per bar in these intraday files, they effectively become time and sales records. `parse_tas.py` converts these one-trade intraday records into time and sales records with a timestamp, price, quantity, and side (0 = at bid, 1 = at ask) fields.

Read more about the intraday data files here: 

https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

How far back can this data go? Sierra Chart's historical data service provides tick data through 2011 for CME group exchanges. For other exchanges, see: 

https://www.sierrachart.com/index.php?page=doc/SierraChartHistoricalData.php#Included

### Market Depth

Market depth files are stored in `/Data/MarketDepthData`. They have a `.depth` extension. One file is produced per symbol, per day. You must configure Sierra Chart to download market depth for any symbols you are interested in. To do so, follow steps 1-8 and 16-18: 

https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375#StepByStepInstructions

See also: 

https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375#DownloadingOfHistoricalMarketDepthData

Depth records contain commands to modify the state of an order book. For example, adding bids, deleting offers, and so on. Cumulatively applying the commands results in the correct state of the order book, up through the latest record processed. Sierra Chart allows you to download the last 30 days of market depth data.