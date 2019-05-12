This program produces an animated plot to show the evolution of the U.S. Treasury yeild curve. 
The program retrieves some 30 years of treasury note and bond yield data from the 
U.S. Treasury web site, beginning with the date 1990-01-02.

This program obtains yield data from the Treasury site using the Python
web scraping module "Beautiful Soup." The BS module requests the contents
of the information in Web_http = 'http://data.treasury.gov/Feed.svc/DailyTreasuryYieldCurveRateData({X})',
where x is a number from 1 to the number of sets of daily yield data. There are over 7350 url daily 
listings of treasury yields, extending back to the first on 1990-01-02, through to the present. 

The U.S. Treasury keeps its yield data in the following html format (Note the index x in this example is 7258,
corresponding to the data of 02-Jan-2019):

<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<entry xml:base="http://data.treasury.gov/Feed.svc/" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" 
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://www.w3.org/2005/Atom">
  <id>http://data.treasury.gov/Feed.svc/DailyTreasuryYieldCurveRateData(7258)</id>
  <title type="text"></title>
  <updated>2019-05-09T07:27:14Z</updated>
  <author>
    <name />
  </author>
  <link rel="edit" title="DailyTreasuryYieldCurveRateDatum" href="DailyTreasuryYieldCurveRateData(7258)" />
  <category term="TreasuryDataWarehouseModel.DailyTreasuryYieldCurveRateDatum" scheme=
      "http://schemas.microsoft.com/ado/2007/08/dataservices/scheme" />
  <content type="application/xml">
    <m:properties>
      <d:Id m:type="Edm.Int32">7258</d:Id>
      <d:NEW_DATE m:type="Edm.DateTime">2019-01-02T00:00:00</d:NEW_DATE>
      <d:BC_1MONTH m:type="Edm.Double">2.4</d:BC_1MONTH>
      <d:BC_2MONTH m:type="Edm.Double">2.4</d:BC_2MONTH>
      <d:BC_3MONTH m:type="Edm.Double">2.42</d:BC_3MONTH>
      <d:BC_6MONTH m:type="Edm.Double">2.51</d:BC_6MONTH>
      <d:BC_1YEAR m:type="Edm.Double">2.6</d:BC_1YEAR>
      <d:BC_2YEAR m:type="Edm.Double">2.5</d:BC_2YEAR>
      <d:BC_3YEAR m:type="Edm.Double">2.47</d:BC_3YEAR>
      <d:BC_5YEAR m:type="Edm.Double">2.49</d:BC_5YEAR>
      <d:BC_7YEAR m:type="Edm.Double">2.56</d:BC_7YEAR>
      <d:BC_10YEAR m:type="Edm.Double">2.66</d:BC_10YEAR>
      <d:BC_20YEAR m:type="Edm.Double">2.83</d:BC_20YEAR>
      <d:BC_30YEAR m:type="Edm.Double">2.97</d:BC_30YEAR>
      <d:BC_30YEARDISPLAY m:type="Edm.Double">2.97</d:BC_30YEARDISPLAY>
    </m:properties>
  </content>
</entry>

This raw text data consists of 13 fields, the first being a date, and the remaining
12 being interest rates on treasuries with maturities starting at 1 month, 
and ending in 30 years. Unfortunately, the url contains only the index number,
not the date. So the url must be called by its index number.  

The Get_New_Daily_Yields function uses Beautiful Soup to parse and extract data from
the url referenced page. This data includes the date, the interest rates
and corresponding maturities. It then creates a Pandas dataframe to report
out the data. Note that in the Treasury data, the next date does not always follow
the next index number; accordingly, the data obtained must be sorted into date order,
which Pandas does easily.

The Get_New_Daily_Yields is a slow process, and retrieving all 30 years takes some time.
Therefore, the data obtained from Treasury is stored locally on disk in a "Data" directory,
in a csv file named "Treasury_Yields." This file is read to a Pandas dataframe by way of the 
Get_Yield_DataFrame function.

For updating the existing local file with new Treasury data, the next
index number is obtained from the length of the existing data. 
There are a few (i.e., 3) data points missing or deleted in the 30 years of data, 
so that the length and the index number do not correspond exactly. Accordingly, 
an error correction factor is added to the length in order to obtain the next index number.

The user calls the YieldCurve procedure, entering the desired begin date and frame rate 
per second for the animation. The date must be entered in 'yyyy-mm-dd' format. YieldCurve 
will retrieve treasury data from the local csv file. It will do an online check of the Treasury
site for new yield data, combine the new data with the old, and save the update. It will  
then call the Animate_Yield_Curve function to produce the animated plot of the yield curve.

