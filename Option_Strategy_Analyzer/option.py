import numpy as np

class Option:
    def __init__(self, option_type, strike, is_buy, premium, quantity=1):
        self.option_type = option_type
        self.strike = strike
        self.is_buy = is_buy
        self.premium = premium
        self.quantity = quantity

    def payoff(self, stock_price):
        if np.isscalar(stock_price):
            stock_price = np.array([stock_price])

        if self.option_type == 'Call':
            payoff = np.maximum(stock_price - self.strike, 0)
        else:
            payoff = np.maximum(self.strike - stock_price, 0)

        if not self.is_buy:
            payoff *= -1

        return (payoff - self.premium) * self.quantity





