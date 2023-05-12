class Spread:
    def __init__(self, options):
        self.calls = [option for option in options if option.option_type == "Call"]
        self.puts = [option for option in options if option.option_type == "Put"]

    @staticmethod
    def group_options_by_strike(options):
        grouped_options = {}
        for option in options:
            if option.strike in grouped_options:
                grouped_options[option.strike].append(option)
            else:
                grouped_options[option.strike] = [option]
        return grouped_options

    def analyze(self):
        calls_by_strike = self.group_options_by_strike(self.calls)
        puts_by_strike = self.group_options_by_strike(self.puts)

        straddle_result = self.check_straddle(calls_by_strike, puts_by_strike)
        if straddle_result is not None:
            spread_type, _ = straddle_result
            return spread_type

        strangle_result = self.check_strangle(calls_by_strike, puts_by_strike)
        if strangle_result is not None:
            spread_type = strangle_result
            return spread_type

        butterfly_result = self.check_butterfly(calls_by_strike, puts_by_strike)
        if butterfly_result is not None:
            spread_type = butterfly_result
            return spread_type

        return "Undefined"


    def check_option_quantity_ratio(self, options, *ratios):
        counts = [option.quantity for option in options]
        return tuple(counts) == ratios


    def check_same_strike(self, options):
        strikes = set(option.strike for option in options)
        return len(strikes) == 1
    
    def check_straddle(self, calls_by_strike, puts_by_strike):
        for strike, calls in calls_by_strike.items():
            if strike in puts_by_strike:
                puts = puts_by_strike[strike]
                if len(calls) == len(puts):
                    if all(call.quantity == put.quantity and call.is_buy == put.is_buy for call, put in zip(calls, puts)):
                        spread_type = "Long Straddle" if calls[0].is_buy else "Short Straddle"
                        return spread_type
        return None

    def check_strangle(self, calls_by_strike, puts_by_strike):
        call_strikes = set(calls_by_strike.keys())
        put_strikes = set(puts_by_strike.keys())

        for call_strike in call_strikes:
            for put_strike in put_strikes:
                if call_strike == put_strike:
                    continue
                call_options = calls_by_strike[call_strike]
                put_options = puts_by_strike[put_strike]

                if all(call.quantity == put.quantity and call.is_buy == put.is_buy for call, put in zip(call_options, put_options)):
                    spread_type = "Long Strangle" if call_options[0].is_buy else "Short Strangle"
                    return spread_type

        return None
    
    def check_butterfly(self, calls_by_strike, puts_by_strike):
        sorted_call_strikes = sorted(calls_by_strike.keys())
        sorted_put_strikes = sorted(puts_by_strike.keys())

        for i in range(1, len(sorted_call_strikes) - 1):
            lower_call_strike = sorted_call_strikes[i - 1]
            middle_call_strike = sorted_call_strikes[i]
            upper_call_strike = sorted_call_strikes[i + 1]

            if upper_call_strike - middle_call_strike == middle_call_strike - lower_call_strike:
                lower_calls = calls_by_strike[lower_call_strike]
                middle_calls = calls_by_strike[middle_call_strike]
                upper_calls = calls_by_strike[upper_call_strike]

                if len(lower_calls) == len(upper_calls) == len(middle_calls) // 2:
                    is_butterfly = all(
                        lower_call.quantity == upper_call.quantity == middle_call.quantity // 2 and
                        lower_call.is_buy != middle_call.is_buy == upper_call.is_buy
                        for lower_call, upper_call, middle_call in zip(lower_calls, upper_calls, middle_calls[:len(lower_calls)]))
                    if is_butterfly:
                        spread_type = "Long Butterfly" if lower_calls[0].is_buy else "Short Butterfly"
                        return spread_type

        for i in range(1, len(sorted_put_strikes) - 1):
            lower_put_strike = sorted_put_strikes[i - 1]
            middle_put_strike = sorted_put_strikes[i]
            upper_put_strike = sorted_put_strikes[i + 1]

            if upper_put_strike - middle_put_strike == middle_put_strike - lower_put_strike:
                lower_puts = puts_by_strike[lower_put_strike]
                middle_puts = puts_by_strike[middle_put_strike]
                upper_puts = puts_by_strike[upper_put_strike]

                if len(lower_puts) == len(upper_puts) == len(middle_puts) // 2:
                    is_butterfly = all(
                        lower_put.quantity == upper_put.quantity == middle_put.quantity // 2 and
                        lower_put.is_buy != middle_put.is_buy == upper_put.is_buy
                        for lower_put, upper_put, middle_put in zip(lower_puts, upper_puts, middle_puts[:len(lower_puts)]))
                    if is_butterfly:
                        spread_type = "Long Butterfly" if lower_puts[0].is_buy else "Short Butterfly"
                        return spread_type

        return None





    def populate_attributes(self, spread_type, spread_label):
        spread_characteristics = {
            "Long Straddle":  {"gamma": "+", "theta": "-", "vega": "+", "downside": "Unlimited reward", "upside": "Unlimited reward"},
            "Long Strangle":  {"gamma": "+", "theta": "-", "vega": "+", "downside": "Unlimited reward", "upside": "Unlimited reward"},
            "Short Butterfly": {"gamma": "+", "theta": "-", "vega": "+", "downside": "Limited reward", "upside": "Limited reward"},
            "Short Condor": {"gamma": "+", "theta": "-", "vega": "+", "downside": "Limited reward", "upside": "Limited reward"},
            "Short Straddle": {"gamma": "-", "theta": "+", "vega": "-", "downside": "Unlimited risk", "upside": "Unlimited risk"},
            "Short Strangle": {"gamma": "-", "theta": "+", "vega": "-", "downside": "Unlimited risk", "upside": "Unlimited risk"},
            "Long Butterfly": {"gamma": "-", "theta": "+", "vega": "-", "downside": "Limited risk", "upside": "Limited risk"},
            "Long Condor": {"gamma": "-", "theta": "+", "vega": "-", "downside": "Limited risk", "upside": "Limited risk"},
        }

        if spread_type in spread_characteristics:
            attributes = spread_characteristics[spread_type]
            spread_label.setText(f"{spread_type} (Gamma: {attributes['gamma']}, Theta: {attributes['theta']}, Vega: {attributes['vega']})")
            self.downside_risk = attributes['downside']
            self.upside_risk = attributes['upside']
        else:
            spread_label.setText("Undefined")
            self.downside_risk = None
            self.upside_risk = None