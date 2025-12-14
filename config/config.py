import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PROGRAMS_CSV = os.path.join(DATA_DIR, 'programs.csv')

# Configurable locations for research (expanded to major US cities)
LOCATIONS = [
    # California
    ('Los Angeles', 'California'), ('San Francisco', 'California'), ('San Diego', 'California'), ('Sacramento', 'California'), ('Fresno', 'California'), ('Long Beach', 'California'), ('Oakland', 'California'), ('Bakersfield', 'California'), ('Anaheim', 'California'), ('Santa Ana', 'California'),
    # Texas
    ('Houston', 'Texas'), ('Dallas', 'Texas'), ('Austin', 'Texas'), ('San Antonio', 'Texas'), ('Fort Worth', 'Texas'), ('El Paso', 'Texas'), ('Arlington', 'Texas'), ('Corpus Christi', 'Texas'), ('Plano', 'Texas'), ('Laredo', 'Texas'),
    # Florida
    ('Miami', 'Florida'), ('Orlando', 'Florida'), ('Tampa', 'Florida'), ('Jacksonville', 'Florida'), ('Tallahassee', 'Florida'), ('St. Petersburg', 'Florida'), ('Cape Coral', 'Florida'), ('Pembroke Pines', 'Florida'), ('Hollywood', 'Florida'), ('Gainesville', 'Florida'),
    # New York
    ('New York City', 'New York'), ('Buffalo', 'New York'), ('Albany', 'New York'), ('Rochester', 'New York'), ('Syracuse', 'New York'), ('Yonkers', 'New York'), ('Brooklyn', 'New York'), ('Queens', 'New York'), ('Manhattan', 'New York'), ('Bronx', 'New York'),
    # Illinois
    ('Chicago', 'Illinois'), ('Springfield', 'Illinois'), ('Peoria', 'Illinois'), ('Naperville', 'Illinois'), ('Aurora', 'Illinois'), ('Rockford', 'Illinois'), ('Joliet', 'Illinois'), ('Elgin', 'Illinois'), ('Waukegan', 'Illinois'), ('Cicero', 'Illinois'),
    # Pennsylvania
    ('Philadelphia', 'Pennsylvania'), ('Pittsburgh', 'Pennsylvania'), ('Harrisburg', 'Pennsylvania'), ('Allentown', 'Pennsylvania'), ('Erie', 'Pennsylvania'), ('Reading', 'Pennsylvania'), ('Scranton', 'Pennsylvania'), ('Bethlehem', 'Pennsylvania'), ('Lancaster', 'Pennsylvania'), ('Altoona', 'Pennsylvania'),
    # Ohio
    ('Columbus', 'Ohio'), ('Cleveland', 'Ohio'), ('Cincinnati', 'Ohio'), ('Toledo', 'Ohio'), ('Akron', 'Ohio'), ('Dayton', 'Ohio'), ('Parma', 'Ohio'), ('Canton', 'Ohio'), ('Youngstown', 'Ohio'), ('Lorain', 'Ohio'),
    # Georgia
    ('Atlanta', 'Georgia'), ('Savannah', 'Georgia'), ('Augusta', 'Georgia'), ('Columbus', 'Georgia'), ('Macon', 'Georgia'), ('Athens', 'Georgia'), ('Sandy Springs', 'Georgia'), ('Roswell', 'Georgia'), ('Johns Creek', 'Georgia'), ('Warner Robins', 'Georgia'),
    # North Carolina
    ('Charlotte', 'North Carolina'), ('Raleigh', 'North Carolina'), ('Greensboro', 'North Carolina'), ('Durham', 'North Carolina'), ('Winston-Salem', 'North Carolina'), ('Fayetteville', 'North Carolina'), ('Cary', 'North Carolina'), ('Wilmington', 'North Carolina'), ('High Point', 'North Carolina'), ('Greenville', 'North Carolina'),
    # Michigan
    ('Detroit', 'Michigan'), ('Grand Rapids', 'Michigan'), ('Lansing', 'Michigan'), ('Warren', 'Michigan'), ('Sterling Heights', 'Michigan'), ('Ann Arbor', 'Michigan'), ('Flint', 'Michigan'), ('Dearborn', 'Michigan'), ('Livonia', 'Michigan'), ('Westland', 'Michigan'),
    # Additional states (sample cities)
    ('Phoenix', 'Arizona'), ('Tucson', 'Arizona'), ('Mesa', 'Arizona'),
    ('Denver', 'Colorado'), ('Colorado Springs', 'Colorado'), ('Aurora', 'Colorado'),
    ('Washington', 'District of Columbia'), ('Seattle', 'Washington'), ('Spokane', 'Washington'),
    ('Boston', 'Massachusetts'), ('Worcester', 'Massachusetts'), ('Springfield', 'Massachusetts'),
    ('Nashville', 'Tennessee'), ('Memphis', 'Tennessee'), ('Knoxville', 'Tennessee'),
    ('Indianapolis', 'Indiana'), ('Fort Wayne', 'Indiana'), ('Evansville', 'Indiana'),
    ('Las Vegas', 'Nevada'), ('Reno', 'Nevada'), ('Henderson', 'Nevada'),
    ('Baltimore', 'Maryland'), ('Frederick', 'Maryland'), ('Rockville', 'Maryland'),
    ('Milwaukee', 'Wisconsin'), ('Madison', 'Wisconsin'), ('Green Bay', 'Wisconsin'),
    ('Albuquerque', 'New Mexico'), ('Las Cruces', 'New Mexico'), ('Rio Rancho', 'New Mexico'),
    ('Tucson', 'Arizona'), ('Fresno', 'California'), ('Colorado Springs', 'Colorado'),
    ('Washington', 'District of Columbia'), ('Seattle', 'Washington'), ('Spokane', 'Washington'),
    ('Boston', 'Massachusetts'), ('Worcester', 'Massachusetts'), ('Springfield', 'Massachusetts'),
    ('Nashville', 'Tennessee'), ('Memphis', 'Tennessee'), ('Knoxville', 'Tennessee'),
    ('Indianapolis', 'Indiana'), ('Fort Wayne', 'Indiana'), ('Evansville', 'Indiana'),
    ('Las Vegas', 'Nevada'), ('Reno', 'Nevada'), ('Henderson', 'Nevada'),
    ('Baltimore', 'Maryland'), ('Frederick', 'Maryland'), ('Rockville', 'Maryland'),
    ('Milwaukee', 'Wisconsin'), ('Madison', 'Wisconsin'), ('Green Bay', 'Wisconsin'),
    ('Albuquerque', 'New Mexico'), ('Las Cruces', 'New Mexico'), ('Rio Rancho', 'New Mexico'),
    ('Omaha', 'Nebraska'), ('Lincoln', 'Nebraska'), ('Bellevue', 'Nebraska'),
    ('Oklahoma City', 'Oklahoma'), ('Tulsa', 'Oklahoma'), ('Norman', 'Oklahoma'),
    ('Portland', 'Oregon'), ('Salem', 'Oregon'), ('Eugene', 'Oregon'),
    ('Providence', 'Rhode Island'), ('Warwick', 'Rhode Island'), ('Cranston', 'Rhode Island'),
    ('Columbia', 'South Carolina'), ('Charleston', 'South Carolina'), ('North Charleston', 'South Carolina'),
    ('Salt Lake City', 'Utah'), ('West Valley City', 'Utah'), ('Provo', 'Utah'),
    ('Virginia Beach', 'Virginia'), ('Norfolk', 'Virginia'), ('Chesapeake', 'Virginia'),
    ('Birmingham', 'Alabama'), ('Montgomery', 'Alabama'), ('Mobile', 'Alabama'),
    ('Anchorage', 'Alaska'), ('Fairbanks', 'Alaska'), ('Juneau', 'Alaska'),
    ('Little Rock', 'Arkansas'), ('Fort Smith', 'Arkansas'), ('Fayetteville', 'Arkansas'),
    ('Bridgeport', 'Connecticut'), ('New Haven', 'Connecticut'), ('Stamford', 'Connecticut'),
    ('Dover', 'Delaware'), ('Wilmington', 'Delaware'), ('Newark', 'Delaware'),
    ('Honolulu', 'Hawaii'), ('Pearl City', 'Hawaii'), ('Hilo', 'Hawaii'),
    ('Boise', 'Idaho'), ('Meridian', 'Idaho'), ('Nampa', 'Idaho'),
    ('Des Moines', 'Iowa'), ('Cedar Rapids', 'Iowa'), ('Davenport', 'Iowa'),
    ('Wichita', 'Kansas'), ('Overland Park', 'Kansas'), ('Kansas City', 'Kansas'),
    ('Louisville', 'Kentucky'), ('Lexington', 'Kentucky'), ('Bowling Green', 'Kentucky'),
    ('New Orleans', 'Louisiana'), ('Baton Rouge', 'Louisiana'), ('Shreveport', 'Louisiana'),
    ('Portland', 'Maine'), ('Lewiston', 'Maine'), ('Bangor', 'Maine'),
    ('Minneapolis', 'Minnesota'), ('Saint Paul', 'Minnesota'), ('Rochester', 'Minnesota'),
    ('Jackson', 'Mississippi'), ('Gulfport', 'Mississippi'), ('Southaven', 'Mississippi'),
    ('Kansas City', 'Missouri'), ('Saint Louis', 'Missouri'), ('Springfield', 'Missouri'),
    ('Billings', 'Montana'), ('Missoula', 'Montana'), ('Great Falls', 'Montana'),
    ('Carson City', 'Nevada'), ('Las Vegas', 'Nevada'), ('Reno', 'Nevada'),
    ('Manchester', 'New Hampshire'), ('Nashua', 'New Hampshire'), ('Concord', 'New Hampshire'),
    ('Trenton', 'New Jersey'), ('Newark', 'New Jersey'), ('Jersey City', 'New Jersey'),
    ('Santa Fe', 'New Mexico'), ('Albuquerque', 'New Mexico'), ('Las Cruces', 'New Mexico'),
    ('Albany', 'New York'), ('Buffalo', 'New York'), ('Rochester', 'New York'),
    ('Raleigh', 'North Carolina'), ('Charlotte', 'North Carolina'), ('Greensboro', 'North Carolina'),
    ('Bismarck', 'North Dakota'), ('Fargo', 'North Dakota'), ('Grand Forks', 'North Dakota'),
    ('Columbus', 'Ohio'), ('Cleveland', 'Ohio'), ('Cincinnati', 'Ohio'),
    ('Oklahoma City', 'Oklahoma'), ('Tulsa', 'Oklahoma'), ('Norman', 'Oklahoma'),
    ('Salem', 'Oregon'), ('Portland', 'Oregon'), ('Eugene', 'Oregon'),
    ('Harrisburg', 'Pennsylvania'), ('Philadelphia', 'Pennsylvania'), ('Pittsburgh', 'Pennsylvania'),
    ('Providence', 'Rhode Island'), ('Warwick', 'Rhode Island'), ('Cranston', 'Rhode Island'),
    ('Columbia', 'South Carolina'), ('Charleston', 'South Carolina'), ('North Charleston', 'South Carolina'),
    ('Pierre', 'South Dakota'), ('Sioux Falls', 'South Dakota'), ('Rapid City', 'South Dakota'),
    ('Nashville', 'Tennessee'), ('Memphis', 'Tennessee'), ('Knoxville', 'Tennessee'),
    ('Austin', 'Texas'), ('Houston', 'Texas'), ('Dallas', 'Texas'),
    ('Salt Lake City', 'Utah'), ('West Valley City', 'Utah'), ('Provo', 'Utah'),
    ('Montpelier', 'Vermont'), ('Burlington', 'Vermont'), ('Rutland', 'Vermont'),
    ('Richmond', 'Virginia'), ('Virginia Beach', 'Virginia'), ('Norfolk', 'Virginia'),
    ('Olympia', 'Washington'), ('Seattle', 'Washington'), ('Spokane', 'Washington'),
    ('Charleston', 'West Virginia'), ('Huntington', 'West Virginia'), ('Parkersburg', 'West Virginia'),
    ('Madison', 'Wisconsin'), ('Milwaukee', 'Wisconsin'), ('Green Bay', 'Wisconsin'),
    ('Cheyenne', 'Wyoming'), ('Casper', 'Wyoming'), ('Laramie', 'Wyoming'),
]