from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from config.config import OPENAI_API_KEY

class SportsResearchAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.used_states = set()

    def research_sports_programs(self, query, handler):
        # Use AI to research programs in one city per query, saving progress incrementally
        total_added = 0
        
        # Extract sport from query
        sport = self.extract_sport(query)
        
        # List of major cities and states to research (expanded for comprehensive coverage)
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
            ('Columbus', 'Ohio'),
            ('Cleveland', 'Ohio'),
            ('Cincinnati', 'Ohio'),
            ('Atlanta', 'Georgia'),
            ('Savannah', 'Georgia'),
            ('Augusta', 'Georgia'),
            ('Charlotte', 'North Carolina'),
            ('Raleigh', 'North Carolina'),
            ('Greensboro', 'North Carolina'),
            ('Detroit', 'Michigan'),
            ('Grand Rapids', 'Michigan'),
            ('Lansing', 'Michigan'),
        ]
        
        # Load existing programs to check counts per city
        from config.config import PROGRAMS_CSV
        import pandas as pd
        try:
            existing_df = pd.read_csv(PROGRAMS_CSV)
            city_counts = existing_df.groupby('address_city').size().to_dict()
        except:
            city_counts = {}
        
        # Select one city from a different state that needs research
        selected_city = None
        selected_state = None
        for city, state in locations:
            current_count = city_counts.get(city, 0)
            if current_count < 5 and state not in self.used_states:
                selected_city = city
                selected_state = state
                self.used_states.add(state)
                break
        
        if not selected_city:
            print(f"No more cities to research for query: {query}")
            return 0
        
        prompt = f"Research youth {sport} programs in {selected_city}, {selected_state}. Provide detailed information for up to 20 programs. Return in this exact format for each program on a new line: Name: [Program Name], Organization: [Organization Name], Organization Type: [Type], Sport: [Sport], Program Type: [Type], Skill Level: [Level], Address: [Street Address], City: [{selected_city}], State: [{selected_state}], Zip: [Zip Code], County: [County], Metro Area: [Metro Area], Phone: [Phone], Email: [Email], Website: [Website], Social Media Facebook: [FB], Social Media Instagram: [IG], Age Min: [Min], Age Max: [Max], Season: [Season], Cost: [Summarized cost info], Notes: [Notes]"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            
            program_info = response.choices[0].message.content
            programs = self.parse_program_info(program_info)
            
            for program in programs:
                try:
                    handler.insert_program(**program)
                    total_added += 1
                    print(f"Added program: {program.get('program_name', 'Unknown')} in {selected_city}, {selected_state}")
                except Exception as e:
                    print(f"Error inserting program in {selected_city}, {selected_state}: {e}")
        except Exception as e:
            print(f"Error researching {selected_city}, {selected_state}: {e}")
        
        return total_added
    
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
    
    def update_database(self, handler, info):
        # First, review existing programs and fill missing information
        self.fill_missing_info(handler)
        
        programs = self.parse_program_info(info)
        for program in programs:
            try:
                handler.insert_program(**program)
            except Exception as e:
                print(f"Error inserting program {program.get('program_name', 'Unknown')}: {e}")
    
    def fill_missing_info(self, handler):
        programs = handler.get_all_programs()
        for program in programs:
            missing_fields = []
            for field in ['phone', 'email', 'website', 'social_media_facebook', 'social_media_instagram']:
                if program.get(field) == 'Unknown':
                    missing_fields.append(field)
            if missing_fields and program.get('organization_name') != 'Unknown':
                prompt = f"Find the {', '.join(missing_fields)} for {program['program_name']} by {program['organization_name']} in {program.get('address_city', 'Unknown')}, {program.get('address_state', 'Unknown')}."
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    update_info = response.choices[0].message.content
                    # Simple parsing: assume "Phone: xxx\nEmail: yyy"
                    for line in update_info.split('\n'):
                        if ': ' in line:
                            key, value = line.split(': ', 1)
                            key_lower = key.lower().replace(' ', '_')
                            if key_lower in missing_fields and value.strip():
                                program[key_lower] = value.strip()
                    # Update in database
                    handler.update_program(program['program_id'], program)
                except Exception as e:
                    print(f"Error updating {program['program_name']}: {e}")
    
    def parse_program_info(self, info):
        programs = []
        lines = info.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.split(', ')
                program_data = {}
                for part in parts:
                    if ': ' in part:
                        key, value = part.split(': ', 1)
                        key = key.lower().replace(' ', '_')
                        program_data[key] = value
                # Map keys to match dict
                program_data['program_name'] = program_data.pop('name', 'Unknown')
                program_data['organization_name'] = program_data.pop('organization', 'Unknown')
                program_data['organization_type'] = program_data.pop('organization_type', 'Nonprofit')
                program_data['sport_type'] = program_data.pop('sport', 'Unknown')
                program_data['program_type'] = program_data.pop('program_type', 'League')
                program_data['skill_level'] = program_data.pop('skill_level', 'all_levels')
                program_data['address_street'] = program_data.pop('address', 'Unknown')
                program_data['address_city'] = program_data.pop('city', 'Unknown')
                program_data['address_state'] = program_data.pop('state', 'Unknown')
                program_data['address_zip'] = program_data.pop('zip', 'Unknown')
                # keep county, metro_area, phone, email, website
                program_data['social_media_facebook'] = program_data.pop('social_media_facebook', 'Unknown')
                program_data['social_media_instagram'] = program_data.pop('social_media_instagram', 'Unknown')
                program_data['age_min'] = program_data.pop('age_min', '5')
                program_data['age_max'] = program_data.pop('age_max', '18')
                program_data['season'] = program_data.pop('season', 'Year-round')
                program_data['cost'] = program_data.pop('cost', 'Unknown')
                program_data['notes'] = program_data.pop('notes', 'Unknown')
                program_data['contact_name'] = 'Contact Person'
                program_data['verified'] = 'No'
                program_data['data_source'] = 'AI Research'
                program_data['program_id'] = f"{program_data['organization_name'].lower().replace(' ', '_')}_{program_data['sport_type'].lower()}_{program_data['program_name'].lower().replace(' ', '_')[:20]}"
                programs.append(program_data)
        return programs

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