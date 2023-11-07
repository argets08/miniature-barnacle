from alpaca_trade_api import REST, Stream

API_KEY=""
API_SECRET=""
ALPACA_BASE_URL = 'https://data.alpaca.markets'

class alpaca_client:
    def get_alpaca_client(self):
        rest_client = REST(base_url=ALPACA_BASE_URL, key_id=API_KEY,secret_key= API_SECRET)
        print(rest_client)
        return rest_client