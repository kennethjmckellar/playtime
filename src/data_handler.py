import pandas as pd
import os
from config.config import PROGRAMS_CSV

class DataHandler:
    def __init__(self):
        self.columns = [
            'program_id', 'organization_name', 'organization_type', 'sport_type', 'program_name', 'program_type', 'skill_level',
            'address_street', 'address_city', 'address_state', 'address_zip', 'county', 'metro_area',
            'phone', 'email', 'contact_name', 'website', 'social_media_facebook', 'social_media_instagram',
            'age_min', 'age_max', 'age_groups', 'gender', 'team_based', 'season', 'cost',
            'transportation_provided', 'reviews_text', 'average_rating', 'review_count', 'verified', 'data_source', 'last_verified', 'notes', 'keywords_long_tail',
            'facility_type'
        ]
        
        if os.path.exists(PROGRAMS_CSV):
            self.df = pd.read_csv(PROGRAMS_CSV)
        else:
            self.df = pd.DataFrame(columns=self.columns)

    def insert_program(self, **kwargs):
        # Required fields: program_id, sport_type, and at least one name field
        if 'program_id' not in kwargs or not kwargs['program_id']:
            raise ValueError("program_id is required")
        if 'sport_type' not in kwargs or not kwargs['sport_type'] or kwargs['sport_type'] == 'Unknown':
            raise ValueError("sport_type is required")
        
        # At least one of organization_name or program_name must be meaningful
        org_name = kwargs.get('organization_name', '')
        prog_name = kwargs.get('program_name', '')
        if (not org_name or org_name == 'Unknown') and (not prog_name or prog_name == 'Unknown'):
            raise ValueError("At least organization_name or program_name must be provided")
        
        # Fill in defaults for missing required fields
        defaults = {
            'organization_name': prog_name if org_name == 'Unknown' else org_name,
            'program_name': org_name if prog_name == 'Unknown' else prog_name,
            'organization_type': 'Nonprofit',
            'program_type': 'League',
            'skill_level': 'all_levels',
            'address_street': 'Unknown',
            'address_city': 'Unknown',
            'address_state': 'Unknown',
            'address_zip': 'Unknown',
            'county': 'Unknown',
            'metro_area': 'Unknown',
            'phone': 'Unknown',
            'email': 'Unknown',
            'contact_name': 'Contact Person',
            'website': 'Unknown',
            'social_media_facebook': 'Unknown',
            'social_media_instagram': 'Unknown',
            'age_min': '5',
            'age_max': '18',
            'season': 'Year-round',
            'cost': 'Unknown',
            'notes': 'Unknown',
            'verified': 'No',
            'data_source': 'AI Research'
        }
        
        for key, default in defaults.items():
            if key not in kwargs or not kwargs[key] or kwargs[key] == 'Unknown':
                kwargs[key] = default
        
        print(f"Inserting program: {kwargs.get('program_name', 'Unknown')} by {kwargs.get('organization_name', 'Unknown')}")
        if kwargs['program_id'] in self.df['program_id'].values:
            # Update existing
            idx = self.df[self.df['program_id'] == kwargs['program_id']].index[0]
            for col in kwargs:
                if col in self.columns:
                    self.df.at[idx, col] = kwargs[col]
            self._save()
            return
        # Fill missing with defaults
        for col in self.columns:
            if col not in kwargs:
                kwargs[col] = 'Unknown'
        new_row = pd.DataFrame([kwargs], columns=self.columns)
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save()

    def _save(self):
        self.df.to_csv(PROGRAMS_CSV, index=False)

    def get_all_programs(self):
        return self.df.to_dict('records')

    def validate_data(self):
        # Ensure all rows have required fields and consistent format
        if self.df.empty:
            return
        for col in self.columns:
            if col not in self.df.columns:
                self.df[col] = 'Unknown'
        # Ensure types: strings
        self.df = self.df.astype(str)
        # Check required not empty
        for req in ['program_id', 'organization_name', 'sport_type', 'program_name']:
            if (self.df[req] == '').any():
                print(f"Warning: Missing {req} in some rows")
        self._save()

    def export_to_json(self, filepath):
        import json
        with open(filepath, 'w') as f:
            json.dump(self.get_all_programs(), f, indent=2)
        print(f"Exported {len(self.df)} programs to {filepath}")