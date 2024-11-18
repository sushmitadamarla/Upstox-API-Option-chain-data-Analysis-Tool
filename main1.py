import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sample_data = [
    {"instrument_name": "NIFTY", "strike_price": 16000, "side": "PE", "bid/ask": 150},
    {"instrument_name": "NIFTY", "strike_price": 16200, "side": "PE", "bid/ask": 140},
    {"instrument_name": "NIFTY", "strike_price": 16400, "side": "CE", "bid/ask": 130},
    {"instrument_name": "NIFTY", "strike_price": 16600, "side": "CE", "bid/ask": 120},
]

option_chain_data = pd.DataFrame(sample_data)
logger.info(f"Sample Option Chain Data:\n{option_chain_data}")

# Part 2: Function to calculate margin and premium earned (using mock margin values)
def calculate_margin_and_premium(data: pd.DataFrame) -> pd.DataFrame:
    logger.info("Calculating margin and premium earned for each option")
    margins = []
    premiums = []

    for _, row in data.iterrows():
        margin_required = 10000  # Example fixed margin for each option
        margins.append(margin_required)
        
        lot_size = 75  # Example lot size for NIFTY options
        premium_earned = row["bid/ask"] * lot_size
        premiums.append(premium_earned)

    data["margin_required"] = margins
    data["premium_earned"] = premiums
    return data

final_data = calculate_margin_and_premium(option_chain_data)
logger.info(f"Final Data with Margin and Premium:\n{final_data}")
