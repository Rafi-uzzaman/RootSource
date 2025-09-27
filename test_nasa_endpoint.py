#!/usr/bin/env python3
"""
Test endpoint to check NASA API directly from Railway deployment
"""
import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime, timedelta

app = FastAPI()

NASA_API_KEY = "M7JQ4IxiBtyLjJjupXOev2tAcqg1EgEBQ0nagvWW"
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

@app.get("/test-nasa")
async def test_nasa_endpoint():
    """
    Direct test of NASA POWER API
    """
    try:
        lat, lon = 40.7128, -74.0060
        days_back = 7
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        params = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR"]
        
        url = f"{NASA_POWER_BASE_URL}?parameters={','.join(params)}&community=SB&longitude={lon}&latitude={lat}&start={start_str}&end={end_str}&format=JSON"
        
        headers = {}
        if NASA_API_KEY:
            headers["X-API-Key"] = NASA_API_KEY
        
        result = {
            "test_info": {
                "url": url,
                "headers": list(headers.keys()),
                "date_range": f"{start_str} to {end_str}",
                "coordinates": {"lat": lat, "lon": lon}
            },
            "status": "attempting_request",
            "success": False
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            result["http_status"] = response.status_code
            result["response_headers"] = dict(response.headers)
            
            if response.status_code == 200:
                data = response.json()
                result["success"] = True
                result["data_keys"] = list(data.keys()) if data else []
                
                if data and "properties" in data and "parameter" in data["properties"]:
                    result["nasa_parameters"] = list(data["properties"]["parameter"].keys())
                    result["sample_data"] = {
                        "first_param": list(data["properties"]["parameter"].values())[0] if data["properties"]["parameter"] else None
                    }
                else:
                    result["error"] = "Invalid data structure"
                    result["data_sample"] = str(data)[:500] if data else "No data"
            else:
                result["error"] = f"HTTP {response.status_code}"
                result["response_text"] = response.text[:500]
                
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)