import numpy as np
import pandas as pd
from scipy.stats import norm
from math import log, exp, sqrt

def black_scholes(S, K, r, T, q, vol, option_type='call'):
    """
    Black-Scholes option pricing model with improved error handling
    """
    # Input validation
    if S <= 0 or K <= 0 or T <= 0 or vol <= 0:
        return None
    
    # Set minimum values to avoid division by zero
    T = max(T, 1/365)  # At least 1 day
    vol = max(vol, 0.001)  # At least 0.1% volatility
    
    try:
        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r - q + 0.5 * vol**2) * T) / (vol * np.sqrt(T))
        d2 = d1 - vol * np.sqrt(T)
        
        # Calculate Greeks (common for both call and put)
        gamma = norm.pdf(d1) * exp(-q * T) / (S * vol * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) * exp(-q * T) / 100  # Divide by 100 for percentage
        
        if option_type == 'call':
            price = S * exp(-q * T) * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
            delta = norm.cdf(d1) * exp(-q * T)
            theta = (
                (-S * norm.pdf(d1) * vol * exp(-q * T)) / (2 * np.sqrt(T))
                - r * K * exp(-r * T) * norm.cdf(d2)
                + q * S * exp(-q * T) * norm.cdf(d1)
            ) / 365
            rho = K * T * exp(-r * T) * norm.cdf(d2) / 100  # Divide by 100 for percentage
            
            return {
                'Call Price': price,
                'Call Delta': delta,
                'Call Gamma': gamma,
                'Call Vega': vega,
                'Call Theta': theta,
                'Call Rho': rho
            }
            
        elif option_type == 'put':
            price = K * exp(-r * T) * norm.cdf(-d2) - S * exp(-q * T) * norm.cdf(-d1)
            delta = exp(-q * T) * (norm.cdf(d1) - 1)
            theta = (
                (-S * norm.pdf(d1) * vol * exp(-q * T)) / (2 * np.sqrt(T))
                + r * K * exp(-r * T) * norm.cdf(-d2)
                - q * S * exp(-q * T) * norm.cdf(-d1)
            ) / 365
            rho = -K * T * exp(-r * T) * norm.cdf(-d2) / 100  # Divide by 100 for percentage
            
            return {
                'Put Price': price,
                'Put Delta': delta,
                'Put Gamma': gamma,
                'Put Vega': vega,
                'Put Theta': theta,
                'Put Rho': rho
            }
        else:
            raise ValueError("option_type must be either 'call' or 'put'")
            
    except Exception as e:
        print(f"Error in Black-Scholes calculation: {e}")
        return None