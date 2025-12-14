from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from config.config import OPENAI_API_KEY, LOCATIONS
import re

class SportsResearchAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.used_states = set()
        self.api_calls = 0
        self.total_tokens = 0

    def research_sports_programs(self, query, handler):
        # Use AI to research programs in one city per query, saving progress incrementally
        total_added = 0
        
        # Extract sport from query
        sport = self.extract_sport(query)
        
        # List of major cities and states to research (expanded for comprehensive coverage)
        locations = LOCATIONS
        
        # Load existing programs to check counts per city
        from config.config import PROGRAMS_CSV
        import pandas as pd
        try:
            existing_df = pd.read_csv(PROGRAMS_CSV)
            city_counts = existing_df.groupby('address_city').size().to_dict()
        except:
            city_counts = {}
        
        # Select up to 3 cities from different states that need research
        selected_locations = []
        for city, state in locations:
            current_count = city_counts.get(city, 0)
            if current_count < 20 and state not in self.used_states and len(selected_locations) < 3:
                selected_locations.append((city, state))
                self.used_states.add(state)
        
        if not selected_locations:
            print(f"No more cities to research for query: {query}")
            return 0
        
        cities_str = ', '.join([f"{city}, {state}" for city, state in selected_locations])
        prompt = f"Research youth {sport} programs in these cities: {cities_str}. Provide detailed information for up to 20 programs per city. For each program, provide ALL available information - do not use 'Unknown' or placeholder values if you can find real information. Return in this exact format for each program:\n\n1. Name: [Actual Program Name]\n   Organization: [Actual Organization Name]\n   Organization Type: [Type]\n   Sport: [{sport}]\n   Program Type: [Type]\n   Skill Level: [Level]\n   Address: [Street Address]\n   City: [City Name]\n   State: [State Name]\n   Zip: [Zip Code]\n   County: [County]\n   Metro Area: [Metro Area]\n   Phone: [Phone Number]\n   Email: [Email Address]\n   Website: [Website URL]\n   Social Media Facebook: [Facebook URL]\n   Social Media Instagram: [Instagram URL]\n   Age Min: [Min Age]\n   Age Max: [Max Age]\n   Season: [Season]\n   Cost: [Cost Information]\n   Notes: [Additional Notes]"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            
            self.api_calls += 1
            if hasattr(response, 'usage') and response.usage:
                self.total_tokens += response.usage.total_tokens
            
            program_info = response.choices[0].message.content
            print(f"Raw AI response for query '{query}':\n{program_info}\n---END RESPONSE---\n")
            programs = self.parse_program_info(program_info)
            
            for program in programs:
                # Set known location fields based on parsed city/state
                parsed_city = program.get('address_city', 'Unknown')
                parsed_state = program.get('address_state', 'Unknown')
                # Find matching location
                for loc_city, loc_state in selected_locations:
                    if parsed_city == loc_city and parsed_state == loc_state:
                        program['address_city'] = loc_city
                        program['address_state'] = loc_state
                        program['county'] = program.get('county', 'Unknown')
                        program['metro_area'] = program.get('metro_area', loc_city)
                        break
                
                # Ensure required fields have defaults
                program['organization_name'] = program.get('organization_name', 'Unknown Organization')
                program['program_name'] = program.get('program_name', f"{parsed_city} Youth Program")
                program['sport_type'] = program.get('sport_type', sport)
                program['phone'] = program.get('phone', 'Unknown')
                program['email'] = program.get('email', 'Unknown')
                program['website'] = program.get('website', 'Unknown')
                
                try:
                    handler.insert_program(**program)
                    total_added += 1
                    print(f"Added program: {program.get('program_name', 'Unknown')} in {parsed_city}, {parsed_state}")
                except Exception as e:
                    print(f"Error inserting program in {parsed_city}, {parsed_state}: {e}")
        except Exception as e:
            print(f"Error researching {cities_str}: {e}")
        
        return total_added, self.api_calls, self.total_tokens
    
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
                        model="gpt-4o-mini",
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
        current_city = None
        current_state = None
        current_program = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for city header like "### Los Angeles, California"
            if line.startswith('### ') and ',' in line:
                city_state = line[4:].strip()
                if ', ' in city_state:
                    current_city, current_state = city_state.split(', ', 1)
                    current_state = current_state.strip()
                continue
            
            # Check for numbered program entries like "1. **Name**: ..."
            if re.match(r'^\d+\.\s+\*\*Name\*\*:\s*', line):
                # Start of a new program
                if current_program:
                    programs.append(current_program)
                
                current_program = {}
                # Extract the name from this line
                name_match = re.search(r'\*\*Name\*\*:\s*(.+)', line)
                if name_match:
                    current_program['name'] = name_match.group(1).strip()
                continue
            
            # If we have a current program, check for other fields
            if current_program is not None:
                # Check for field lines like "   - Organization: ..."
                if line.startswith('   - ') and ': ' in line:
                    field_line = line[5:]  # Remove the "   - " prefix
                    if ': ' in field_line:
                        key, value = field_line.split(': ', 1)
                        key = key.strip().lower().replace(' ', '_')
                        value = value.strip()
                        current_program[key] = value
        
        # Add the last program
        if current_program:
            programs.append(current_program)
        
        # Now process all programs
        processed_programs = []
        for program_data in programs:
            # Map keys to match database schema
            program_data['program_name'] = program_data.pop('name', 'Unknown')
            program_data['organization_name'] = program_data.pop('organization', 'Unknown')
            program_data['organization_type'] = program_data.pop('organization_type', 'Nonprofit')
            program_data['sport_type'] = program_data.pop('sport', 'Unknown')
            program_data['program_type'] = program_data.pop('program_type', 'League')
            program_data['skill_level'] = program_data.pop('skill_level', 'all_levels')
            program_data['address_street'] = program_data.pop('address', 'Unknown')
            program_data['address_city'] = program_data.pop('city', current_city or 'Unknown')
            program_data['address_state'] = program_data.pop('state', current_state or 'Unknown')
            program_data['address_zip'] = program_data.pop('zip', 'Unknown')
            program_data['county'] = program_data.pop('county', 'Unknown')
            program_data['metro_area'] = program_data.pop('metro_area', current_city or 'Unknown')
            program_data['phone'] = program_data.pop('phone', 'Unknown')
            program_data['email'] = program_data.pop('email', 'Unknown')
            program_data['website'] = program_data.pop('website', 'Unknown')
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
            
            processed_programs.append(program_data)
        
        return processed_programs

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