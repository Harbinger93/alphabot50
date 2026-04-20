import requests

try:
    print("Testing requests...")
    res = requests.get("https://demo-fapi.binance.com/fapi/v1/exchangeInfo", timeout=10)
    print("Status code:", res.status_code)
    print("Content length:", len(res.text))
except Exception as e:
    print("Error:", e)
