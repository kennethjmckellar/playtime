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
        response = self.client.completions.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=2000
        )
        return response.choices[0].text.strip()

    def scrape_website(self, url):
        # Simple web scraping example
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract relevant info, e.g., team names from common selectors
            teams = soup.find_all(['h2', 'h3', 'div'], string=lambda text: text and 'team' in text.lower())
            return [elem.text.strip() for elem in teams if elem.text.strip()]
        except:
            return []

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

                try:
                    handler.insert_program(
                        program_id=program_id,
                        organization_name=organization_name,
                        organization_type=organization_type,
                        sport_type=sport_type,
                        program_name=program_name,
                        program_type=program_type,
                        skill_level=skill_level,
                        address_street=address_street,
                        address_city=address_city,
                        address_state=address_state,
                        address_zip=address_zip,
                        county=county,
                        metro_area=metro_area,
                        phone=phone,
                        email=email,
                        contact_name=contact_name,
                        website=website,
                        social_media_facebook=social_media_facebook,
                        social_media_instagram=social_media_instagram,
                        age_min=age_min,
                        age_max=age_max,
                        season=season,
                        registration_fee=registration_fee,
                        notes=notes,
                        verified='No',
                        data_source='AI Research'
                    )
                except ValueError as e:
                    print(f"Error inserting program {program_name}: {e}")
        handler.validate_data()