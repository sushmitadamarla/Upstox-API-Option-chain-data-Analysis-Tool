import os
import requests
import pandas as pd
from dotenv import load_dotenv
import logging
import random
import string

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client_id = os.getenv("UPSTOX_API_KEY")
client_secret = os.getenv("UPSTOX_API_SECRET")
redirect_uri = "https://upstox.com"

logger.info(f"API Key (client_id): {client_id}")

state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
auth_url = (
    f"https://api.upstox.com/v2/login/authorization/dialog?"
    f"client_id={client_id}&"
    f"redirect_uri={redirect_uri}&"
    f"response_type=code&"
    f"scope=read&"
    f"state={state}"
)

logger.info("Please go to this URL and authorize the app:")
logger.info(auth_url)

auth_code = input("Enter the authorization code from the redirect URL: ")

token_url = "https://api.upstox.com/v2/login/authorization/token"
data = {
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code'
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}

try:
    response = requests.post(token_url, data=data, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    access_token = response_data.get("access_token")
    
    if not access_token:
        logger.error("Access token not found in the response.")
        exit()
    
    logger.info("Access token successfully retrieved!")
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error occurred: {e} - Response: {response.text}")
    exit()
except Exception as e:
    logger.error(f"Failed to retrieve access token: {e}")
    exit()

# Function to retrieve option contracts data
def get_option_chain_data(instrument_key: str, expiry_date: str, side: str) -> pd.DataFrame:
    logger.info(f"Fetching option chain data for {instrument_key} on {expiry_date} ({side})")
    
    option_chain_endpoint = "https://api.upstox.com/v2/option/contract"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    params = {
        "instrument_key": instrument_key,
        "expiry_date": expiry_date
    }
    
    try:
        response = requests.get(option_chain_endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "success":
            logger.error(f"Failed to fetch option chain data: {data}")
            return pd.DataFrame()
        
        rows = []
        for option in data.get('data', []):
            market_data = option.get("call_options" if side == "CE" else "put_options", {}).get("market_data", {})
            bid_ask_price = market_data.get("ask_price" if side == "CE" else "bid_price")
            
            if bid_ask_price is not None:
                rows.append([instrument_key, option['strike_price'], side, bid_ask_price])
            else:
                rows.append([instrument_key, option['strike_price'], side, 0]) 
        
        df = pd.DataFrame(rows, columns=["instrument_name", "strike_price", "side", "bid/ask"])
        return df
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred while fetching option chain data: {e} - Response: {response.text}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error occurred while fetching option chain data: {e}")
        return pd.DataFrame()


# Function to calculate margin and premium earned
def calculate_margin_and_premium(data: pd.DataFrame) -> pd.DataFrame:
    logger.info("Calculating margin and premium earned for each option")
    margins = []
    premiums = []
    
    for _, row in data.iterrows():
        margin_required = get_margin_requirement(row['instrument_name'], row['strike_price'], row['side'])
        margins.append(margin_required)

        lot_size = 75 
        premium_earned = row["bid/ask"] * lot_size
        premiums.append(premium_earned)
    
    data["margin_required"] = margins
    data["premium_earned"] = premiums
    return data

def get_margin_requirement(instrument_name, strike_price, side):
    # For the sake of this example, returning a static value
    return 10000  

# Example usage
instrument_name = "NSE_INDEX|Nifty 50" 
expiry_date = "2024-11-07"  
side = "CE" 

# Step 1: Get option chain data
option_chain_data = get_option_chain_data(instrument_name, expiry_date, side)
logger.info(f"Option Chain Data:\n{option_chain_data}")

# Step 2: Calculate margin and premium earned
if not option_chain_data.empty:
    final_data = calculate_margin_and_premium(option_chain_data)
    logger.info(f"Final Data with Margin and Premium:\n{final_data}")
else:
    logger.warning("No option chain data available to calculate margin and premium.")
