import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PROGRAMS_CSV = os.path.join(DATA_DIR, 'programs.csv')

# Configurable locations for research
LOCATIONS = [
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