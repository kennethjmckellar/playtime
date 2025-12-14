from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from config.config import OPENAI_API_KEY

class SportsResearchAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def research_sports_programs(self, query):
        # Use AI to research programs city by city, state by state
        programs = []
        
        # Extract sport from query
        sport = self.extract_sport(query)
        
        # List of major cities and states to research
        locations = [
            ('Los Angeles', 'California'),
            ('San Francisco', 'California'),
            ('San Diego', 'California'),
            ('Houston', 'Texas'),
            ('Dallas', 'Texas'),
            ('Austin', 'Texas'),
            ('Miami', 'Florida'),
            ('Orlando', 'Florida'),
            ('Tampa', 'Florida'),
            ('New York City', 'New York'),
            ('Buffalo', 'New York'),
            ('Albany', 'New York'),
            ('Chicago', 'Illinois'),
            ('Springfield', 'Illinois'),
            ('Peoria', 'Illinois'),
            ('Philadelphia', 'Pennsylvania'),
            ('Pittsburgh', 'Pennsylvania'),
            ('Harrisburg', 'Pennsylvania'),
        ]
        
        info = ''
        for city, state in locations:
            prompt = f"Research youth {sport} programs in {city}, {state}. Provide detailed information for up to 2 programs. Return in this exact format for each program on a new line: Program: [Program Name], Organization: [Organization Name], Organization Type: [Type], Sport: [Sport], Program Type: [Type], Skill Level: [Level], Address Street: [Street], Address City: [City], Address State: [State], Address Zip: [Zip], County: [County], Metro Area: [Metro], Phone: [Phone], Email: [Email], Contact Name: [Contact], Website: [Website], Social Media Facebook: [FB], Social Media Instagram: [IG], Age Min: [Min], Age Max: [Max], Season: [Season], Registration Fee: [Fee], Notes: [Notes]"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            
            program_info = response.choices[0].message.content
            info += program_info + '\n'
        
        return info
    
    def extract_sport(self, query):
        query_lower = query.lower()
        if 'baseball' in query_lower:
            return 'baseball'
        elif 'soccer' in query_lower:
            return 'soccer'
        elif 'basketball' in query_lower:
            return 'basketball'
        else:
            return 'sports'

    def fill_missing_info(self, program_data):
        # Since we're using scraping, fill missing with defaults instead of AI
        defaults = {
            'organization_type': 'Nonprofit Organization',
            'program_type': 'League',
            'skill_level': 'all_levels',
            'county': 'Unknown',
            'metro_area': 'Unknown',
            'contact_name': 'Contact Person',
            'social_media_facebook': 'Unknown',
            'social_media_instagram': 'Unknown',
            'age_min': '5',
            'age_max': '18',
            'season': 'Year-round',
            'registration_fee': 'Varies',
            'notes': 'Scraped from website',
            'verified': 'No',
            'data_source': 'Web Scraping'
        }
        for key, default in defaults.items():
            if key not in program_data or not program_data[key] or program_data[key] == 'Unknown':
                program_data[key] = default
        return program_data

    def update_database(self, handler, info):
        lines = info.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Program:'):
                parts = [p.strip() for p in line.split(',')]
                program_name = parts[0].replace('Program:', '').strip()
                organization_name = next((p.replace('Organization:', '').strip() for p in parts if p.startswith('Organization:')), '')
                organization_type = next((p.replace('Organization Type:', '').strip() for p in parts if p.startswith('Organization Type:')), '')
                sport_type = next((p.replace('Sport:', '').strip() for p in parts if p.startswith('Sport:')), '')
                program_type = next((p.replace('Program Type:', '').strip() for p in parts if p.startswith('Program Type:')), '')
                skill_level = next((p.replace('Skill Level:', '').strip() for p in parts if p.startswith('Skill Level:')), 'all_levels')
                address_street = next((p.replace('Address Street:', '').strip() for p in parts if p.startswith('Address Street:')), '')
                address_city = next((p.replace('Address City:', '').strip() for p in parts if p.startswith('Address City:')), '')
                address_state = next((p.replace('Address State:', '').strip() for p in parts if p.startswith('Address State:')), '')
                address_zip = next((p.replace('Address Zip:', '').strip() for p in parts if p.startswith('Address Zip:')), '')
                county = next((p.replace('County:', '').strip() for p in parts if p.startswith('County:')), '')
                metro_area = next((p.replace('Metro Area:', '').strip() for p in parts if p.startswith('Metro Area:')), '')
                phone = next((p.replace('Phone:', '').strip() for p in parts if p.startswith('Phone:')), '')
                email = next((p.replace('Email:', '').strip() for p in parts if p.startswith('Email:')), '')
                contact_name = next((p.replace('Contact Name:', '').strip() for p in parts if p.startswith('Contact Name:')), '')
                website = next((p.replace('Website:', '').strip() for p in parts if p.startswith('Website:')), '')
                social_media_facebook = next((p.replace('Social Media Facebook:', '').strip() for p in parts if p.startswith('Social Media Facebook:')), 'Unknown')
                social_media_instagram = next((p.replace('Social Media Instagram:', '').strip() for p in parts if p.startswith('Social Media Instagram:')), 'Unknown')
                age_min = next((p.replace('Age Min:', '').strip() for p in parts if p.startswith('Age Min:')), '')
                age_max = next((p.replace('Age Max:', '').strip() for p in parts if p.startswith('Age Max:')), '')
                season = next((p.replace('Season:', '').strip() for p in parts if p.startswith('Season:')), '')
                registration_fee = next((p.replace('Registration Fee:', '').strip() for p in parts if p.startswith('Registration Fee:')), '')
                notes = next((p.replace('Notes:', '').strip() for p in parts if p.startswith('Notes:')), '')

                program_id = f"{organization_name}_{sport_type}_{program_name}".replace(' ', '_').replace(',', '').lower()

                program_data = {
                    'program_id': program_id,
                    'organization_name': organization_name,
                    'organization_type': organization_type,
                    'sport_type': sport_type,
                    'program_name': program_name,
                    'program_type': program_type,
                    'skill_level': skill_level,
                    'address_street': address_street,
                    'address_city': address_city,
                    'address_state': address_state,
                    'address_zip': address_zip,
                    'county': county,
                    'metro_area': metro_area,
                    'phone': phone,
                    'email': email,
                    'contact_name': contact_name,
                    'website': website,
                    'social_media_facebook': social_media_facebook,
                    'social_media_instagram': social_media_instagram,
                    'age_min': age_min,
                    'age_max': age_max,
                    'season': season,
                    'registration_fee': registration_fee,
                    'notes': notes,
                    'verified': 'No',
                    'data_source': 'AI Research'
                }
                
                # Fill missing info via additional AI query
                program_data = self.fill_missing_info(program_data)
                
                try:
                    handler.insert_program(**program_data)
                except ValueError as e:
                    print(f"Error inserting program {program_name}: {e}")
        handler.validate_data()