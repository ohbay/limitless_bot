import math
import time

class ProbabilityEngine:
    """
    Calculates probabilities for market outcomes.
    """
    
    @staticmethod
    def norm_cdf(x):
        """Cumulative distribution function for the standard normal distribution."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    @staticmethod
    def calculate_probability(current_price, strike_price, time_to_expiry_years, volatility=0.6, risk_free_rate=0.05):
        """
        Calculate the probability of price > strike_price at expiration.
        Using Black-Scholes risk-neutral probability (N(d2)).
        
        :param volatility: Annualized volatility (e.g., 0.6 for 60%)
        """
        if time_to_expiry_years <= 0:
            return 1.0 if current_price > strike_price else 0.0
            
        S = current_price
        K = strike_price
        T = time_to_expiry_years
        r = risk_free_rate
        sigma = volatility
        
        # d2 term from Black-Scholes
        # d2 = (ln(S/K) + (r - 0.5 * sigma^2) * T) / (sigma * sqrt(T))
        
        try:
            numerator = math.log(S / K) + (r - 0.5 * sigma**2) * T
            denominator = sigma * math.sqrt(T)
            d2 = numerator / denominator
            
            prob_ITM = ProbabilityEngine.norm_cdf(d2)
            return prob_ITM
        except ValueError:
            # Can happen if S or K is negative/zero
            return 0.0

    @staticmethod
    def get_time_to_expiry(deadline_iso):
        """
        Calculate years to expiry from ISO timestamp.
        """
        try:
            # Simple parsing, assuming UTC "Z" or similar
            # For robustness, we might want dateutil, but let's try basic strptime
            # Format example: "2024-12-31T23:59:59Z"
            import datetime
            
            # Remove Z if present
            deadline_iso = deadline_iso.replace("Z", "+00:00")
            
            deadline = datetime.datetime.fromisoformat(deadline_iso)
            now = datetime.datetime.now(datetime.timezone.utc)
            
            diff = deadline - now
            years = diff.total_seconds() / (365.25 * 24 * 60 * 60)
            return max(0, years)
        except Exception as e:
            print(f"[Analytics] Error parsing deadline {deadline_iso}: {e}")
            return 0
