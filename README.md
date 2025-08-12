# Dummy Trader

This prototype desktop application analyses Indian stocks using simple
technical and fundamental indicators.  Enter a stock symbol (for example
`RELIANCE.NS`) along with your risk appetite and initial investment to get:

* A buy/sell/hold decision based on moving-average crossover and P/E ratio.
* An estimate for when a better entry/exit point may occur.
* A sample portfolio allocation tailored to your risk profile.

The application uses the free Yahoo Finance API and requires an internet
connection.  Run it with:

```bash
python trader_app.py
```

> **Note**: In restricted environments without internet access the program will
report that data is unavailable.
