## Exchange Engine Design Logic
### Data Clearning

* Bloomberg Raw Data
  * Selection for First Month Exchange Rate
    * **Using "SP" (Starting Price) as the exchange rate for the first month.**
    * Exchange rate calculation:
      * Exchange Rate = (Forward Bid Price + Forward Ask Price) / 2