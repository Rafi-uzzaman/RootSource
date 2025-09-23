#  RootSource AI

<div align="center">

![RootSource AI Logo](assets/logo.png)

**Your Expert AI Assistant for Farming & Agriculture**

</div>

**RootSource AI** is a sophisticated, multilingual agricultural assistant designed to provide farmers, researchers, and enthusiasts with expert-level advice and real-time information. By integrating a powerful AI engine with a multi-source research system and a seamless voice interface, RootSource AI delivers accurate, context-aware answers to all your farming questions.

---

## ✨ Key Features

- **🤖 Advanced AI Engine**: Powered by a high-performance LLM (Groq LLaMA 3.1 8B) for fast, intelligent, and context-aware responses.
- **🔍 Multi-Source Research**: Gathers and cross-references information from **Wikipedia**, **ArXiv**, and **DuckDuckGo** to provide comprehensive and verified answers.
- **🌐 Global Accessibility**: 
  - **Automatic Language Detection**: Understands questions in over 40 languages.
  - **Real-time Translation**: Delivers answers in your preferred language.
  - **Priority Language Support**: Enhanced for English, Bengali, Hindi, and Urdu.
- **🎤 Hands-Free Voice Interface**: 
  - **Full Voice Control**: Ask questions and hear responses read aloud.
  - **Smart Voice Detection**: Automatically activates for voice-initiated conversations.
  - **Visual Feedback**: On-screen indicators for speaking and processing states.
  - **Stop Control**: Instantly interrupt the AI's voice response.
- **💻 Modern & Responsive UI**: A clean, mobile-first single-page application (SPA) that works on any device.
- **🚀 Production-Ready**: Built with a high-performance **FastAPI** backend, containerized with **Docker**, and includes a full CI/CD pipeline.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- An optional **Groq API Key** for full AI functionality (the app runs in a limited demo mode without it).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Rafi-uzzaman/RootSource.git
    cd RootSource
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment:**
    Create a `.env` file from the example and add your API key:
    ```bash
    cp .env.example .env
    # Now, edit the .env file
    ```

5.  **Run the application:**
    ```bash
    uvicorn backend:app --reload
    ```
    The application will be available at `http://localhost:8000`.

---

## 🛠️ Development & Architecture

RootSource AI is built with a modern, robust technology stack designed for performance and scalability.

### Tech Stack

| Component         | Technology                               | Purpose                                             |
| ----------------- | ---------------------------------------- | --------------------------------------------------- |
| **Backend**       | FastAPI, Python 3.11+                    | High-performance, asynchronous API server           |
| **AI Engine**     | LangChain, Groq LLaMA 3.1 8B             | Core AI logic, context management, and processing   |
| **Data Sources**  | Wikipedia, ArXiv, DuckDuckGo             | Real-time, multi-source information retrieval       |
| **Frontend**      | Vanilla JavaScript, HTML5, CSS3          | Responsive, framework-free user interface           |
| **Voice**         | Web Speech API                           | Browser-native speech recognition and synthesis     |
| **Container**     | Docker                                   | Easy deployment and environment consistency         |
| **CI/CD**         | GitHub Actions                           | Automated testing and quality checks                |

### Project Structure

```
RootSource/
├── 📁 assets/         # Frontend static files (JS, CSS, images)
├── 📁 tests/         # Backend test suite
├── 🐍 backend.py      # Main FastAPI application logic
├── 🌐 index.html      # Single-page application entry point
├── 📋 requirements.txt  # Python dependencies
├── 🐳 Dockerfile     # Docker container definition
└── 📖 README.md      # This file
```

---

## 🤝 Contributing

Contributions are welcome! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is appreciated. Please fork the repository and submit a pull request.

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

<div align="center">
    <p><strong>Developed with ❤️ by Team BlueDot</strong></p>
    <p><em>Empowering the world's farmers with the power of AI.</em></p>
</div>
