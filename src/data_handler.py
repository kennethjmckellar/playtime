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
        # Required fields: all address, name, and contact information, plus website or social media
        required = [
            'program_id', 'organization_name', 'program_name',
            'address_street', 'address_city', 'address_state', 'address_zip', 'county', 'metro_area',
            'phone', 'email'
        ]
        for req in required:
            if req not in kwargs or not kwargs[req] or kwargs[req] == 'Unknown':
                raise ValueError(f"{req} is required and cannot be unknown")
        # Additional required
        if 'sport_type' not in kwargs or not kwargs['sport_type'] or kwargs['sport_type'] == 'Unknown':
            raise ValueError("sport_type is required")
        # Website or social media required
        has_website = kwargs.get('website') and kwargs['website'] != 'Unknown'
        has_social = (kwargs.get('social_media_facebook') and kwargs['social_media_facebook'] != 'Unknown') or \
                     (kwargs.get('social_media_instagram') and kwargs['social_media_instagram'] != 'Unknown')
        if not has_website and not has_social:
            raise ValueError("Either website or at least one social media link (Facebook or Instagram) is required")
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