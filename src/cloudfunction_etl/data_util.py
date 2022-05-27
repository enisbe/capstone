import requests as req
import json 
import pandas as pd
from datetime import datetime, timedelta
import re
from io import StringIO



class YahooData:
    """
    Retrieves data from Yahoo Finance.
    
    Original code source: https://stackoverflow.com/questions/44225771/scraping-historical-data-from-yahoo-finance-with-python
    Correct headers: https://stackoverflow.com/questions/68259148/getting-404-error-for-certain-stocks-and-pages-on-yahoo-finance-python
    """
    timeout = 2
    crumb_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
    crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
    quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{quote}?period1={dfrom}&period2={dto}&interval=1mo&events=history&crumb={crumb}'


    def __init__(self, symbol, days_back=7):
        """
        symbol: ticker symbol for the asset to be pulled.
        Correct headers: https://stackoverflow.com/questions/68259148/getting-404-error-for-certain-stocks-and-pages-on-yahoo-finance-python
        """
        self.symbol = str(symbol)
        self.session = req.Session()
        self.dt = timedelta(days=days_back)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'DNT': '1', # Do Not Track Request Header 
                        'Connection': 'close'}


    def get_crumb(self):
        """
        Original code source: https://stackoverflow.com/questions/44225771/scraping-historical-data-from-yahoo-finance-with-python
        """
        response = self.session.get(self.crumb_link.format(self.symbol),
                                    headers=self.headers,
                                    timeout=self.timeout)
        response.raise_for_status()
        match = re.search(self.crumble_regex, response.text)
        if not match:
            raise ValueError('Could not get crumb from Yahoo Finance')
        else:
            self.crumb = match.group(1)


    def get_quote(self):
        """
        Original code source: https://stackoverflow.com/questions/44225771/scraping-historical-data-from-yahoo-finance-with-python
        """
        if not hasattr(self, 'crumb') or len(self.session.cookies) == 0:
            self.get_crumb()
        now = datetime.utcnow()
        dateto = int(now.timestamp())
        datefrom = -630961200
#       line in original code: datefrom = int((now - self.dt).timestamp())
        url = self.quote_link.format(quote=self.symbol, dfrom=datefrom, dto=dateto, crumb=self.crumb)
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text), parse_dates=['Date'])


class DataSeries:
    """
    Contains methods and objects to retrieve data from FRED and Yahoo Finance.
    """
    
    
    def __init__(self):
        self.dates = []
        self.values = []
        
        
    def fred_response(self, params):
        """
        Makes requests to the FRED API.
        
        params: dictionary, FRED API parameters.
        """
        params = dict(params)
        fred_request = req.get(url='https://api.stlouisfed.org/fred/series/observations',
                               params=params)
        fred_json = json.loads(fred_request.text)['observations']
        for observation in fred_json:
            self.dates.append(str(observation['date']))
            self.values.append(float(observation['value']))
        self.series = pd.Series(self.values,index=self.dates,name=params['series_name'])
         
            
    def yahoo_response(self, series_id):
        """
        Retrieves data from Yahoo Finance, and performs timestamp adjustments.
        
        series_id: ticker symbol for the asset to be pulled.
        """
        series_id = str(series_id)
        series_dataframe = YahooData(series_id).get_quote()[::-1]
        series_dataframe.reset_index(inplace=True)
        series_dataframe.drop('index', axis=1, inplace=True)
        most_recent_day = datetime.strptime(str(series_dataframe['Date'][0])[:10],
                                            '%Y-%m-%d').day
        if most_recent_day != 1:
            series_dataframe = series_dataframe[1:]
            series_dataframe.reset_index(inplace=True)
            series_dataframe.drop('index', axis=1, inplace=True)
        self.dates.extend([str(series_dataframe['Date'][index])[:10]
            for index in range(0, len(series_dataframe))])
        self.values.extend([float(series_dataframe['Adj Close'][index])
            for index in range(0, len(series_dataframe))])