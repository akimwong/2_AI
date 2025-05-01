# Automated Job Application System

## Project Structure

```
JobAutoApply/
├── agents/
│ ├── agent1_download.py # Downloads and filters job postings
│ ├── agent2_advanced.py # Semantic filtering against profile
│ └── agent3_profile.py # CV generation engine
├── stages/
│ ├── download_offers.py # LinkedIn/Gmail integration
│ ├── initial_filter.py # Location/keyword filtering
│ ├── advanced_filter.py # TF-IDF similarity scoring
│ └── cv_generator.py # RAG-based CV customization
├── utils/
│ ├── email_utils.py # Gmail API handler
│ ├── linkedin_utils.py # Selenium LinkedIn scraper
│ ├── profile_manager.py # Pinecone vector storage
│ └── initial_filter_keywords.py # Keyword lists
├── profile_eng.json # English professional profile
├── profile_esp.json # Spanish professional profile
├── main.py # Orchestration script
├── token.json # Token for access to LinkedIn
├── credentials.json # API keys
└── requirements.txt # Python dependencies
```

## Core Functionality

### 1. Intelligent Job Collection
- Monitors Gmail for LinkedIn job alerts
- Extracts and normalizes job posting URLs
- Scrapes complete job details using Selenium

### 2. Two-Stage Filtering System
**Initial Filter:**
- Hard filters by location (Madrid/EU)
- Keyword-based title screening
- Language detection (English/Spanish)

**Advanced Filter:**
- Semantic matching using TF-IDF vectors
- Compares job descriptions against:
  - Technical skills (Data/Telecom)
  - Professional experience
  - Role preferences
- Cosine similarity threshold: 0.55

### 3. Smart CV Generation
- Dynamic profile selection (English/Spanish)
- Keyword extraction from job descriptions <- LLM
- Category detection (Data vs Telecom roles) <- LLM
- Context-aware resume building:   <- LLM
  - Highlights relevant skills
  - Omits non-matching requirements
  - Formats for ATS compatibility

## Technical Highlights

- **Multi-LLM Support**: OpenAI, Claude, and DeepSeek integration
- **Vectorized Profiles**: Pinecone storage for semantic retrieval
- **Bilingual Operation**: Parallel English/Spanish processing
- **Modular Agents**: LangGraph-ready architecture

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
