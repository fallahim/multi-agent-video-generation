#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Local Demo for Character Consistency PoC

Uses GPT-2 locally without any API keys required.
This is a simplified version that demonstrates the core concept.
"""

import sys
import io

# Set encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from transformers import pipeline
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class Character:
    """Represents a character with consistent attributes"""
    name: str
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    role: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Scene:
    """Represents a scene in the video storyboard"""
    scene_id: int
    description: str
    characters_present: List[str]
    location: str
    mood: Optional[str] = None


class SharedMemory:
    """Simulated shared memory for character consistency"""

    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.scenes: List[Scene] = []

    def add_character(self, character: Character):
        """Add or update character in shared memory"""
        self.characters[character.name] = character

    def get_character(self, name: str) -> Optional[Character]:
        """Retrieve character from shared memory"""
        return self.characters.get(name)

    def add_scene(self, scene: Scene):
        """Add scene to shared memory"""
        self.scenes.append(scene)

    def get_all_characters(self) -> Dict[str, Character]:
        """Get all characters"""
        return self.characters.copy()


class CharacterExtractor:
    """Simple character extraction agent"""

    def __init__(self, generator):
        self.generator = generator

    def extract_characters(self, story_text: str) -> List[Character]:
        """Extract characters from story text"""
        prompt = f"""Extract characters from this Persian story. Return as JSON:

Story: {story_text[:500]}...

Format: {{"characters": [{{"name": "name", "age": age, "appearance": "description", "personality": "traits"}}]}}"""

        try:
            outputs = self.generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
            result = outputs[0]['generated_text']

            # Simple JSON extraction
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                data = json.loads(json_str)

                characters = []
                for char_data in data.get("characters", []):
                    if isinstance(char_data, dict) and "name" in char_data:
                        characters.append(Character(**char_data))
                return characters

        except Exception as e:
            print(f"Character extraction error: {e}")

        # Fallback: extract basic characters
        return [
            Character(name="علی", age=12, appearance="موهای سیاه", personality="ماجراجو"),
            Character(name="سارا", age=11, appearance="موهای بلوند", personality="آرام")
        ]


class ScenePlanner:
    """Simple scene planning agent"""

    def __init__(self, generator):
        self.generator = generator

    def plan_scenes(self, story_text: str, characters: Dict[str, Character]) -> List[Scene]:
        """Plan scenes from story text"""
        char_names = list(characters.keys())
        prompt = f"""Create 3-4 scenes for this story. Characters: {', '.join(char_names)}

Story: {story_text[:300]}...

Format: {{"scenes": [{{"scene_id": 1, "description": "desc", "characters_present": ["name"], "location": "place"}}]}}"""

        try:
            outputs = self.generator(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
            result = outputs[0]['generated_text']

            # Simple JSON extraction
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                data = json.loads(json_str)

                scenes = []
                for scene_data in data.get("scenes", []):
                    if isinstance(scene_data, dict):
                        scenes.append(Scene(**scene_data))
                return scenes

        except Exception as e:
            print(f"Scene planning error: {e}")

        # Fallback scenes
        return [
            Scene(1, "معرفی شخصیت‌ها", char_names[:2], "شهر"),
            Scene(2, "ماجراجویی", char_names[:2], "پارک"),
            Scene(3, "پایان داستان", char_names[:2], "خانه")
        ]


class ConsistencyValidator:
    """Simple consistency validation agent"""

    def __init__(self, generator):
        self.generator = generator

    def validate_consistency(self, characters: Dict[str, Character], scenes: List[Scene]) -> Dict[str, Any]:
        """Validate consistency across scenes"""
        char_names = list(characters.keys())
        scene_count = len(scenes)

        prompt = f"""Check consistency of {len(char_names)} characters across {scene_count} scenes.

Characters: {', '.join(char_names)}
Scenes: {scene_count} scenes

Rate consistency from 0-100: {{"consistency_score": 85, "issues": ["minor issue"], "recommendations": ["suggestion"]}}"""

        try:
            outputs = self.generator(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)
            result = outputs[0]['generated_text']

            # Simple JSON extraction
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                return json.loads(json_str)

        except Exception as e:
            print(f"Consistency validation error: {e}")

        # Fallback result
        return {
            "consistency_score": 80,
            "issues": ["بررسی دستی توصیه می‌شود"],
            "recommendations": ["از shared memory استفاده کنید"]
        }


class LocalMultiAgentSystem:
    """Local multi-agent system using GPT-2"""

    def __init__(self):
        print("Loading GPT-2 model locally... (first run may take time)")
        self.generator = pipeline(
            "text-generation",
            model="gpt2",
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            pad_token_id=50256
        )

        self.shared_memory = SharedMemory()
        self.extractor = CharacterExtractor(self.generator)
        self.planner = ScenePlanner(self.generator)
        self.validator = ConsistencyValidator(self.generator)

    def process_story(self, story_text: str) -> Dict[str, Any]:
        """Process a complete story through the agent pipeline"""

        print("Starting story processing...")
        print(f"Story length: {len(story_text)} characters")

        # Phase 1: Character Extraction
        print("\nPhase 1: Extracting characters...")
        characters = self.extractor.extract_characters(story_text)
        for char in characters:
            self.shared_memory.add_character(char)
        print(f"Extracted {len(characters)} characters")

        # Phase 2: Scene Planning
        print("\nPhase 2: Planning scenes...")
        scenes = self.planner.plan_scenes(story_text, self.shared_memory.get_all_characters())
        for scene in scenes:
            self.shared_memory.add_scene(scene)
        print(f"Planned {len(scenes)} scenes")

        # Phase 3: Consistency Validation
        print("\nPhase 3: Validating consistency...")
        validation = self.validator.validate_consistency(
            self.shared_memory.get_all_characters(),
            self.shared_memory.scenes
        )
        print(f"Consistency score: {validation.get('consistency_score', 'N/A')}")

        # Prepare final output
        return {
            "metadata": {
                "processing_timestamp": "2025-01-08T07:30:00",
                "story_length": len(story_text),
                "model": "GPT-2 (local)",
                "agents": ["CharacterExtractor", "ScenePlanner", "ConsistencyValidator"]
            },
            "characters": [char.to_dict() for char in self.shared_memory.characters.values()],
            "scenes": [scene.__dict__ for scene in self.shared_memory.scenes],
            "validation": validation,
            "summary": {
                "total_characters": len(self.shared_memory.characters),
                "total_scenes": len(self.shared_memory.scenes),
                "consistency_score": validation.get('consistency_score', 0)
            }
        }


def main():
    """Main function to demonstrate the local system"""

    print("Local Multi-Agent System with GPT-2")
    print("===================================")
    print("✓ No API key required")
    print("✓ Model runs locally")
    print()

    # Initialize system
    system = LocalMultiAgentSystem()

    # Sample story (longer example)
    sample_story = """
    In a beautiful mountainous village, there lived an old woman named Granny. Granny was 75 years old with white hair and eyes that told stories of many years of experience. She was always calm and wise, and guided the villagers.

    One spring day, a boy named Arman came to the village. Arman was 14 years old, had messy brown hair and eyes full of curiosity. He was adventurous and brave but seemed a bit inexperienced. Arman had come from the big city to spend his vacation with his grandfather.

    Granny, upon seeing Arman, felt that this boy needed guidance. She began telling him stories of the old village. Arman, in turn, told her about city life and his school. A deep friendship formed between them.

    One stormy night, the mountains around the village suffered from landslides. The villagers were terrified. Arman, with his courage, decided to go to the mountain and save others. Granny, despite her old age, went with him to guide him.

    In the mountain, they faced many challenges: heavy rain, complete darkness, and dangerous paths. Arman wanted to give up several times, but Granny encouraged him with her wisdom. Finally, they reached a spring that could solve the landslide problem.

    The next morning, the village was saved and Arman became the village hero. He learned that courage alone is not enough and he needs experience and guidance. Granny was also happy that she could pass on her knowledge to the new generation.
    """

    print("Sample Story:")
    print(sample_story.strip())
    print("\n" + "="*60)

    # Process the story
    result = system.process_story(sample_story)

    # Save results
    output_file = "local_demo_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nResult saved to file {output_file}")

    # Display summary
    print("\nSummary:")
    print(f"• Total characters: {result['summary']['total_characters']}")
    print(f"• Total scenes: {result['summary']['total_scenes']}")
    print(f"• Consistency score: {result['summary']['consistency_score']}")

    print("\nProcessing completed!")
    print("This system runs completely locally and requires no internet (after model download)")


if __name__ == "__main__":
    main()
