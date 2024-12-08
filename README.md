# Tourist Information Chatbot

## Project Overview
This project is a **Tourist Information Chatbot** designed to assist users in finding tourist attractions, hotels, restaurants, and transportation in various locations. The chatbot provides personalized recommendations based on the user's preferences, such as location and budget.

---

## Features
- **Location-based recommendations**: Provides tourist attraction information based on user input.
- **Accommodation suggestions**: Suggests hotels based on the user's location and budget.
- **Restaurant suggestions**: Recommends restaurants in proximity to the tourist locations.
- **Transportation options**: Guides users on available transport services to the chosen destinations.
  
---

## Technologies Used
- **Rasa**: Open-source conversational AI platform for building and deploying the chatbot.
- **Python**: Backend language for logic handling.
- **NLP**: Natural Language Processing to understand user inputs.
- **RAG**: Retrieval Augmented Generation
  
---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/luan-hillne/tourist_RASA.git
2. **Install dependencies**:
   ```bash
   pip install rasa
   pip install groq
   pip install fastapi
3. **Start chatbot**:
   ```
   rasa run actions
   rasa run --enable-api
   python server.py
4. **Test chat**:
   Run ports: 0.0.0.0:8080/docs
   
