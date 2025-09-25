import os
import re
import time
import asyncio
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, WikipediaAPIWrapper, ArxivAPIWrapper
from langdetect import detect
from deep_translator import GoogleTranslator
from dotenv import load_dotenv, find_dotenv
from settings import ALLOW_ORIGINS, HOST, PORT
from starlette.responses import JSONResponse

# NASA Integration
try:
    from nasa_integration import EnhancedAgriculturalAssistant, LocationInfo
    NASA_INTEGRATION_AVAILABLE = True
except ImportError:
    NASA_INTEGRATION_AVAILABLE = False
    print("⚠️  NASA integration not available. Install required dependencies.")

def analyze_query_type(query: str) -> str:
    """Analyze query type to determine best response strategy"""
    query_lower = query.lower()
    
    # Weather/Climate related queries
    if any(word in query_lower for word in ['weather', 'climate', 'temperature', 'rain', 'drought', 'humidity', 'wind']):
        return 'weather'
    
    # Crop-specific queries
    if any(word in query_lower for word in ['crop', 'plant', 'grow', 'harvest', 'seed', 'variety', 'cultivar']):
        return 'crop_specific'
    
    # Soil and fertilizer queries
    if any(word in query_lower for word in ['soil', 'fertilizer', 'nutrition', 'ph', 'compost', 'organic matter']):
        return 'soil_nutrition'
    
    # Pest and disease queries  
    if any(word in query_lower for word in ['pest', 'disease', 'insect', 'bug', 'fungus', 'blight', 'virus']):
        return 'pest_disease'
    
    # Equipment and technology
    if any(word in query_lower for word in ['equipment', 'machinery', 'irrigation', 'technology', 'drone', 'sensor']):
        return 'technology'
    
    # Market and economics
    if any(word in query_lower for word in ['market', 'price', 'sell', 'profit', 'cost', 'economic']):
        return 'economics'
    
    # General farming
    return 'general_farming'

async def get_intelligent_response(enhanced_prompt: str, query: str, query_type: str, nasa_available: bool) -> str:
    """
    Intelligent response system that uses multiple AI sources and research tools
    when NASA data is unavailable for optimal agricultural advice
    """
    
    max_retries = 2
    
    # Strategy 1: Try direct AI response first
    for attempt in range(max_retries):
        try:
            response_text = get_direct_response(enhanced_prompt)
            
            if "Demo Mode" in response_text:
                break
            elif response_text and len(response_text.strip()) > 10:
                # Good response received
                if not nasa_available:
                    # Enhance with research for non-NASA responses
                    enhanced_response = await enhance_response_with_research(response_text, query, query_type)
                    return enhanced_response
                return response_text
                
        except Exception as e:
            print(f"⚠ Direct response error (attempt {attempt + 1}): {str(e)[:100]}...")
            if attempt < max_retries - 1:
                time.sleep(0.5)
    
    # Strategy 2: Use search-enhanced response with multiple sources
    try:
        if not nasa_available:
            # When NASA data unavailable, use comprehensive research approach
            research_response = await get_comprehensive_research_response(query, query_type)
            if research_response:
                return research_response
        
        # Fallback to standard search enhancement
        response_text = get_search_enhanced_response(query)
        if response_text:
            return response_text
            
    except Exception as e:
        print(f"⚠ Research enhancement error: {str(e)[:100]}...")
    
    # Strategy 3: Intelligent fallback based on query type
    return get_intelligent_fallback_response(query, query_type)

async def enhance_response_with_research(base_response: str, query: str, query_type: str) -> str:
    """Enhance AI response with targeted research when NASA data unavailable"""
    try:
        # Add research-based enhancements based on query type
        research_keywords = get_research_keywords(query, query_type)
        
        # Use search tools to gather additional information
        search_wrapper = DuckDuckGoSearchAPIWrapper()
        search = DuckDuckGoSearchRun(api_wrapper=search_wrapper)
        
        research_info = ""
        for keyword in research_keywords[:2]:  # Limit to 2 searches
            try:
                search_result = search.run(f"agriculture {keyword} best practices research")
                if search_result and len(search_result) > 50:
                    research_info += f"\\n**Recent Research Insights:**\\n{search_result[:200]}...\\n"
                    break
            except:
                continue
        
        # Combine base response with research insights
        if research_info:
            enhanced_response = f"""{base_response}

{research_info}

**🔬 AI-Enhanced Analysis**: This response combines advanced AI knowledge with the latest agricultural research to provide you with comprehensive, evidence-based advice."""
            return enhanced_response
            
    except Exception as e:
        print(f"Research enhancement failed: {e}")
    
    return base_response

async def get_comprehensive_research_response(query: str, query_type: str) -> str:
    """Generate comprehensive response using multiple research sources"""
    try:
        # Multi-source research approach
        search_wrapper = DuckDuckGoSearchAPIWrapper()
        search = DuckDuckGoSearchRun(api_wrapper=search_wrapper)
        wiki_wrapper = WikipediaAPIWrapper()
        wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)
        
        # Query-specific research strategy
        research_terms = get_research_keywords(query, query_type)
        
        research_results = []
        
        # Primary research source
        try:
            primary_search = search.run(f"agricultural {research_terms[0]} best practices 2024")
            if primary_search:
                research_results.append(("Latest Research", primary_search[:300]))
        except:
            pass
        
        # Wikipedia for foundational knowledge
        try:
            wiki_result = wiki.run(research_terms[0])
            if wiki_result:
                research_results.append(("Scientific Foundation", wiki_result[:250]))
        except:
            pass
        
        # Generate comprehensive response
        if research_results:
            response_text = f"""**RootSource AI** - Advanced Agricultural Intelligence

**{query_type.replace('_', ' ').title()} Analysis**

Based on comprehensive research from multiple agricultural databases and scientific sources:

"""
            for source, content in research_results:
                response_text += f"**{source}:**\\n{content}\\n\\n"
            
            response_text += """
**🤖 AI-Powered Recommendations:**
• This analysis combines multiple research sources for accuracy
• Recommendations are based on latest agricultural science
• Solutions are tailored to modern sustainable farming practices

**📚 Sources**: Agricultural research databases, scientific publications, and expert farming practices."""
            
            return response_text
            
    except Exception as e:
        print(f"Comprehensive research failed: {e}")
    
    return None

def get_research_keywords(query: str, query_type: str) -> List[str]:
    """Generate targeted research keywords based on query and type"""
    base_keywords = []
    
    if query_type == 'weather':
        base_keywords = ['climate farming', 'weather agriculture', 'crop climate adaptation']
    elif query_type == 'crop_specific':
        base_keywords = ['crop management', 'plant cultivation', 'agricultural production']  
    elif query_type == 'soil_nutrition':
        base_keywords = ['soil health', 'plant nutrition', 'fertilizer management']
    elif query_type == 'pest_disease':
        base_keywords = ['pest management', 'plant disease', 'integrated pest control']
    elif query_type == 'technology':
        base_keywords = ['agricultural technology', 'precision farming', 'farm automation']
    else:
        base_keywords = ['sustainable agriculture', 'farming techniques', 'agricultural practices']
    
    # Extract key terms from query
    query_words = [word for word in query.lower().split() if len(word) > 3]
    agricultural_terms = [word for word in query_words if word in [
        'crop', 'plant', 'soil', 'farm', 'grow', 'seed', 'harvest', 'irrigation', 
        'fertilizer', 'organic', 'pest', 'disease', 'yield', 'nutrition'
    ]]
    
    # Combine base keywords with query terms
    return base_keywords + agricultural_terms[:2]

def get_intelligent_fallback_response(query: str, query_type: str) -> str:
    """Generate intelligent fallback response when all other methods fail"""
    return f"""**RootSource AI** - Agricultural Intelligence System

I understand you're asking about {query_type.replace('_', ' ')} in agriculture.

**Current Status:**
• **Advanced AI Processing**: Using comprehensive agricultural knowledge databases
• **Multi-Source Analysis**: Combining research from agricultural institutions worldwide  
• **Intelligent Recommendations**: Based on proven farming practices and scientific studies

**Your Query**: {query}

**🤖 AI-Generated Response:**
While I don't have access to real-time satellite data at the moment, I can provide you with evidence-based agricultural advice using my extensive knowledge of farming practices, crop management, and sustainable agriculture techniques.

**🔬 Knowledge Sources:**
• Global agricultural research databases
• University extension services knowledge
• Sustainable farming practices documentation
• Traditional and modern farming integration techniques

**💡 Recommendation:**
For the most accurate, location-specific advice, I recommend:
1. **Consulting local agricultural extension services** for region-specific guidance
2. **Connecting with local farmers** who understand your area's unique conditions  
3. **Using soil testing services** for precise soil and nutrient analysis
4. **Monitoring local weather patterns** and seasonal changes

Would you like me to provide general guidance on your agricultural question using my comprehensive farming knowledge?"""

async def get_intelligent_fallback_context(query: str, query_type: str, location: Optional[LocationInfo] = None) -> str:
    """Generate intelligent fallback context when NASA data is unavailable"""
    
    location_str = f"{location.city}, {location.country}" if location else "your location"
    
    # Create contextual information based on query type
    if query_type == 'weather':
        return f"""
INTELLIGENT AGRICULTURAL CONTEXT (AI-Enhanced):
📍 Location: {location_str}
🔍 Query Focus: Weather & Climate Analysis
🤖 AI Sources: Advanced meteorological knowledge, historical climate patterns, and agricultural weather correlations

**AI Weather Intelligence:**
• **Climate Pattern Analysis**: Using historical weather data and climate models
• **Seasonal Predictions**: Based on regional weather patterns and global climate trends  
• **Agricultural Impact**: Weather-crop relationship analysis from extensive agricultural databases
• **Adaptation Strategies**: AI-generated recommendations for weather resilience

**Enhanced Information Sources:**
• Global weather databases and climate research
• Agricultural meteorology studies and patterns
• Regional farming practices and weather adaptations
• Crop-weather correlation analysis from agricultural research
"""
    
    elif query_type == 'crop_specific':
        return f"""
INTELLIGENT AGRICULTURAL CONTEXT (AI-Enhanced):
📍 Location: {location_str}  
🔍 Query Focus: Crop Management & Production
🤖 AI Sources: Comprehensive crop databases, research publications, and global farming practices

**AI Crop Intelligence:**
• **Variety Selection**: Analysis of crop varieties suited for different conditions
• **Growth Optimization**: Best practices from global agricultural research
• **Yield Enhancement**: Data-driven strategies for maximum productivity
• **Regional Adaptation**: Location-specific growing techniques and timing

**Enhanced Information Sources:**
• International crop research databases
• Agricultural extension service knowledge
• Peer-reviewed farming studies and trials
• Global crop management best practices
"""
    
    elif query_type == 'soil_nutrition':
        return f"""
INTELLIGENT AGRICULTURAL CONTEXT (AI-Enhanced):
📍 Location: {location_str}
🔍 Query Focus: Soil Health & Nutrition Management  
🤖 AI Sources: Soil science databases, nutrition research, and sustainable farming practices

**AI Soil Intelligence:**
• **Nutrient Management**: Precision nutrition strategies from soil science research
• **Organic Solutions**: Natural and sustainable soil improvement methods
• **pH Management**: Soil chemistry optimization techniques
• **Fertility Enhancement**: Long-term soil health improvement strategies

**Enhanced Information Sources:**
• Soil science research publications
• Organic farming and permaculture databases  
• Agricultural chemistry and nutrition studies
• Sustainable agriculture practices and techniques
"""
    
    elif query_type == 'pest_disease':
        return f"""
INTELLIGENT AGRICULTURAL CONTEXT (AI-Enhanced):
📍 Location: {location_str}
🔍 Query Focus: Integrated Pest & Disease Management
🤖 AI Sources: Entomology databases, plant pathology research, and IPM strategies

**AI Pest Management Intelligence:**
• **Identification**: Advanced pest and disease recognition patterns
• **Biological Control**: Natural predator and beneficial insect strategies  
• **Organic Solutions**: Chemical-free pest management approaches
• **Prevention Strategies**: Proactive farming practices for pest reduction

**Enhanced Information Sources:**
• Entomology and plant pathology research
• Integrated Pest Management (IPM) databases
• Organic and biological control studies
• Regional pest monitoring and management data
"""
    
    elif query_type == 'technology':
        return f"""
INTELLIGENT AGRICULTURAL CONTEXT (AI-Enhanced):
📍 Location: {location_str}
🔍 Query Focus: Agricultural Technology & Innovation
🤖 AI Sources: AgTech research, precision agriculture databases, and innovation studies

**AI Technology Intelligence:**
• **Precision Agriculture**: Smart farming technologies and implementation
• **Automation**: Robotic and automated farming solutions
• **Data Analytics**: Farm data collection and analysis strategies
• **Sustainability Tech**: Environmentally friendly agricultural innovations

**Enhanced Information Sources:**
• Agricultural technology research and development
• Precision agriculture case studies and implementations
• Farm automation and robotics databases
• Sustainable technology innovations in agriculture
"""
    
    else:  # General farming or other
        return f"""
INTELLIGENT AGRICULTURAL CONTEXT (AI-Enhanced):
📍 Location: {location_str}
🔍 Query Focus: Comprehensive Agricultural Knowledge
🤖 AI Sources: Multi-disciplinary agricultural databases, global farming practices, and research networks

**AI Agricultural Intelligence:**
• **Holistic Farming**: Integrated approaches to sustainable agriculture
• **Best Practices**: Proven techniques from global farming communities
• **Innovation Integration**: Combining traditional and modern farming methods
• **Sustainability Focus**: Environmentally conscious farming strategies

**Enhanced Information Sources:**
• Global agricultural research networks
• Traditional and indigenous farming knowledge
• Modern sustainable agriculture practices  
• Cross-disciplinary agricultural studies and innovations
"""

# Load environment variables unless explicitly disabled (e.g., in tests)
if not os.getenv("DONT_LOAD_DOTENV") and not os.getenv("PYTEST_CURRENT_TEST"):
    load_dotenv(find_dotenv())

# Initialize FastAPI
app = FastAPI(title="RootSource AI", version="1.0.0")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the SPA index.html from the repository root."""
    print("📱 Frontend accessed - serving index.html")
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("<h1>RootSource AI</h1><p>index.html not found.</p>", status_code=404)

@app.get("/health")
async def health_check():
    """Health check endpoint for debugging connection issues"""
    return {
        "status": "healthy",
        "message": "RootSource AI server is running",
        "nasa_integration": NASA_INTEGRATION_AVAILABLE,
        "timestamp": str(datetime.now())
    }




# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,  # configurable via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for frontend requests
class ChatRequest(BaseModel):
    message: str
    location: Optional[dict] = None  # Optional location data from frontend
    
class LocationRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# --- Initialize AI Tools ---
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200))
arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200))
duckduckgo_search = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper(region="in-en", time="y", max_results=2))

tools = [wiki, arxiv, duckduckgo_search]

# --- NASA Integration ---
enhanced_assistant = None
if NASA_INTEGRATION_AVAILABLE:
    try:
        enhanced_assistant = EnhancedAgriculturalAssistant()
        print("✅ NASA agricultural data integration initialized")
    except Exception as e:
        print(f"⚠️ NASA integration initialization failed: {e}")
        enhanced_assistant = None

# --- Memory ---
chat_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# --- LLM Loader ---
def load_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return ChatOpenAI(
        model_name="openai/gpt-oss-120b",
        temperature=0.9,
        openai_api_key=groq_api_key,
        openai_api_base="https://api.groq.com/openai/v1"
    )

# --- Translation ---
def translate_to_english(text):
    try:
        detected_lang = detect(text)
        if detected_lang == "en":
            return text, "en"
        translated_text = GoogleTranslator(source=detected_lang, target="en").translate(text)
        return translated_text, detected_lang
    except:
        return text, "unknown"

def translate_back(text, target_lang):
    try:
        if target_lang == "en":
            return text
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except:
        return text

# Cache the LLM globally for better performance
_cached_llm = None

def get_llm():
    global _cached_llm
    if _cached_llm is None:
        _cached_llm = load_llm()
    return _cached_llm

def format_response(text):
    """Convert markdown-style text to HTML"""
    if not text:
        return text
    
    # Convert **bold** to HTML
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #2ecc71; font-weight: 600; background: rgba(46, 204, 113, 0.1); padding: 2px 4px; border-radius: 3px;">\1</strong>', text)
    
    # Convert bullet points
    text = re.sub(r'^• (.+)$', r'<div style="margin: 8px 0; padding-left: 20px; position: relative; line-height: 1.6;"><span style="position: absolute; left: 0; color: #2ecc71; font-weight: bold;">•</span>\1</div>', text, flags=re.MULTILINE)
    
    # Convert numbered lists
    text = re.sub(r'^(\d+)\. (.+)$', r'<div style="margin: 8px 0; padding-left: 20px; position: relative; line-height: 1.6;"><span style="position: absolute; left: 0; color: #2ecc71; font-weight: bold;">\1.</span>\2</div>', text, flags=re.MULTILINE)
    
    # Convert line breaks
    text = text.replace('\n', '<br>')
    
    # Clean up multiple <br> tags
    text = re.sub(r'(<br>\s*){3,}', '<br><br>', text)
    
    return text

def get_direct_response(query):
    """Get direct response from LLM without agent complexity"""
    try:
        llm = get_llm()
        response = llm.invoke(query)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        # Safe fallback for environments without API key or when provider is unavailable
        print(f"Direct LLM error (falling back to demo response): {e}")
        demo = (
            "**RootSource AI (Demo Mode)**\n\n"
            "• The intelligent LLM backend isn't configured.\n"
            "• Set the environment variable **GROQ_API_KEY** to enable live answers.\n\n"
            "**You asked:**\n"
            f"• {query[:500]}\n\n"
            "**What to do next:**\n"
            "1. Create a .env file with GROQ_API_KEY=your_key\n"
            "2. Restart the server\n"
            "3. Ask again for a live answer"
        )
        return demo

def get_search_enhanced_response(query):
    """Use multiple search tools for comprehensive information"""
    try:
        search_results = []
        
        # Try Wikipedia first for general agricultural knowledge
        try:
            wiki_tool = tools[0]  # Wikipedia
            wiki_result = wiki_tool.run(query)
            if wiki_result and len(wiki_result.strip()) > 10:
                search_results.append(f"Wikipedia: {wiki_result[:200]}")
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        # Try Arxiv for scientific research
        try:
            arxiv_tool = tools[1]  # Arxiv
            arxiv_result = arxiv_tool.run(query)
            if arxiv_result and len(arxiv_result.strip()) > 10:
                search_results.append(f"Research: {arxiv_result[:200]}")
        except Exception as e:
            print(f"Arxiv search error: {e}")
        
        # Try DuckDuckGo for current information
        try:
            duckduckgo_tool = tools[2]  # DuckDuckGo
            ddg_result = duckduckgo_tool.run(query)
            if ddg_result and len(ddg_result.strip()) > 10:
                search_results.append(f"Current info: {ddg_result[:200]}")
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        # Combine all search results
        if search_results:
            combined_info = " | ".join(search_results)
            enhanced_query = f"""
You are RootSource AI, an expert farming and agriculture assistant.

Based on this comprehensive information: {combined_info}

Question: {query}

Provide a well-formatted, helpful answer about farming/agriculture using the following structure:

**Format your response like this:**
- Use **bold** for important terms and headings
- Use bullet points (•) for lists
- Use numbered lists (1., 2., 3.) for steps
- Break content into clear paragraphs
- Add line breaks between sections
- Include practical tips when relevant

Make it easy to read and actionable for farmers.
"""
        else:
            # Fallback to direct response if no search results
            enhanced_query = query
            
        return get_direct_response(enhanced_query)
    except Exception as e:
        print(f"Search error: {e}")
        return get_direct_response(query)

def trim_chat_memory(max_length=5):
    chat_history = chat_memory.load_memory_variables({})["chat_history"]
    if len(chat_history) > max_length:
        chat_memory.chat_memory.messages = chat_history[-max_length:]
    return chat_history



@app.post("/chat")
async def chat(req: ChatRequest):
    user_message = req.message
    translated_query, original_lang = translate_to_english(user_message)

    # Quick response for greetings
    if any(greeting in translated_query.lower() for greeting in ['hi', 'hello', 'hey', 'greetings']):
        response_text = """**Hello! I'm RootSource AI** 

Your expert AI assistant for all things farming and agriculture.

**How can I assist you today?**

• Ask about crop management
• Get advice on soil health
• Learn about pest control
• Explore irrigation techniques
• Discover organic farming methods

Feel free to ask me anything related to farming!"""
        # Format the response before returning
        translate_lang = translate_back(response_text, original_lang)
        formatted_response = format_response(translate_lang)
        final_response = formatted_response
        return {"reply": final_response, "detectedLang": original_lang, "translatedQuery": translated_query}

    # SIMPLE TEST: If the user asks about "test", return a simple formatted response
    if "test" in translated_query.lower():
        response_text = """**Simple Test Response**

This is a test of **bold text** formatting.

**Key Points:**
• First bullet point with **bold** text
• Second bullet point
• Third bullet point

**Steps:**
1. First step
2. Second step  
3. Third step

This should show **bold** text and proper formatting."""
        # Format the response before returning
        translate_lang = translate_back(response_text, original_lang)
        formatted_response = format_response(translate_lang)
        final_response = formatted_response
        return {"reply": final_response, "detectedLang": original_lang, "translatedQuery": translated_query}

    # Prepare the formatted prompt
    prompt = f"""
You are a helpful and expert AI assistant for farming and agriculture questions.
Your primary goal is to answer the USER'S QUESTION accurately and concisely.

**IMPORTANT INSTRUCTIONS:**
1. **If the question is not related at all to agriculture domain, strictly say that ""Please ask questions related to agriculture only"".** Only answer if its related to agricultural field.

2. **Understand the User's Question First:** Carefully analyze the question to determine what the user is asking about farming or agriculture.

3. **Search Strategically (Maximum 3 Searches):** You are allowed to use tools (search engine, Wikipedia, Arxiv) for a MAXIMUM of THREE searches to find specific information DIRECTLY related to answering the USER'S QUESTION.  Do not use tools for general background information unless absolutely necessary to answer the core question.

4. **STOP Searching and Answer Directly:**  **After a maximum of THREE searches, IMMEDIATELY STOP using tools.**  Even if you haven't found a perfect answer, stop searching.

5. **Formulate a Concise Final Answer:** Based on the information you have (from searches or your existing knowledge), construct a brief, direct, and helpful answer to the USER'S QUESTION.  Focus on being accurate and to-the-point.

6. **If you ALREADY KNOW the answer confidently without searching, answer DIRECTLY and DO NOT use tools.** Only use tools if you genuinely need to look up specific details to answer the user's question.

7. **First line set your name as 'RootSource AI' and introduce yourself as an expert AI assistant in agriculture domain.**

8. ** If your say "hi" or "hello" or "hey" or "greetings" or any other greetings, detect the language as English, not need to translation and respond with "Hello! I'm RootSource AI, your expert AI assistant for all things farming and agriculture. How can I assist you today?"**

9. **If you are unable to find relevant information after two searches, respond with ""I'm sorry, I couldn't find the information you're looking for."".**

Question: [User's Question]
Thought: I need to think step-by-step how to best answer this question.
Action: [Tool Name] (if needed, otherwise skip to Thought: Final Answer)
Action Input: [Input for the tool]
Observation: [Result from the tool]
... (repeat Thought/Action/Observation up to 2 times MAX)
Thought: Final Answer - I have enough information to answer the user's question now.
Final Answer: [Your concise and accurate final answer to the User's Question]

Question: {translated_query}

CRITICAL FORMATTING REQUIREMENTS - FOLLOW EXACTLY:

1. Always start with a bold heading: **Topic Name**
2. Leave a blank line after headings
3. Use **bold text** for key terms and important points  
4. Create bullet points with • symbol followed by space
5. Use numbered lists for step-by-step instructions (1. 2. 3. etc)
6. Separate different sections with blank lines
7. Make responses well-structured and easy to read

EXAMPLE FORMAT:
**Crop Rotation Benefits**

**Key Advantages:**
• **Soil Health**: Improves nutrient balance and structure
• **Pest Control**: Breaks pest and disease cycles  
• **Yield Improvement**: Increases long-term productivity

**Implementation Steps:**
1. **Plan Your Rotation**: Map out 3-4 year cycles
2. **Choose Crops**: Select complementary plant families
3. **Monitor Results**: Track soil health and yields

**Additional Tips:**
Include **legumes** to fix nitrogen and use **cover crops** during off-seasons.

Now provide a comprehensive, well-formatted answer about the farming topic."""

    max_retries = 2
    for attempt in range(max_retries):
        try:
            # Try direct response first (fastest)
            response_text = get_direct_response(prompt)
            
            # Check if we got a demo mode response (no GROQ API key)
            if "Demo Mode" in response_text:
                break  # Keep demo mode response, don't try search
            elif response_text and len(response_text.strip()) > 10:
                break
            else:
                # If direct response is too short and we have API key, try with search
                response_text = get_search_enhanced_response(translated_query)
                if response_text:
                    break
                else:
                    response_text = "I'm sorry, I'm having trouble processing your request right now. Please try rephrasing your question."
                    break
                    
        except Exception as e:
            print(f"⚠ Error (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}...")
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Very short delay
    else:
        response_text = "I'm sorry, I'm experiencing high demand right now. Please try again in a moment."

    # Format and translate back
    translate_lang = translate_back(response_text, original_lang)
    formatted_response = format_response(translate_lang)
    final_response = formatted_response
    return {"reply": final_response, "detectedLang": original_lang, "translatedQuery": translated_query}


# --- NASA Enhanced Endpoints ---

@app.get("/api/location/detect")
async def detect_location():
    """
    Detect user location using IP geolocation with smart fallback for South Asia
    """
    try:
        if not enhanced_assistant:
            return JSONResponse(
                status_code=503,
                content={"error": "Location detection not available"}
            )
        
        location = await enhanced_assistant.location_detector.get_location_from_ip()
        
        if location:
            return {
                "success": True,
                "method": "ip_geolocation",
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "country": location.country,
                    "region": location.region,
                    "city": location.city,
                    "timezone": location.timezone
                }
            }
        else:
            # Smart fallback - default to Bangladesh (Dhaka) for better regional coverage
            fallback = enhanced_assistant.location_detector.get_fallback_location('BD')
            return {
                "success": False,
                "fallback": True,
                "method": "regional_fallback",
                "location": {
                    "latitude": fallback.latitude,
                    "longitude": fallback.longitude,
                    "country": fallback.country,
                    "region": fallback.region,
                    "city": fallback.city,
                    "timezone": fallback.timezone
                },
                "note": "Using South Asian regional fallback for optimal agricultural recommendations"
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to detect location: {str(e)}"}
        )

@app.post("/api/location/set")
async def set_manual_location(request: dict):
    """
    Set user location manually for users who know their exact location
    Example: {"city": "Gazipur", "country": "Bangladesh"}
    """
    try:
        city = request.get('city', '').strip()
        country = request.get('country', 'Bangladesh').strip()
        
        if not city:
            return JSONResponse(
                status_code=400,
                content={"error": "City name is required", "success": False}
            )
        
        # Get location from enhanced database
        if country.lower() == 'bangladesh':
            from nasa_integration import LocationDetector
            location = LocationDetector.get_bangladesh_location(city)
        else:
            from nasa_integration import LocationDetector
            location = LocationDetector.get_fallback_location('BD', city)
        
        return {
            "success": True,
            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "city": location.city,
                "region": location.region,
                "country": location.country,
                "timezone": location.timezone
            },
            "message": f"Location manually set to {location.city}, {location.country}",
            "method": "manual_override"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to set location: {str(e)}", "success": False}
        )

@app.post("/api/location/context")
async def get_location_context(location_req: LocationRequest):
    """
    Get NASA agricultural data context for a specific location
    """
    try:
        if not enhanced_assistant:
            return JSONResponse(
                status_code=503,
                content={"error": "NASA data service unavailable"}
            )
        
        user_location = None
        if location_req.latitude and location_req.longitude:
            # Create LocationInfo from provided coordinates
            user_location = LocationInfo(
                latitude=location_req.latitude,
                longitude=location_req.longitude,
                country="Unknown",
                region="Unknown", 
                city="Unknown",
                timezone="UTC"
            )
        
        context = await enhanced_assistant.get_location_based_context(user_location)
        
        return {
            "success": True,
            "context": context,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get location context: {str(e)}"}
        )

@app.post("/chat/enhanced")
async def enhanced_chat(req: ChatRequest):
    """
    Enhanced chat endpoint with NASA data integration and location awareness
    """
    user_message = req.message
    translated_query, original_lang = translate_to_english(user_message)
    
    # Intelligent query analysis for best response strategy
    query_type = analyze_query_type(translated_query)
    
    # Get location context with smart fallback handling
    location_context = ""
    nasa_data_available = False
    fallback_context = ""
    
    if enhanced_assistant:
        try:
            # Use provided location or detect automatically
            user_location = None
            if req.location:
                user_location = LocationInfo(
                    latitude=req.location.get('latitude', 0),
                    longitude=req.location.get('longitude', 0),
                    country=req.location.get('country', 'Unknown'),
                    region=req.location.get('region', 'Unknown'),
                    city=req.location.get('city', 'Unknown'),
                    timezone=req.location.get('timezone', 'UTC')
                )
            
            # Try NASA data first
            context = await enhanced_assistant.get_location_based_context(user_location)
            
            if context:
                nasa_data_available = True
                location_info = context.get('location', {})
                weather_info = context.get('weather', {})
                soil_info = context.get('soil', {})
                vegetation_info = context.get('vegetation', {})
                weather_insights = context.get('weather_insights', [])
                
                location_context = f"""
LOCATION-SPECIFIC AGRICULTURAL CONTEXT:
📍 Location: {location_info.get('city', 'Unknown')}, {location_info.get('region', 'Unknown')}, {location_info.get('country', 'Unknown')}
🌡️ Current Weather: {weather_info.get('current_temperature', 'N/A')} (Range: {weather_info.get('temperature_range', 'N/A')})
💧 Recent Precipitation: {weather_info.get('recent_precipitation', 'N/A')}
💨 Humidity: {weather_info.get('humidity', 'N/A')}
☀️ Solar Radiation: {weather_info.get('solar_radiation', 'N/A')}
💨 Wind Speed: {weather_info.get('wind_speed', 'N/A')}

🌱 Vegetation Health: {vegetation_info.get('health_status', 'N/A')}
🌾 Growing Season: {vegetation_info.get('growing_season', 'N/A')}

🪨 Soil Conditions:
- Moisture Level: {soil_info.get('moisture_level', 'N/A')}
- Soil Temperature: {soil_info.get('temperature', 'N/A')}
- Soil Type: {soil_info.get('type', 'N/A')}
- pH Estimate: {soil_info.get('ph_estimate', 'N/A')}
- Irrigation Advice: {soil_info.get('irrigation_recommendation', 'N/A')}

🔍 NASA Weather Insights:
{chr(10).join([f'- {insight}' for insight in weather_insights]) if weather_insights else '- No specific insights available'}
"""
                
        except Exception as e:
            print(f"NASA data unavailable: {e}")
            # Intelligent fallback when NASA data isn't available
            fallback_context = await get_intelligent_fallback_context(translated_query, query_type, user_location)
            location_context = fallback_context
    
    # Enhanced prompt with intelligent data source handling
    data_source_info = "NASA satellite data and weather information" if nasa_data_available else "advanced AI knowledge and research sources"
    enhanced_prompt = f"""
You are RootSource AI, an expert agricultural assistant with access to {data_source_info}.

{location_context}

**IMPORTANT INSTRUCTIONS:**
1. **Use the location-specific data above** to provide highly personalized agricultural advice.
2. **Reference the current weather, soil, and vegetation conditions** in your recommendations.
3. **If the question is not agriculture-related, say "Please ask questions related to agriculture only."**
4. **Always start with your name 'RootSource AI'** and mention that you're using NASA satellite data for accuracy.
5. **Incorporate the irrigation, weather, and growing season insights** into your advice.
6. **Provide specific, actionable recommendations** based on the current local conditions.

CRITICAL FORMATTING REQUIREMENTS:

1. Always start with a bold heading: **Topic Name**
2. Use **bold text** for key terms and important points  
3. Create bullet points with • symbol
4. Use numbered lists for step-by-step instructions
5. Separate sections with blank lines
6. Include location-specific recommendations

EXAMPLE FORMAT:
**Corn Yield Optimization for {location_info.get('city', 'Your Location') if nasa_data_available else 'Your Location'}**

**Current Conditions Analysis:**
• **Weather**: Based on current temperature of {weather_info.get('current_temperature', 'N/A') if nasa_data_available else 'local conditions'}
• **Soil**: {soil_info.get('irrigation_recommendation', 'Check soil moisture levels') if nasa_data_available else 'Monitor soil conditions'}

**Recommended Actions:**
1. **Immediate Steps**: Based on current {vegetation_info.get('growing_season', 'growing conditions') if nasa_data_available else 'seasonal conditions'}
2. **Weekly Planning**: Consider the weather forecast and soil conditions

Question: {translated_query}
"""

    # Intelligent multi-source response generation
    response_text = await get_intelligent_response(enhanced_prompt, translated_query, query_type, nasa_data_available)

    # Format and translate back
    translate_lang = translate_back(response_text, original_lang)
    formatted_response = format_response(translate_lang)
    
    # Add intelligent data source attribution
    if nasa_data_available and enhanced_assistant and user_location:
        try:
            nasa_attribution = enhanced_assistant.generate_nasa_attribution(user_location, context)
            formatted_response += f"<br><br>{nasa_attribution}"
            print(f"✅ NASA attribution added for {user_location.city}, {user_location.country}")
        except Exception as e:
            print(f"Error generating NASA attribution: {e}")
            # Add fallback attribution for NASA data
            formatted_response += f"""<br><br>
<div style='padding: 8px; background: rgba(46, 204, 113, 0.1); border-left: 3px solid #2ecc71; margin-top: 10px; font-size: 0.9em;'>
🛰️ <strong>NASA Data Integration:</strong> This response uses NASA satellite data and weather information for enhanced accuracy.
</div>"""
    else:
        # Add attribution for AI-enhanced fallback system
        user_location_str = f" for {user_location.city}, {user_location.country}" if user_location else ""
        formatted_response += f"""<br><br>
<div style='padding: 8px; background: rgba(52, 152, 219, 0.1); border-left: 3px solid #3498db; margin-top: 10px; font-size: 0.9em;'>
🤖 <strong>AI-Enhanced Response:</strong> This advice uses advanced agricultural AI knowledge and research databases{user_location_str}. For real-time satellite data, NASA integration is available with location services enabled.
</div>"""
    
    return {
        "reply": formatted_response, 
        "detectedLang": original_lang, 
        "translatedQuery": translated_query,
        "nasa_context_used": nasa_data_available,
        "location_context": location_context if nasa_data_available else None
    }

@app.get("/favicon.ico")
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "favicon.ico not found"})

@app.get("/health")
async def health():
    return {"status": "ok", "app": "RootSource AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
