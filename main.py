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
        "youth sports programs in New York",
        "youth sports programs in the Midwest",
        "youth sports programs in the South",
        "youth sports programs in the Northeast",
        "youth sports programs in the West",
        "youth baseball in the Midwest",
        "youth soccer in the South",
        "youth basketball in the Northeast",
        "youth sports in major US cities"
    ]
    
    total_added_all = 0
    total_api_calls = 0
    total_tokens = 0
    
    for query in queries:
        print(f"Researching: {query}")
        added, calls, tokens = agent.research_sports_programs(query, handler)
        total_added_all += added
        total_api_calls += calls
        total_tokens += tokens
        print(f"Added {added} programs for this query")

    # Print some data
    programs = handler.get_all_programs()
    print(f"Total programs: {len(programs)}")
    print(f"Total API calls: {total_api_calls}")
    print(f"Estimated tokens used: {total_tokens}")
    print(f"Estimated cost: ${(total_tokens / 1000000) * 0.0004:.4f} (GPT-4o-mini pricing)")
    handler.export_to_json('data/programs.json')
    for program in programs[:10]:  # Print first 10
        print(f"Program: {program['program_name']}, Org: {program['organization_name']}, Sport: {program['sport_type']}")

if __name__ == "__main__":
    main()
