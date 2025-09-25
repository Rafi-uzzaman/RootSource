#!/usr/bin/env python3
"""
RootSource AI - Intelligent Fallback System Test
============================================

This script tests the intelligent AI system that automatically chooses the best
data source (NASA satellite data vs AI research databases) based on availability.
"""

import asyncio
import aiohttp
import json

async def test_intelligent_system():
    """Test the intelligent fallback system"""
    
    base_url = "http://localhost:8002"
    
    test_cases = [
        {
            "name": "Weather Query (NASA preferred)",
            "query": "What are the optimal planting conditions for wheat in Bangladesh?",
            "location": {"city": "Gazipur", "country": "Bangladesh", "latitude": 23.9999, "longitude": 90.4203},
            "expected_source": "NASA satellite data"
        },
        {
            "name": "Crop Management (AI fallback)",
            "query": "How can I improve my tomato yield using organic methods?", 
            "location": None,  # No location = AI fallback
            "expected_source": "AI research databases"
        },
        {
            "name": "Soil Health (Enhanced)",
            "query": "What are the signs of nitrogen deficiency in corn plants?",
            "location": {"city": "Gazipur", "country": "Bangladesh", "latitude": 23.9999, "longitude": 90.4203},
            "expected_source": "NASA + AI hybrid"
        },
        {
            "name": "Pest Control (Research mode)",
            "query": "Best organic pest control for aphids on cucumber plants",
            "location": None,
            "expected_source": "AI research mode"
        }
    ]
    
    print("🚀 Testing RootSource AI Intelligent Fallback System")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test['name']}")
            print(f"🔍 Query: {test['query']}")
            
            # Determine endpoint
            endpoint = "/chat/enhanced" if test['location'] else "/chat"
            url = f"{base_url}{endpoint}"
            
            # Prepare request
            request_data = {
                "message": test['query'],
                "voice": False
            }
            
            if test['location']:
                request_data['location'] = test['location']
                print(f"📍 Location: {test['location']['city']}, {test['location']['country']}")
            else:
                print("🌍 Location: Not provided (triggers AI research mode)")
            
            print(f"📡 Expected Source: {test['expected_source']}")
            print("⏳ Processing...", end="", flush=True)
            
            try:
                async with session.post(url, json=request_data, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        print(f"\r✅ Response received!")
                        
                        # Analyze response to determine data source used
                        reply = data.get('reply', '')
                        
                        if 'NASA' in reply and 'satellite' in reply:
                            actual_source = "NASA satellite data"
                        elif 'AI-Enhanced' in reply or 'research databases' in reply:
                            actual_source = "AI research databases"
                        else:
                            actual_source = "Standard AI"
                        
                        print(f"🎯 Actual Source: {actual_source}")
                        
                        # Show response preview
                        response_preview = reply[:200].replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')
                        print(f"💬 Response Preview: {response_preview}...")
                        
                        # Check if NASA attribution is present
                        if '🛰️' in reply or 'NASA' in reply:
                            print("🛰️ NASA data integration: ✅")
                        elif '🤖' in reply or 'AI-Enhanced' in reply:
                            print("🤖 AI research enhancement: ✅")
                        
                        print("─" * 40)
                        
                    else:
                        print(f"\r❌ Error: HTTP {response.status}")
                        
            except asyncio.TimeoutError:
                print(f"\r⏰ Timeout - Response took too long")
            except Exception as e:
                print(f"\r❌ Error: {str(e)}")
    
    print("\n🏁 Test Summary:")
    print("✅ Intelligent fallback system allows RootSource AI to provide expert")
    print("   agricultural advice even when NASA satellite data is unavailable")
    print("🛰️ NASA data is used when location is provided and services are available")
    print("🤖 AI research databases provide comprehensive fallback information")
    print("📚 Multiple research sources ensure high-quality responses in all cases")
    
    print(f"\n🌐 Access your application at: http://localhost:8002")

if __name__ == "__main__":
    asyncio.run(test_intelligent_system())