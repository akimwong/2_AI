# Automated Job Application System

## Project Structure

'''
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
├── profiles/
│ ├── profile_eng.json # English professional profile
│ └── profile_esp.json # Spanish professional profile
├── main.py # Orchestration script
└── requirements.txt # Python dependencies
'''
