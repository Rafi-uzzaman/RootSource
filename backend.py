import os
import re
import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, WikipediaAPIWrapper, ArxivAPIWrapper
from langdetect import detect
from deep_translator import GoogleTranslator
from dotenv import load_dotenv, find_dotenv
from settings import ALLOW_ORIGINS, HOST, PORT
from starlette.responses import JSONResponse

# Load environment variables unless explicitly disabled (e.g., in tests)
if not os.getenv("DONT_LOAD_DOTENV") and not os.getenv("PYTEST_CURRENT_TEST"):
    load_dotenv(find_dotenv())

# Initialize FastAPI
app = FastAPI(title="RootSource AI", version="1.0.0")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the SPA index.html from the repository root."""
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("<h1>RootSource AI</h1><p>index.html not found.</p>", status_code=404)




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

# --- Initialize AI Tools ---
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200))
arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200))
duckduckgo_search = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper(region="in-en", time="y", max_results=2))

tools = [wiki, arxiv, duckduckgo_search]

# --- Memory ---
chat_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# --- LLM Loader ---
def load_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return ChatOpenAI(
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
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
        response_text = """**Hello! I'm RootSource AI** 🌾

Your expert AI assistant for all things farming and agriculture.

**How can I assist you today?**

• Ask about crop management
• Get advice on soil health
• Learn about pest control
• Explore irrigation techniques
• Discover organic farming methods

Feel free to ask me anything related to farming!"""
        # Format the response before returning
        formatted_response = format_response(response_text)
        final_response = translate_back(formatted_response, original_lang)
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
        formatted_response = format_response(response_text)
        final_response = translate_back(formatted_response, original_lang)
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
    formatted_response = format_response(response_text)
    final_response = translate_back(formatted_response, original_lang)
    return {"reply": final_response, "detectedLang": original_lang, "translatedQuery": translated_query}



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
