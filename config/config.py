import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PROGRAMS_CSV = os.path.join(DATA_DIR, 'programs.csv')