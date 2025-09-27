#!/usr/bin/env python3
"""
Test script to verify NASA dataset fixes
"""
import asyncio
import httpx
import json

async def test_nasa_datasets():
    """Test if NASA datasets are properly attributed"""
    
    # Test with a agriculture-related query that should trigger NASA data
    test_query = {
        "prompt": "What is the current soil moisture and weather conditions for crops in New York?",
        "lang": "en-US"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8000/chat", json=test_query)
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get("reply", "")
                nasa_data_used = result.get("nasaDataUsed", [])
                
                print("=== NASA Dataset Test Results ===")
                print(f"Status: SUCCESS")
                print(f"NASA Datasets Used: {nasa_data_used}")
                
                # Check if the response contains NASA attribution
                if "NASA dataset(s) used:" in reply:
                    if "None" in reply and "unavailable" in reply:
                        print("❌ ISSUE DETECTED: Still showing 'None (datasets unavailable)'")
                        print(f"Response excerpt: {reply[-200:]}")
                    else:
                        print("✅ NASA attribution looks good!")
                        # Extract attribution line
                        lines = reply.split('\n')
                        nasa_line = [line for line in lines if "NASA dataset(s) used:" in line]
                        if nasa_line:
                            print(f"Attribution: {nasa_line[0]}")
                else:
                    print("⚠️  No NASA attribution found in response")
                
                return len(nasa_data_used) > 0
            else:
                print(f"❌ Request failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing NASA dataset fixes...")
    result = asyncio.run(test_nasa_datasets())
    if result:
        print("\n🎉 NASA datasets are working properly!")
    else:
        print("\n⚠️  NASA datasets may need additional fixes")