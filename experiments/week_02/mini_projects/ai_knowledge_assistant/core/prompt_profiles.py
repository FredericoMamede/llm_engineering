"""
Prompt profiles: load and serve system/task profiles from YAML.

Profiles capture different “thinking styles”:
- Concise Expert
- Teaching Mode
- Reviewer Mode
"""

from pathlib import Path
from typing import Dict

import yaml


class PromptProfiles:
    """Loader and accessor for profile prompts."""

    def __init__(self) -> None:
        self.base: Dict = {}
        self.profiles: Dict[str, Dict] = {}

    def load(self, base_dir: str) -> None:
        """
        Load base and profile YAML files.

        Args:
            base_dir: Directory containing base.yaml and profiles.yaml
        """
        base_path = Path(base_dir) / "base.yaml"
        profiles_path = Path(base_dir) / "profiles.yaml"

        if base_path.exists():
            with open(base_path, "r", encoding="utf-8") as f:
                self.base = yaml.safe_load(f) or {}
        else:
            self.base = {}

        if profiles_path.exists():
            with open(profiles_path, "r", encoding="utf-8") as f:
                self.profiles = yaml.safe_load(f) or {}
        else:
            self.profiles = {}

    def available(self):
        return list(self.profiles.keys())

    def get(self, name: str) -> Dict:
        """Return a profile dict; falls back to the first available."""
        if name in self.profiles:
            return self.profiles[name]
        if self.profiles:
            return next(iter(self.profiles.values()))
        return {}

    def build_system_prompt(self, profile_name: str) -> str:
        """Compose the system prompt from base + profile metadata."""
        base_system = self.base.get("base_system", "").strip()
        profile = self.get(profile_name)
        desc = profile.get("description", "")
        tone = profile.get("tone", "")
        focus = profile.get("output_focus", [])

        parts = [base_system]
        if desc:
            parts.append(f"Profile: {desc}")
        if tone:
            parts.append(f"Tone: {tone}")
        if focus:
            parts.append("Focus on: " + ", ".join(focus))

        return "\n".join([p for p in parts if p])
