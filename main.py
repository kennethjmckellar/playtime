from src.data_handler import DataHandler
from src.agent import SportsResearchAgent

def main():
    handler = DataHandler()
    agent = SportsResearchAgent()

    # Queries for different regions/sports to get more programs
    queries = [
        "youth baseball leagues and programs in major US cities",
        "youth soccer clubs and academies in the USA", 
        "youth basketball programs and camps nationwide",
        "youth sports leagues in California cities",
        "youth sports programs in Texas metropolitan areas",
        "youth sports leagues in Florida cities",
        "youth sports programs in New York state",
        "youth baseball programs in Midwest states",
        "youth soccer programs in Southern states",
        "youth basketball programs in Northeast region",
        "youth sports academies in Western states",
        "youth baseball leagues in Chicago, Detroit, Milwaukee",
        "youth soccer clubs in Atlanta, Nashville, Charlotte",
        "youth basketball programs in Boston, Philadelphia, Baltimore",
        "youth sports programs in Denver, Phoenix, Las Vegas",
        "youth sports leagues in Seattle, Portland, San Francisco"
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
