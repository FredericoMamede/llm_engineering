"""
Configuration loader for requirement sets and company contexts.

Supports multi-company/multi-role extensibility by reading from YAML configs.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml


class ConfigLoader:
    """Load requirement sets and company contexts from YAML files."""
    
    def __init__(self, configs_dir: Optional[Path] = None):
        """
        Initialize config loader.
        
        Args:
            configs_dir: Directory containing config files (default: project_root/configs)
        """
        if configs_dir is None:
            configs_dir = Path(__file__).parent.parent / "configs"
        self.configs_dir = Path(configs_dir)
    
    def load_requirement_sets(self) -> List[Dict[str, Any]]:
        """
        Load available requirement sets from requirements.yaml.
        
        Returns:
            List of requirement set dictionaries with id, name, description
        """
        requirements_file = self.configs_dir / "requirements.yaml"
        if not requirements_file.exists():
            return []
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Extract requirement set info
            # For now, we have one set (ai-first-mern-fullstack)
            # But structure supports multiple sets
            requirement_sets = []
            
            if 'requirements' in data:
                reqs = data['requirements']
                core_count = len(reqs.get('core', []))
                plus_count = len(reqs.get('plus', []))
                
                # Extract metadata if available
                set_id = data.get('set_id', 'ai-first-mern-fullstack')
                set_name = data.get('set_name', 'AI-First MERN Fullstack Developer')
                set_description = data.get('set_description', 'Eventyr AI-First MERN Fullstack Developer role requirements')
                
                requirement_sets.append({
                    'id': set_id,
                    'name': set_name,
                    'description': set_description,
                    'requirement_count': core_count + plus_count
                })
            
            return requirement_sets if requirement_sets else [{
                'id': 'ai-first-mern-fullstack',
                'name': 'AI-First MERN Fullstack Developer',
                'description': 'Eventyr AI-First MERN Fullstack Developer role requirements',
                'requirement_count': 22
            }]
        except Exception as e:
            print(f"Error loading requirement sets: {e}")
            return [{
                'id': 'ai-first-mern-fullstack',
                'name': 'AI-First MERN Fullstack Developer',
                'description': 'Eventyr AI-First MERN Fullstack Developer role requirements',
                'requirement_count': 22
            }]
    
    def load_companies(self) -> List[Dict[str, Any]]:
        """
        Load available companies from company_context.yaml.
        
        Returns:
            List of company dictionaries with id, name, description
        """
        company_file = self.configs_dir / "company_context.yaml"
        if not company_file.exists():
            return []
        
        try:
            with open(company_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            companies = []
            
            if 'company_context' in data:
                company_name = data['company_context'].get('name', 'Eventyr')
                company_role = data['company_context'].get('role', 'AI-First MERN Fullstack Developer')
                domain_count = len(data['company_context'].get('domains', []))
                
                companies.append({
                    'id': company_name.lower().replace(' ', '-'),
                    'name': company_name,
                    'role': company_role,
                    'description': f'{company_name} - {company_role}',
                    'domain_count': domain_count
                })
            
            return companies if companies else [{
                'id': 'eventyr',
                'name': 'Eventyr',
                'role': 'AI-First MERN Fullstack Developer',
                'description': 'Eventyr - AI-First MERN Fullstack Developer',
                'domain_count': 7
            }]
        except Exception as e:
            print(f"Error loading companies: {e}")
            return [{
                'id': 'eventyr',
                'name': 'Eventyr',
                'role': 'AI-First MERN Fullstack Developer',
                'description': 'Eventyr - AI-First MERN Fullstack Developer',
                'domain_count': 7
            }]
    
    def get_requirement_set_by_id(self, set_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific requirement set by ID."""
        sets = self.load_requirement_sets()
        for req_set in sets:
            if req_set['id'] == set_id:
                return req_set
        return None
    
    def get_company_by_id(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific company by ID."""
        companies = self.load_companies()
        for company in companies:
            if company['id'] == company_id:
                return company
        return None
