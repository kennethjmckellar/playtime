from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from config.config import OPENAI_API_KEY

class SportsResearchAgent:
    def __init__(self):
        pass  # No AI client needed for scraping

    def research_sports_programs(self, query):
        # Instead of AI, scrape known websites for youth sports programs
        programs = []
        
        # Example sites to scrape with known addresses and counties
        sites = [
            ('https://www.littleleague.org/', 'Little League International', 'Baseball', '539 US Highway Route 15, Williamsport, PA 17701', 'Lycoming'),
            ('https://www.ymca.net/', 'YMCA', 'Various', '101 North Wacker Drive, Chicago, IL 60606', 'Cook'),
            ('https://ayso.org/', 'American Youth Soccer Organization', 'Soccer', '19750 S Vermont Ave, Torrance, CA 90502', 'Los Angeles'),
            ('https://www.bgca.org/', 'Boys & Girls Clubs of America', 'Various', '1275 Peachtree St NE, Atlanta, GA 30309', 'Fulton'),
            ('https://www.i9sports.com/', 'i9 Sports', 'Various', '201 Florida St, Mandeville, LA 70471', 'St. Tammany'),
            ('https://www.usyouthsoccer.org/', 'United States Youth Soccer Association', 'Soccer', '123 Main St, Chicago, IL 60601', 'Cook')
        ]
        
        for url, org, sport, known_address, county in sites:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract basic info
                title = soup.find('title').text.strip() if soup.find('title') else f'{org} Youth Sports Program'
                
                # Use known address
                address_text = known_address
                parts = [p.strip() for p in address_text.split(', ')]
                address_street = parts[0] if len(parts) > 0 else 'Unknown'
                address_city = parts[1] if len(parts) > 1 else 'Unknown'
                address_state_zip = parts[2] if len(parts) > 2 else 'Unknown Unknown'
                address_state, address_zip = address_state_zip.split() if len(address_state_zip.split()) >= 2 else ('Unknown', 'Unknown')
                
                phone = soup.find(string=lambda text: text and '(' in text and ')' in text and len(text) < 20)
                phone = phone.strip() if phone else 'Unknown'
                
                email = soup.find('a', href=lambda href: href and 'mailto:' in href)
                email = email['href'].replace('mailto:', '') if email else 'Unknown'
                
                phone = soup.find(string=lambda text: text and '(' in text and ')' in text)
                phone = phone.strip() if phone else 'Unknown'
                
                email = soup.find('a', href=lambda href: href and 'mailto:' in href)
                email = email['href'].replace('mailto:', '') if email else 'Unknown'
                
                contact_name = 'Contact Person'  # Placeholder
                
                program_data = {
                    'program_id': f"{org.lower().replace(' ', '_')}_{sport.lower()}_{title.lower().replace(' ', '_')[:20]}",
                    'organization_name': org,
                    'organization_type': 'Nonprofit Organization',
                    'sport_type': sport,
                    'program_name': title,
                    'program_type': 'League',
                    'skill_level': 'all_levels',
                    'address_street': address_street,
                    'address_city': address_city,
                    'address_state': address_state,
                    'address_zip': address_zip,
                    'county': county,
                    'metro_area': 'Unknown',
                    'phone': phone,
                    'email': email,
                    'contact_name': 'Contact Person',
                    'website': url,
                    'social_media_facebook': 'Unknown',
                    'social_media_instagram': 'Unknown',
                    'age_min': '5',
                    'age_max': '18',
                    'season': 'Year-round',
                    'registration_fee': 'Varies',
                    'notes': f'Program from {org} website',
                    'verified': 'No',
                    'data_source': 'Web Scraping'
                }
                
                # Fill missing if needed (though scraping provides basics)
                program_data = self.fill_missing_info(program_data)
                programs.append(program_data)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        # Convert to text format for parsing
        info = '\n'.join([f"Program: {p['program_name']}, Organization: {p['organization_name']}, Organization Type: {p['organization_type']}, Sport: {p['sport_type']}, Program Type: {p['program_type']}, Skill Level: {p['skill_level']}, Address Street: {p['address_street']}, Address City: {p['address_city']}, Address State: {p['address_state']}, Address Zip: {p['address_zip']}, County: {p['county']}, Metro Area: {p['metro_area']}, Phone: {p['phone']}, Email: {p['email']}, Contact Name: {p['contact_name']}, Website: {p['website']}, Social Media Facebook: {p['social_media_facebook']}, Social Media Instagram: {p['social_media_instagram']}, Age Min: {p['age_min']}, Age Max: {p['age_max']}, Season: {p['season']}, Registration Fee: {p['registration_fee']}, Notes: {p['notes']}" for p in programs])
        return info

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