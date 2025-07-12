import yfinance as yf
import datetime as dt
from OptionPricingDash import black_scholes
import pandas as pd
import numpy as np

def main():
    # Step 1: User input
    ticker_symbol = input("Enter the ticker symbol: ").upper()
    
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Step 2: Get spot price with error handling
        hist_data = ticker.history(period="1d")
        if hist_data.empty:
            print("Error: No price data available for this ticker")
            return
        
        spot_price = hist_data['Close'].iloc[-1]
        print(f"\nLive Spot Price: ${spot_price:.2f}")

        # Step 3: Fetch nearest expiry and options
        options = ticker.options
        if not options:
            print("Error: No options data available for this ticker")
            return
            
        expiry = options[0]  # Nearest expiry
        print(f"Selected Expiry: {expiry}")
        
        option_chain = ticker.option_chain(expiry)
        calls = option_chain.calls
        puts = option_chain.puts
        
        if calls.empty or puts.empty:
            print("Error: No option chain data available for selected expiry")
            return

        # Step 4: Find ATM strike (closest to spot price)
        strikes = calls['strike'].tolist()
        atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
        print(f"ATM Strike: ${atm_strike}")

        # Step 5: Get ATM option rows
        atm_call = calls[calls['strike'] == atm_strike]
        atm_put = puts[puts['strike'] == atm_strike]

        # Step 6: Calculate Time to expiry (T) with improved handling
        expiry_date = pd.to_datetime(expiry)
        now = pd.to_datetime(dt.datetime.now())
        days_to_expiry = (expiry_date - now).days
        
        if days_to_expiry <= 0:
            T = 1/365  # 1 day minimum
            print("⚠️ Warning: Option is expiring today or has expired. Using minimum time value.")
        else:
            T = days_to_expiry / 365
            
        print(f"Days to Expiry: {days_to_expiry}")
        print(f"Time to Expiry (T): {T:.4f}")
        
        # Market parameters
        r = 0.04  # Risk-free rate
        q = 0.01  # Dividend yield

        # Step 7: Calculate for Call
        if not atm_call.empty:
            vol_call = atm_call['impliedVolatility'].values[0]
            market_call_price = atm_call['lastPrice'].values[0]
            bid_call = atm_call['bid'].values[0]
            ask_call = atm_call['ask'].values[0]
            volume_call = atm_call['volume'].values[0]
            
            print("\n" + "="*50)
            print("CALL OPTION ANALYSIS")
            print("="*50)
            print(f"Market Price: ${market_call_price:.2f}")
            print(f"Bid: ${bid_call:.2f}")
            print(f"Ask: ${ask_call:.2f}")
            print(f"Volume: {volume_call:,.0f}")
            print(f"Implied Volatility: {vol_call*100:.2f}%")
            
            # Check for valid IV
            if vol_call <= 0 or np.isnan(vol_call):
                print("❌ Error: Invalid implied volatility for call option")
            else:
                model_call = black_scholes(S=spot_price, K=atm_strike, r=r, T=T, q=q, vol=vol_call, option_type='call')
                
                if model_call is not None:
                    model_call_price = model_call['Call Price']
                    mispricing = ((market_call_price - model_call_price) / model_call_price) * 100
                    
                    print(f"\nBSM Model Price: ${model_call_price:.2f}")
                    print(f"Mispricing: {mispricing:.2f}%")
                    
                    print("\n--- GREEKS ---")
                    for greek, val in model_call.items():
                        if greek != 'Call Price':
                            print(f"{greek}: {val:.4f}")
                else:
                    print("❌ Error: Could not calculate Black-Scholes price for call option")

        # Step 8: Calculate for Put
        if not atm_put.empty:
            vol_put = atm_put['impliedVolatility'].values[0]
            market_put_price = atm_put['lastPrice'].values[0]
            bid_put = atm_put['bid'].values[0]
            ask_put = atm_put['ask'].values[0]
            volume_put = atm_put['volume'].values[0]
            
            print("\n" + "="*50)
            print("PUT OPTION ANALYSIS")
            print("="*50)
            print(f"Market Price: ${market_put_price:.2f}")
            print(f"Bid: ${bid_put:.2f}")
            print(f"Ask: ${ask_put:.2f}")
            print(f"Volume: {volume_put:,.0f}")
            print(f"Implied Volatility: {vol_put*100:.2f}%")
            
            # Check for valid IV
            if vol_put <= 0 or np.isnan(vol_put):
                print("❌ Error: Invalid implied volatility for put option")
            else:
                model_put = black_scholes(S=spot_price, K=atm_strike, r=r, T=T, q=q, vol=vol_put, option_type='put')
                
                if model_put is not None:
                    model_put_price = model_put['Put Price']
                    mispricing = ((market_put_price - model_put_price) / model_put_price) * 100
                    
                    print(f"\nBSM Model Price: ${model_put_price:.2f}")
                    print(f"Mispricing: {mispricing:.2f}%")
                    
                    print("\n--- GREEKS ---")
                    for greek, val in model_put.items():
                        if greek != 'Put Price':
                            print(f"{greek}: {val:.4f}")
                else:
                    print("❌ Error: Could not calculate Black-Scholes price for put option")

        print("\n" + "="*50)
        print("ANALYSIS COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please check the ticker symbol and try again.")

if __name__ == "__main__":
    main()