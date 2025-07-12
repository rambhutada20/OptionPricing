import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt
from OptionPricingDash import black_scholes
import numpy as np

st.set_page_config(page_title="ATM Option Analyzer", layout="wide")

st.title("📈 ATM Option Pricing & Greeks Dashboard")

# --- Ticker input ---
ticker_symbol = st.text_input("Enter Stock Ticker", value="AAPL").upper()

if ticker_symbol:
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # Get spot price with error handling
        hist_data = ticker.history(period="1d")
        if hist_data.empty:
            st.error("No price data available for this ticker")
            st.stop()
            
        spot_price = hist_data['Close'].iloc[-1]
        st.markdown(f"**Live Spot Price:** ${spot_price:.2f}")

        # --- Expiry selection ---
        expiries = ticker.options
        if not expiries:
            st.error("No options data available for this ticker")
            st.stop()
            
        expiry = st.selectbox("Select Option Expiry", expiries)

        # --- Option Chain Data ---
        option_chain = ticker.option_chain(expiry)
        calls = option_chain.calls
        puts = option_chain.puts

        if calls.empty or puts.empty:
            st.error("No option chain data available for selected expiry")
            st.stop()

        # --- Find ATM Strike ---
        strikes = calls['strike'].tolist()
        atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
        st.markdown(f"**ATM Strike Price:** ${atm_strike}")

        # --- Filter ATM options ---
        atm_call = calls[calls['strike'] == atm_strike]
        atm_put = puts[puts['strike'] == atm_strike]

        # --- Calculate Time to Expiry (improved) ---
        expiry_date = pd.to_datetime(expiry)
        now = pd.to_datetime(dt.datetime.now())
        
        # Calculate days to expiry
        days_to_expiry = (expiry_date - now).days
        
        # If same day or past expiry, set minimum time
        if days_to_expiry <= 0:
            T = 1/365  # 1 day minimum
            st.warning("⚠️ Option is expiring today or has expired. Using minimum time value.")
        else:
            T = days_to_expiry / 365
            
        st.markdown(f"**Days to Expiry:** {days_to_expiry}")
        st.markdown(f"**Time to Expiry (T):** {T:.4f}")

        # --- Market parameters ---
        r = 0.04  # Risk-free rate
        q = 0.01  # Dividend yield

        # --- Choose Option Type ---
        option_type = st.radio("Select Option Type", ["Call", "Put"])

        # --- Call Option Analysis ---
        if option_type == "Call" and not atm_call.empty:
            st.subheader("📊 Call Option Analysis")
            
            # Get option data
            iv = atm_call['impliedVolatility'].values[0]
            market_price = atm_call['lastPrice'].values[0]
            bid = atm_call['bid'].values[0]
            ask = atm_call['ask'].values[0]
            volume = atm_call['volume'].values[0]
            
            # Display market data
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Price", f"${market_price:.2f}")
                st.metric("Bid", f"${bid:.2f}")
            with col2:
                st.metric("Ask", f"${ask:.2f}")
                st.metric("Volume", f"{volume:,.0f}")
            with col3:
                st.metric("Implied Volatility", f"{iv*100:.2f}%")
            
            # Check for valid IV
            if iv <= 0 or np.isnan(iv):
                st.error("Invalid implied volatility. Cannot calculate BSM price.")
            else:
                # Calculate BSM
                bs = black_scholes(S=spot_price, K=atm_strike, r=r, T=T, q=q, vol=iv, option_type='call')
                
                if bs is not None:
                    bsm_price = bs['Call Price']
                    mispricing = ((market_price - bsm_price) / bsm_price) * 100
                    
                    # Display BSM results
                    st.markdown("### Black-Scholes Model Results")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("BSM Price", f"${bsm_price:.2f}")
                    with col2:
                        if abs(mispricing) > 5:
                            st.metric("Mispricing", f"{mispricing:.2f}%", delta=f"{mispricing:.2f}%")
                        else:
                            st.metric("Mispricing", f"{mispricing:.2f}%")
                    
                    # Display Greeks
                    st.markdown("### Option Greeks")
                    greeks_data = {k: v for k, v in bs.items() if k != "Call Price"}
                    
                    # Create a nice display for Greeks
                    greek_cols = st.columns(len(greeks_data))
                    for i, (greek, value) in enumerate(greeks_data.items()):
                        with greek_cols[i]:
                            st.metric(greek.replace("Call ", ""), f"{value:.4f}")
                else:
                    st.error("Error calculating Black-Scholes price. Please check input parameters.")

        # --- Put Option Analysis ---
        elif option_type == "Put" and not atm_put.empty:
            st.subheader("📊 Put Option Analysis")
            
            # Get option data
            iv = atm_put['impliedVolatility'].values[0]
            market_price = atm_put['lastPrice'].values[0]
            bid = atm_put['bid'].values[0]
            ask = atm_put['ask'].values[0]
            volume = atm_put['volume'].values[0]
            
            # Display market data
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Price", f"${market_price:.2f}")
                st.metric("Bid", f"${bid:.2f}")
            with col2:
                st.metric("Ask", f"${ask:.2f}")
                st.metric("Volume", f"{volume:,.0f}")
            with col3:
                st.metric("Implied Volatility", f"{iv*100:.2f}%")
            
            # Check for valid IV
            if iv <= 0 or np.isnan(iv):
                st.error("Invalid implied volatility. Cannot calculate BSM price.")
            else:
                # Calculate BSM
                bs = black_scholes(S=spot_price, K=atm_strike, r=r, T=T, q=q, vol=iv, option_type='put')
                
                if bs is not None:
                    bsm_price = bs['Put Price']
                    mispricing = ((market_price - bsm_price) / bsm_price) * 100
                    
                    # Display BSM results
                    st.markdown("### Black-Scholes Model Results")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("BSM Price", f"${bsm_price:.2f}")
                    with col2:
                        if abs(mispricing) > 5:
                            st.metric("Mispricing", f"{mispricing:.2f}%", delta=f"{mispricing:.2f}%")
                        else:
                            st.metric("Mispricing", f"{mispricing:.2f}%")
                    
                    # Display Greeks
                    st.markdown("### Option Greeks")
                    greeks_data = {k: v for k, v in bs.items() if k != "Put Price"}
                    
                    # Create a nice display for Greeks
                    greek_cols = st.columns(len(greeks_data))
                    for i, (greek, value) in enumerate(greeks_data.items()):
                        with greek_cols[i]:
                            st.metric(greek.replace("Put ", ""), f"{value:.4f}")
                else:
                    st.error("Error calculating Black-Scholes price. Please check input parameters.")

        # --- Debug Information ---
        with st.expander("🔍 Debug Information"):
            st.write(f"**Spot Price:** {spot_price}")
            st.write(f"**ATM Strike:** {atm_strike}")
            st.write(f"**Time to Expiry:** {T}")
            st.write(f"**Risk-free Rate:** {r}")
            st.write(f"**Dividend Yield:** {q}")
            
            if option_type == "Call" and not atm_call.empty:
                st.write(f"**Call IV:** {atm_call['impliedVolatility'].values[0]}")
                st.write(f"**Call Last Price:** {atm_call['lastPrice'].values[0]}")
            elif option_type == "Put" and not atm_put.empty:
                st.write(f"**Put IV:** {atm_put['impliedVolatility'].values[0]}")
                st.write(f"**Put Last Price:** {atm_put['lastPrice'].values[0]}")

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Please check the ticker symbol and try again.")
        
        # Debug info
        with st.expander("Error Details"):
            st.exception(e)