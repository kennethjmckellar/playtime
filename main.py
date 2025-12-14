from src.data_handler import DataHandler
from src.agent import SportsResearchAgent

def main():
    handler = DataHandler()
    agent = SportsResearchAgent()

    # Queries for different regions/sports to get more programs
    queries = [
        "youth sports programs in the USA",
        "youth baseball programs in the USA",
        "youth soccer programs in the USA",
        "youth basketball programs in the USA",
        "youth sports programs in California",
        "youth sports programs in Texas",
        "youth sports programs in Florida",
        "youth sports programs in New York"
    ]
    
    for query in queries:
        print(f"Researching: {query}")
        info = agent.research_sports_programs(query)
        agent.update_database(handler, info)

    # Print some data
    programs = handler.get_all_programs()
    print(f"Total programs: {len(programs)}")
    for program in programs[:10]:  # Print first 10
        print(f"Program: {program['program_name']}, Org: {program['organization_name']}, Sport: {program['sport_type']}")

if __name__ == "__main__":
    main()
