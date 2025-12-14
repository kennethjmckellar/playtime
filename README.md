# Sports Research AI Agent

This project builds an AI agent that researches and identifies youth sports programs in the USA, then updates and maintains a CSV file with comprehensive information about each program. It ensures data completeness and consistent formatting across all columns.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file with `OPENAI_API_KEY=your_key_here`
3. Run: `python main.py`

## Usage
- The agent researches youth sports programs across the USA using OpenAI.
- Data is stored in `data/programs.csv` with all required columns from the starter file.
- The agent validates data for completeness (required fields present) and format consistency (all columns filled, data types consistent).

## CSV Schema
The `programs.csv` file includes all columns from the starter file. **Required fields** (must be provided and not 'Unknown'): program_id, organization_name, program_name, contact_name, address_street, address_city, address_state, address_zip, county, metro_area, phone, email, sport_type. Additionally, either website or at least one social media link (Facebook or Instagram) must be provided.

All columns: program_id, organization_name, organization_type, sport_type, program_name, program_type, skill_level, address_street, address_city, address_state, address_zip, county, metro_area, latitude, longitude, phone, email, contact_name, director_name, website, social_media_facebook, social_media_instagram, age_min, age_max, age_groups, gender, team_based, season, registration_fee, monthly_fee, annual_fee, scholarship_available, scholarship_percentage, equipment_provided, transportation_provided, reviews_text, average_rating, review_count, verified, data_source, last_verified, notes, keywords_long_tail, facility_type, facility_amenities, coaches_available, certifications, parent_involvement

## Features
- AI-powered research for structured program data extraction, ensuring all required fields (address, name, contact info, and website/social media) are provided
- **Automatic info completion**: If initial AI research misses required details, the agent makes follow-up queries to fill missing information via internet research
- CSV storage matching the provided starter file schema
- Data validation to ensure every column is handled, data is complete (required fields present), and formatted consistently
