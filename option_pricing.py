from typing import Literal, Optional
import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from math import log, sqrt, pi, exp
from scipy.stats import norm

RISK_FREE_RATE=0.04

class Option:
    def __init__(
        self,
        *,
        put_call: Literal["C", "P"],
        spot: float,
        strike: float,
        days_to_expiration: int,
        price: Optional[float] = None,
        volatility: Optional[float] = None,
    ):
        self.put_call = put_call
        self.spot = spot
        self.strike = strike
        self.days_to_expiration = days_to_expiration
        self.risk_free_rate = RISK_FREE_RATE

        if price:
            self.price = price
            self.volatility = self.get_implied_vol(
                self.put_call,
                self.price,
                self.spot,
                self.strike,
                self.days_to_expiration / 365,
                self.risk_free_rate,
            )

        else:
            self.volatility = volatility
            if put_call == "C":
                self.price = self.get_call_price(
                    self.spot,
                    self.strike,
                    self.days_to_expiration / 365,
                    self.risk_free_rate,
                    self.volatility,
                )
            else:
                self.price = self.get_put_price(
                    self.spot,
                    self.strike,
                    self.days_to_expiration / 365,
                    self.risk_free_rate,
                    self.volatility,
                )

        self.delta = self.get_delta(
            self.put_call,
            self.spot,
            self.strike,
            self.days_to_expiration / 365,
            self.risk_free_rate,
            self.volatility,
        )
        self.theta = self.get_theta(
            self.put_call,
            self.spot,
            self.strike,
            self.days_to_expiration / 365,
            self.risk_free_rate,
            self.volatility,
        )
        self.vega = self.get_vega(
            self.spot,
            self.strike,
            self.days_to_expiration / 365,
            self.risk_free_rate,
            self.volatility,
        )
        self.gamma = self.get_gamma(
            self.spot,
            self.strike,
            self.days_to_expiration / 365,
            self.risk_free_rate,
            self.volatility,
        )
        self.rho = self.get_rho(
            self.put_call,
            self.spot,
            self.strike,
            self.days_to_expiration / 365,
            self.risk_free_rate,
            self.volatility
        )
        self.option_df = pd.Series(
            [self.price, self.volatility, self.delta, self.gamma, self.theta, self.vega, self.rho],
            ["Price", "Implied Vol", "Delta", "Gamma", "Theta", "Vega", "Rho"]
        )

    def get_d1(self, S, K, T, r, sigma):
        return (log(S / K) + (r + sigma**2 / 2) * T) / (sigma * sqrt(T))

    def get_d2(self, S, K, T, r, sigma):
        return self.get_d1(S, K, T, r, sigma) - sigma * sqrt(T)

    def get_call_price(self, S, K, T, r, sigma):
        return S * norm.cdf(self.get_d1(S, K, T, r, sigma)) - K * exp(
            -r * T
        ) * norm.cdf(self.get_d2(S, K, T, r, sigma))

    def get_put_price(self, S, K, T, r, sigma):
        return K * exp(-r * T) - S + self.get_call_price(S, K, T, r, sigma)

    def get_delta(self, put_call, S, K, T, r, sigma):
        if put_call == "C":
            return norm.cdf(self.get_d1(S, K, T, r, sigma))
        return -norm.cdf(-self.get_d1(S, K, T, r, sigma))

    def get_gamma(self, S, K, T, r, sigma):
        return norm.pdf(self.get_d1(S, K, T, r, sigma)) / (S * sigma * sqrt(T))

    def get_vega(self, S, K, T, r, sigma):
        return 0.01 * (S * norm.pdf(self.get_d1(S, K, T, r, sigma)) * sqrt(T))

    def get_theta(self, put_call, S, K, T, r, sigma):
        if put_call == "C":
            return 0.01 * (
                -(S * norm.pdf(self.get_d1(S, K, T, r, sigma)) * sigma) / (2 * sqrt(T))
                - r * K * exp(-r * T) * norm.cdf(self.get_d2(S, K, T, r, sigma))
            )
        return 0.01 * (
            -(S * norm.pdf(self.get_d1(S, K, T, r, sigma)) * sigma) / (2 * sqrt(T))
            + r * K * exp(-r * T) * norm.cdf(-self.get_d2(S, K, T, r, sigma))
        )

    def get_rho(self, put_call, S, K, T, r, sigma):
        if put_call == "C":
            return 0.01 * (
                K * T * exp(-r * T) * norm.cdf(self.get_d2(S, K, T, r, sigma))
            )
        return 0.01 * (-K * T * exp(-r * T) * norm.cdf(-self.get_d2(S, K, T, r, sigma)))

    def get_implied_vol(self, put_call, P, S, K, T, r):
        sigma = 0.001
        if put_call == "C":
            while sigma < 1:
                Price_implied = S * norm.cdf(self.get_d1(S, K, T, r, sigma)) - K * exp(
                    -r * T
                ) * norm.cdf(self.get_d2(S, K, T, r, sigma))
                if P - (Price_implied) < 0.001:
                    return sigma
                sigma += 0.001
            raise RuntimeError("Could not find correct IV")
        while sigma < 1:
            Price_implied = K * exp(-r * T) - S + self.get_call_price(S, K, T, r, sigma)
            if P - (Price_implied) < 0.001:
                return sigma
            sigma += 0.001
        raise RuntimeError("Could not find correct IV")