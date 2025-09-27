#!/usr/bin/env python3
"""
Test NASA API functions locally to debug the issue
"""
import asyncio
import httpx
from datetime import datetime, timedelta

# NASA API Configuration
NASA_API_KEY = "M7JQ4IxiBtyLjJjupXOev2tAcqg1EgEBQ0nagvWW"
NASA_EARTHDATA_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InJhZml1enphbWFuIiwiZXhwIjoxNzY0MjAxNTk5LCJpYXQiOjE3NTg5ODA3NjMsImlzcyI6Imh0dHBzOi8vdXJzLmVhcnRoZGF0YS5uYXNhLmdvdiIsImlkZW50aXR5X3Byb3ZpZGVyIjoiZWRsX29wcyIsImFjciI6ImVkbCIsImFzc3VyYW5jZV9sZXZlbCI6M30.A3UEvv9NvNuFt2GGwBtiScJunBq2wvYgBu1yZZp4xVjrZLo5Auk4sOr80txxRaOJlqPuOlGhqf0k_ng2PyEimhhD_xAzjUrjHVVTsfKGVToE_JkxaUdwJzUq-k6KQXpY3wl0JfmQ3qboB1Xvj9y1QHOZRmrA3p629RWKjhsLQZ2l-RPrQrDXL60jrvZhJbbLKvOUaMW9piegrTqr-QMFeOZV5_RHs4R0wVd9qRVmvQ1a8-2z0XAmhnPqqfg0ZZeriCOuzhOlUkYFs5R4ucysl6gE3S0F1LKh_b-cBx_VD83CZ-40gmoVAbnTgKBlqXsVt-_gYTha7aa_zxy1sIcz8w"
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

async def test_nasa_power_data(lat: float, lon: float, days_back: int = 30):
    """
    Test NASA POWER API call with the same logic as in backend.py
    """
    try:
        print(f"Testing NASA POWER API for lat={lat}, lon={lon}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        print(f"Date range: {start_str} to {end_str}")
        
        # Key agricultural parameters
        params = [
            "T2M", "T2M_MAX", "T2M_MIN",  # Temperature
            "PRECTOTCORR",                 # Precipitation
            "RH2M",                        # Humidity
            "WS2M",                        # Wind speed
            "ALLSKY_SFC_SW_DWN"           # Solar radiation
        ]
        
        url = f"{NASA_POWER_BASE_URL}?parameters={','.join(params)}&community=SB&longitude={lon}&latitude={lat}&start={start_str}&end={end_str}&format=JSON"
        print(f"Request URL: {url}")
        
        # Prepare headers for authentication if tokens are available
        headers = {}
        if NASA_API_KEY:
            headers["X-API-Key"] = NASA_API_KEY
            print(f"Using NASA_API_KEY: {NASA_API_KEY[:20]}...")
        if NASA_EARTHDATA_TOKEN:
            headers["Authorization"] = f"Bearer {NASA_EARTHDATA_TOKEN}"
            print(f"Using NASA_EARTHDATA_TOKEN: {NASA_EARTHDATA_TOKEN[:30]}...")
        
        print(f"Headers: {list(headers.keys())}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            print("Making HTTP request...")
            response = await client.get(url, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response data keys: {list(data.keys())}")
                
                # Verify we have actual data
                if data and "properties" in data and "parameter" in data["properties"]:
                    print("✅ SUCCESS: Valid data structure found")
                    print(f"Parameters available: {list(data['properties']['parameter'].keys())}")
                    return {
                        "success": True,
                        "dataset": "POWER",
                        "data": data,
                        "location": f"Lat: {lat:.2f}, Lon: {lon:.2f}",
                        "date_range": f"{start_str} to {end_str}",
                        "parameters": ["temperature", "precipitation", "humidity", "solar_radiation"]
                    }
                else:
                    print("❌ FAILURE: Invalid data structure")
                    print(f"Data keys: {list(data.keys()) if data else 'No data'}")
                    if data and "properties" in data:
                        print(f"Properties keys: {list(data['properties'].keys())}")
            elif response.status_code == 401:
                print(f"❌ NASA POWER API authentication failed: {response.status_code}")
            elif response.status_code == 403:
                print(f"❌ NASA POWER API access forbidden: {response.status_code}")
            else:
                print(f"❌ NASA POWER API error: HTTP {response.status_code}")
                print(f"Response text: {response.text[:500]}")
    
    except Exception as e:
        print(f"❌ NASA POWER API error: {e}")
        import traceback
        traceback.print_exc()
    
    return {"success": False, "dataset": "POWER", "error": "Unable to fetch climate data"}

async def main():
    print("=== Testing NASA POWER API ===")
    
    # Test with New York coordinates (same as in our curl test)
    lat, lon = 40.7128, -74.0060
    result = await test_nasa_power_data(lat, lon)
    
    print(f"\nFinal result: {result}")
    print(f"Success: {result.get('success', False)}")
    
    if result.get('success'):
        print("🎉 NASA POWER API is working correctly!")
    else:
        print("💥 NASA POWER API test failed")

if __name__ == "__main__":
    asyncio.run(main())