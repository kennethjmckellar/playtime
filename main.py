from src.data_handler import DataHandler
from src.agent import SportsResearchAgent

def main():
    handler = DataHandler()
    agent = SportsResearchAgent()

    # Query for youth sports programs in the USA
    query = "youth sports programs in the USA"
    info = agent.research_sports_programs(query)

    # Update CSV
    agent.update_database(handler, info)

    # Print some data
    programs = handler.get_all_programs()
    print(f"Total programs: {len(programs)}")
    for program in programs[:3]:  # Print first 3
        print(f"Program: {program['program_name']}, Org: {program['organization_name']}, Sport: {program['sport_type']}")

if __name__ == "__main__":
    main()