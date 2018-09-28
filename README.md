# economist_pay
Contains data on economists from publicly available sources.

There are two distinct sources here. The first is FedsDataCenter.org. It only contains the most recent three fiscal years, and we just pulled the 2015 data, since that is closest in time to the internal data we are using, so could serve as the best comparison. It contains everyone with the occupation "Economist" in that year, for the agencies that report to OPM and were released as part of the FOIA request.

The second source is FederalPay.org. It has a time series of earnings that starts in 2004, but does not allow searches by occupation, so the data was collected by manually entering the names of economists. That work was time consuming, so the data file FederalPay.xlsx is still incomplete. The more targeted search of economists in the Census Bureau, BLS, and BEA is complete, and targets PhD/Research economists in those agencies.
