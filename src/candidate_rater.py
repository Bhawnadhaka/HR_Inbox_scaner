"""
Candidate rating module for categorizing candidates based on experience
"""
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandidateRater:
    """Rates candidates based on their experience and other factors"""
    
    def __init__(self):
        """Initialize candidate rater"""
        self.rating_criteria = {
            'Junior': {'min_experience': 0, 'max_experience': 2},
            'Mid-level': {'min_experience': 2, 'max_experience': 5},
            'Senior': {'min_experience': 5, 'max_experience': float('inf')}
        }
    
    def rate_candidate(self, candidate_info: Dict) -> Dict:
        """Rate candidate and add rating information"""
        years_experience = candidate_info.get('years_of_experience', 0)
        
        # Determine experience level
        experience_level = self._categorize_experience(years_experience)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(candidate_info)
        
        # Add rating information to candidate info
        candidate_info.update({
            'experience_level': experience_level,
            'overall_score': overall_score,
            'rating_breakdown': self._get_rating_breakdown(candidate_info)
        })
        
        logger.info(f"Rated candidate {candidate_info.get('name', 'Unknown')}: {experience_level} ({overall_score}/100)")
        
        return candidate_info
    
    def _categorize_experience(self, years: int) -> str:
        """Categorize candidate based on years of experience"""
        for level, criteria in self.rating_criteria.items():
            if criteria['min_experience'] <= years < criteria['max_experience']:
                return level
        
        return 'Senior'  # Default for high experience
    
    def _calculate_overall_score(self, candidate_info: Dict) -> int:
        """Calculate overall candidate score out of 100"""
        score = 0
        
        # Experience score (40 points max)
        experience_years = candidate_info.get('years_of_experience', 0)
        if experience_years > 0:
            score += min(experience_years * 4, 40)
        
        # Skills score (30 points max)
        skills = candidate_info.get('skills', [])
        score += min(len(skills) * 3, 30)
        
        # Education score (15 points max)
        education = candidate_info.get('education', '')
        if education:
            score += 15
        
        # Contact completeness score (15 points max)
        contact_fields = ['email', 'phone', 'location']
        completed_fields = sum(1 for field in contact_fields if candidate_info.get(field))
        score += completed_fields * 5
        
        return min(score, 100)  # Cap at 100
    
    def _get_rating_breakdown(self, candidate_info: Dict) -> Dict:
        """Get detailed breakdown of rating components"""
        breakdown = {
            'experience_points': 0,
            'skills_points': 0,
            'education_points': 0,
            'contact_points': 0
        }
        
        # Experience points
        experience_years = candidate_info.get('years_of_experience', 0)
        breakdown['experience_points'] = min(experience_years * 4, 40)
        
        # Skills points
        skills = candidate_info.get('skills', [])
        breakdown['skills_points'] = min(len(skills) * 3, 30)
        
        # Education points
        education = candidate_info.get('education', '')
        breakdown['education_points'] = 15 if education else 0
        
        # Contact points
        contact_fields = ['email', 'phone', 'location']
        completed_fields = sum(1 for field in contact_fields if candidate_info.get(field))
        breakdown['contact_points'] = completed_fields * 5
        
        return breakdown
    
    def get_rating_summary(self, candidates: list) -> Dict:
        """Get summary statistics of all rated candidates"""
        if not candidates:
            return {}
        
        total_candidates = len(candidates)
        
        # Count by experience level
        level_counts = {'Junior': 0, 'Mid-level': 0, 'Senior': 0}
        total_score = 0
        
        for candidate in candidates:
            level = candidate.get('experience_level', 'Junior')
            level_counts[level] += 1
            total_score += candidate.get('overall_score', 0)
        
        # Calculate percentages
        level_percentages = {
            level: (count / total_candidates) * 100 
            for level, count in level_counts.items()
        }
        
        return {
            'total_candidates': total_candidates,
            'level_counts': level_counts,
            'level_percentages': level_percentages,
            'average_score': total_score / total_candidates if total_candidates > 0 else 0,
            'distribution': {
                'junior_percentage': level_percentages['Junior'],
                'mid_level_percentage': level_percentages['Mid-level'],
                'senior_percentage': level_percentages['Senior']
            }
        }
