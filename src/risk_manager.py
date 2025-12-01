class RiskManager:
    """
    Manages risk and position sizing based on confidence and portfolio state.
    """
    def __init__(self, max_portfolio_risk=0.05, kelly_fraction=0.5):
        """
        :param max_portfolio_risk: Max % of portfolio to risk on a single trade (e.g. 5%)
        :param kelly_fraction: Fraction of Kelly Criterion to use (e.g. 0.5 for half-Kelly)
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.kelly_fraction = kelly_fraction

    def calculate_position_size(self, portfolio_balance, confidence, odds):
        """
        Calculate optimal position size using Kelly Criterion.
        
        :param portfolio_balance: Total available funds (USDC)
        :param confidence: Our estimated probability of winning (0.0 to 1.0)
        :param odds: Market odds (decimal, e.g. 2.0 for doubling money). 
                     In prediction markets, if price is 0.60, payout is 1.00.
                     So odds = 1.00 / 0.60 = 1.66
        """
        if confidence <= 0.5:
            return 0.0
            
        # Kelly Formula: f = (bp - q) / b
        # b = odds - 1
        # p = probability of winning (confidence)
        # q = probability of losing (1 - p)
        
        b = odds - 1
        if b <= 0:
            return 0.0
            
        p = confidence
        q = 1 - p
        
        f = (b * p - q) / b
        
        # Apply fractional Kelly for safety
        f = f * self.kelly_fraction
        
        # Cap at max risk
        f = min(f, self.max_portfolio_risk)
        
        # Ensure non-negative
        f = max(0.0, f)
        
        amount = portfolio_balance * f
        return amount

    def check_timing_risk(self, time_to_expiry_years):
        """
        Adjust risk based on time to expiry.
        Too early = high uncertainty (reduce size).
        Too late = low reward/high gamma (reduce size or be careful).
        """
        # Simple heuristic:
        # If > 1 month (0.08 years), reduce size slightly due to unknown events.
        # If < 1 day (0.0027 years), reduce size due to volatility/gamma risk.
        
        multiplier = 1.0
        if time_to_expiry_years > 0.1: # > ~36 days
            multiplier = 0.8
        elif time_to_expiry_years < 0.0027: # < 1 day
            multiplier = 0.5
            
        return multiplier
