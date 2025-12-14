from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from config.config import OPENAI_API_KEY

class SportsResearchAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def research_sports_programs(self, query):
        # Use OpenAI to generate structured info for programs
        prompt = f"""Research and identify youth sports programs in the USA related to: {query}.
        Provide information in the following format for each program. ALL address, name, and contact information is required, and either website or social media links must be provided:
        Program: Program Name, Organization: Organization Name, Organization Type: Type, Sport: Sport Type, Program Type: Type (e.g., League, Camp), Skill Level: Level, Address Street: Street, Address City: City, Address State: State, Address Zip: Zip, County: County, Metro Area: Area, Phone: Phone, Email: Email, Contact Name: Name, Website: URL, Social Media Facebook: URL, Social Media Instagram: URL, Age Min: Min Age, Age Max: Max Age, Season: Season, Registration Fee: Fee, Notes: Description
        Ensure all required fields are provided for each program, including at least website or one social media link."""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()

    def fill_missing_info(self, program_data):
        # Required fields
        required = [
            'organization_name', 'program_name', 'contact_name',
            'address_street', 'address_city', 'address_state', 'address_zip', 'county', 'metro_area',
            'phone', 'email', 'sport_type'
        ]
        # Check if website or social media
        has_online = program_data.get('website') and program_data['website'] != 'Unknown' or \
                     (program_data.get('social_media_facebook') and program_data['social_media_facebook'] != 'Unknown') or \
                     (program_data.get('social_media_instagram') and program_data['social_media_instagram'] != 'Unknown')
        
        missing = [field for field in required if not program_data.get(field) or program_data[field] == 'Unknown']
        if not has_online:
            missing.append('website')  # Need at least one
        
        if missing:
            query = f"Find the following information for the youth sports program '{program_data.get('program_name', 'Unknown')}' by '{program_data.get('organization_name', 'Unknown')}' in {program_data.get('address_city', 'USA')}, {program_data.get('address_state', 'USA')}: {', '.join(missing)}"
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": query}
                    ],
                    max_tokens=500
                )
                info = response.choices[0].message.content.strip()
                # Parse the response to fill missing fields
                lines = info.split('\n')
                for line in lines:
                    line = line.strip()
                    for field in missing:
                        if field.replace('_', ' ').title() in line or field.upper() in line:
                            value = line.split(':', 1)[-1].strip() if ':' in line else line
                            program_data[field] = value
                            break
            except Exception as e:
                print(f"Error filling missing info for {program_data.get('program_name')}: {e}")
        
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