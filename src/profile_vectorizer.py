"""Profile vectorization using sentence-transformers."""

import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import Dict, List
import re

from config import (
    EMBEDDING_MODEL,
    PROFILE_PATH,
    PROFILE_EMBEDDING_PATH,
)


class ProfileVectorizer:
    """Converts career profile into semantic embeddings."""

    def __init__(self):
        """Initialize the sentence transformer model."""
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.profile_data = None
        self.embedding = None

    def parse_profile(self) -> Dict[str, any]:
        """Parse the profile markdown document into structured data."""
        if not PROFILE_PATH.exists():
            raise FileNotFoundError(f"Profile not found at {PROFILE_PATH}")

        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        profile = {
            'full_text': content,
            'technical_skills': self._extract_technical_skills(content),
            'work_preferences': self._extract_work_preferences(content),
            'culture_priorities': self._extract_culture_priorities(content),
            'red_flags': self._extract_red_flags(content),
            'accomplishments': self._extract_accomplishments(content),
            'resume_anchors': self._extract_resume_anchors(content),
        }

        self.profile_data = profile
        return profile

    def _extract_technical_skills(self, content: str) -> Dict[str, List[str]]:
        """Extract technical skills organized by proficiency tier."""
        skills = {
            'expert': [],
            'intermediate': [],
            'foundational': []
        }

        # Extract Tier 1 - Expert Level
        expert_match = re.search(r'\*\*Tier 1 - Expert Level:\*\*(.*?)\*\*Tier 2', content, re.DOTALL)
        if expert_match:
            expert_text = expert_match.group(1)
            # Extract bullet points
            skills['expert'] = [line.strip('- ').strip() for line in expert_text.split('\n')
                              if line.strip().startswith('-') and not line.strip().startswith('  -')]

        # Extract Tier 2 - Intermediate Level
        intermediate_match = re.search(r'\*\*Tier 2 - Intermediate Level:\*\*(.*?)\*\*Tier 3', content, re.DOTALL)
        if intermediate_match:
            intermediate_text = intermediate_match.group(1)
            skills['intermediate'] = [line.strip('- ').strip() for line in intermediate_text.split('\n')
                                    if line.strip().startswith('-') and not line.strip().startswith('  -')]

        # Extract Tier 3 - Foundational/Learning
        foundational_match = re.search(r'\*\*Tier 3 - Foundational/Learning:\*\*(.*?)###', content, re.DOTALL)
        if foundational_match:
            foundational_text = foundational_match.group(1)
            skills['foundational'] = [line.strip('- ').strip() for line in foundational_text.split('\n')
                                     if line.strip().startswith('-')]

        return skills

    def _extract_work_preferences(self, content: str) -> Dict[str, any]:
        """Extract work arrangement and compensation preferences."""
        preferences = {}

        # Extract compensation range
        comp_match = re.search(r'\*\*Salary Range:\*\*\s*\$?([\d,]+)\s*-\s*\$?([\d,]+)', content)
        if comp_match:
            preferences['salary_min'] = int(comp_match.group(1).replace(',', ''))
            preferences['salary_max'] = int(comp_match.group(2).replace(',', ''))

        # Extract remote preference
        if 'High preference for at least 80% remote' in content or 'Remote:** High preference' in content:
            preferences['remote_preference'] = 'high'

        # Extract location
        location_match = re.search(r'\*\*Location:\*\*\s*([^\n]+)', content)
        if location_match:
            preferences['location'] = location_match.group(1).strip()

        # Extract industries
        preferences['preferred_industries'] = []
        if 'Mission-driven education/nonprofits' in content:
            preferences['preferred_industries'].append('education')
            preferences['preferred_industries'].append('nonprofit')
        if 'Healthcare technology' in content:
            preferences['preferred_industries'].append('healthcare')

        return preferences

    def _extract_culture_priorities(self, content: str) -> List[str]:
        """Extract positive culture attributes (green flags)."""
        priorities = []

        green_flags_match = re.search(r'### Green Flags \(Ideal\)(.*?)### Deal-Breakers', content, re.DOTALL)
        if green_flags_match:
            green_text = green_flags_match.group(1)
            # Extract items that start with - **
            matches = re.findall(r'-\s*\*\*([^:]+):\*\*([^-]+)', green_text)
            for title, description in matches:
                priorities.append(f"{title.strip()}: {description.strip()}")

        return priorities

    def _extract_red_flags(self, content: str) -> List[str]:
        """Extract deal-breaker culture attributes."""
        red_flags = []

        red_flags_match = re.search(r'### Deal-Breakers \(Red Flags\)(.*?)### Culture Research', content, re.DOTALL)
        if red_flags_match:
            red_text = red_flags_match.group(1)
            # Extract items that start with - **
            matches = re.findall(r'-\s*\*\*([^:]+):\*\*([^-]+)', red_text)
            for title, description in matches:
                red_flags.append(f"{title.strip()}: {description.strip()}")

        return red_flags

    def _extract_accomplishments(self, content: str) -> List[str]:
        """Extract key accomplishments from experience section."""
        accomplishments = []

        accomplishments_match = re.search(r'\*\*Key Accomplishments:\*\*(.*?)\*\*Why Staying', content, re.DOTALL)
        if accomplishments_match:
            accomp_text = accomplishments_match.group(1)
            # Extract bullet points
            matches = re.findall(r'-\s*\*\*([^:]+):\*\*([^\n]+)', accomp_text)
            for title, description in matches:
                accomplishments.append(f"{title.strip()}: {description.strip()}")

        return accomplishments

    def _extract_resume_anchors(self, content: str) -> Dict[str, List[str]]:
        """Extract resume customization anchors for different role types."""
        anchors = {}

        anchors_match = re.search(r'### Key Accomplishments to Highlight \(Varies by Role\)(.*?)---', content, re.DOTALL)
        if anchors_match:
            anchors_text = anchors_match.group(1)

            # Extract each role type section
            role_sections = re.findall(r'\*\*For ([^:]+):\*\*(.*?)(?=\*\*For |$)', anchors_text, re.DOTALL)
            for role_type, points_text in role_sections:
                role_key = role_type.lower().replace('-focused', '').replace(' roles', '').strip()
                points = [line.strip('- ').strip() for line in points_text.split('\n')
                         if line.strip().startswith('-')]
                anchors[role_key] = points

        return anchors

    def create_embedding(self, force_recreate: bool = False) -> np.ndarray:
        """Create vector embedding for the profile."""
        # Check if embedding already exists
        if PROFILE_EMBEDDING_PATH.exists() and not force_recreate:
            print(f"Loading existing profile embedding from {PROFILE_EMBEDDING_PATH}")
            self.embedding = np.load(PROFILE_EMBEDDING_PATH)
            return self.embedding

        # Parse profile if not already done
        if not self.profile_data:
            self.parse_profile()

        # Create a comprehensive text representation for embedding
        embedding_text = self._create_embedding_text()

        print("Creating profile embedding...")
        self.embedding = self.model.encode(embedding_text, convert_to_numpy=True)

        # Save embedding
        np.save(PROFILE_EMBEDDING_PATH, self.embedding)
        print(f"Profile embedding saved to {PROFILE_EMBEDDING_PATH}")

        return self.embedding

    def _create_embedding_text(self) -> str:
        """Create a focused text representation for embedding.

        Emphasizes technical skills, experience, and key preferences
        for better matching against job descriptions.
        """
        parts = []

        # Technical skills (weighted heavily)
        parts.append("TECHNICAL EXPERTISE:")
        if 'expert' in self.profile_data['technical_skills']:
            parts.append("Expert: " + ", ".join(self.profile_data['technical_skills']['expert']))
        if 'intermediate' in self.profile_data['technical_skills']:
            parts.append("Intermediate: " + ", ".join(self.profile_data['technical_skills']['intermediate']))

        # Key accomplishments
        parts.append("\nKEY ACCOMPLISHMENTS:")
        parts.extend(self.profile_data['accomplishments'][:5])  # Top 5

        # Work preferences
        parts.append("\nWORK PREFERENCES:")
        prefs = self.profile_data['work_preferences']
        if 'salary_min' in prefs:
            parts.append(f"Salary range: ${prefs['salary_min']}-${prefs['salary_max']}")
        if 'remote_preference' in prefs:
            parts.append("Strong preference for remote work")
        if 'location' in prefs:
            parts.append(f"Location: {prefs['location']}")
        if 'preferred_industries' in prefs:
            parts.append(f"Preferred industries: {', '.join(prefs['preferred_industries'])}")

        # Culture priorities (top 3)
        parts.append("\nCULTURE PRIORITIES:")
        parts.extend(self.profile_data['culture_priorities'][:3])

        return "\n".join(parts)

    def get_profile_summary(self) -> str:
        """Get a human-readable summary of the parsed profile."""
        if not self.profile_data:
            self.parse_profile()

        summary = []
        summary.append("=== PROFILE SUMMARY ===\n")

        summary.append("Technical Skills:")
        for tier, skills in self.profile_data['technical_skills'].items():
            summary.append(f"  {tier.title()}: {len(skills)} skills")

        summary.append(f"\nWork Preferences:")
        prefs = self.profile_data['work_preferences']
        if 'salary_min' in prefs:
            summary.append(f"  Salary: ${prefs['salary_min']:,} - ${prefs['salary_max']:,}")
        if 'remote_preference' in prefs:
            summary.append(f"  Remote: {prefs['remote_preference']}")

        summary.append(f"\nCulture Priorities: {len(self.profile_data['culture_priorities'])} items")
        summary.append(f"Red Flags: {len(self.profile_data['red_flags'])} items")
        summary.append(f"Key Accomplishments: {len(self.profile_data['accomplishments'])} items")

        return "\n".join(summary)


if __name__ == "__main__":
    # Test the vectorizer
    vectorizer = ProfileVectorizer()
    profile = vectorizer.parse_profile()
    print(vectorizer.get_profile_summary())

    print("\n" + "="*50)
    print("Creating embedding...")
    embedding = vectorizer.create_embedding()
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding saved successfully!")
