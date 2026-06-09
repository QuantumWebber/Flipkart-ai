import pandas as pd
import numpy as np
import datetime
import logging
from prophet import Prophet


#avoid warnings 
logging.getLogger('prophet').setLevel(logging.ERROR)
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

def clean_price(price_str: str) -> float:
    if not price_str or price_str == "N/A":
        return 399.0  
    clean = price_str.replace('₹', '').replace(',', '').strip()
    try:
        return float(clean)
    except ValueError:
        return 399.0

def generate_historical_prices(current_price: float, days: int = 180) -> pd.DataFrame:
    """
    Simulate historical price data for the past 180 days with realistic patterns:
    """
    np.random.seed(42)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days-1)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    
    base_prices = np.linspace(current_price * 1.15, current_price, len(date_range))
    
    
    noise = np.random.normal(0, current_price * 0.02, len(date_range))
    prices = base_prices + noise
    
    
    for i, date in enumerate(date_range):
       
        if date.weekday() in [5, 6]:
            prices[i] = prices[i] * 0.96
        
       
        if 45 <= i <= 52:
            prices[i] = prices[i] * 0.75
            
       
        if 125 <= i <= 130:
            prices[i] = prices[i] * 0.82
            
    #
    prices[-1] = current_price
    
    df = pd.DataFrame({
        'ds': date_range,
        'y': np.round(prices, 2)
    })
    return df

def calculate_technical_indicators(prices: np.ndarray) -> dict:
    """
    Share market algorithms (Support, Resistance, RSI) product prices par apply karna
    """
    
    support = np.percentile(prices, 10)
    resistance = np.percentile(prices, 90)
    
   
    sma_7 = pd.Series(prices).rolling(window=7, min_periods=1).mean().iloc[-1]
    
    
    deltas = np.diff(prices)
    seed = deltas[:14]
    up = seed[seed >= 0].sum() / 14
    down = -seed[seed < 0].sum() / 14
    
    for i in range(14, len(prices)-1):
        delta = deltas[i]
        if delta > 0:
            upval, downval = delta, 0.
        else:
            upval, downval = 0., -delta
        up = (up * 13 + upval) / 14
        down = (down * 13 + downval) / 14
        
    rs = up / (down if down != 0 else 1e-5)
    rsi_score = round(100. - 100. / (1. + rs), 2)
    
    
    if rsi_score < 30:
        signal = " STRONG BUY (Heavy Discount - Highly Undervalued)"
    elif rsi_score > 70:
        signal = " OVERPRICED (Wait for Price Drop)"
    else:
        signal = " FAIR VALUE (Stable Buy)"
        
    return {
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "sma_7": round(sma_7, 2),
        "rsi": rsi_score,
        "signal": signal
    }

def forecast_product_price(current_price_str: str, forecast_days: int = 14) -> tuple:
    current_price = clean_price(current_price_str)
    df_history = generate_historical_prices(current_price)
    
    # all indicators dictionary
    indicators = calculate_technical_indicators(df_history['y'].values)
    
    # Prophet fit
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95
    )
    model.fit(df_history)
    
    future = model.make_future_dataframe(periods=forecast_days, freq='D')
    forecast = model.predict(future)
    
    df_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)

    """  ds: Future Date (Aane waali tareekh).

yhat: Predicted Price (AI ke mutabik us din kya price hoga).

yhat_lower: Minimum Price (Price zyada se zyada kitna gir sakta hai).

yhat_upper: Maximum Price (Price zyada se zyada kitna badh sakta hai). """
    
    # Meta Metrics calculation
    max_hist = df_history['y'].max()
    min_hist = df_history['y'].min()
    discount_from_peak = round(((max_hist - current_price) / max_hist) * 100, 2)
    
    indicators["max_price"] = max_hist
    indicators["min_price"] = min_hist
    indicators["discount_from_peak"] = discount_from_peak
    
    return df_history, df_forecast, indicators