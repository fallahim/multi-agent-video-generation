#!/usr/bin/env python3
"""
PoC for Character Consistency in Multi-Agent Video Generation Systems

This script demonstrates how to maintain character consistency across multiple agents
processing different scenes of a story using shared memory and coordination.
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from transformers import pipeline


@dataclass
class Character:
    """Represents a character with consistent attributes"""
    name: str
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    role: Optional[str] = None
    relationships: Dict[str, str] = None

    def __post_init__(self):
        if self.relationships is None:
            self.relationships = {}

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Scene:
    """Represents a scene in the video storyboard"""
    scene_id: int
    description: str
    characters_present: List[str]
    location: str
    time_of_day: Optional[str] = None
    mood: Optional[str] = None
    key_actions: List[str] = None

    def __post_init__(self):
        if self.key_actions is None:
            self.key_actions = []


class SharedMemory:
    """Simulated shared memory for character consistency"""

    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.scenes: List[Scene] = []
        self.global_context: Dict[str, Any] = {}

    def add_character(self, character: Character):
        """Add or update character in shared memory"""
        self.characters[character.name] = character

    def get_character(self, name: str) -> Optional[Character]:
        """Retrieve character from shared memory"""
        return self.characters.get(name)

    def update_character(self, name: str, **updates):
        """Update character attributes"""
        if name in self.characters:
            char = self.characters[name]
            for key, value in updates.items():
                if hasattr(char, key):
                    setattr(char, key, value)

    def add_scene(self, scene: Scene):
        """Add scene to shared memory"""
        self.scenes.append(scene)

    def get_all_characters(self) -> Dict[str, Character]:
        """Get all characters"""
        return self.characters.copy()

    def get_recent_scenes(self, limit: int = 3) -> List[Scene]:
        """Get recent scenes for context"""
        return self.scenes[-limit:] if self.scenes else []


class StoryProcessingAgent:
    """Base agent for processing story elements"""

    def __init__(self, name: str, generator, shared_memory: SharedMemory):
        self.name = name
        self.generator = generator
        self.shared_memory = shared_memory
        self.memory = []  # Simple list for conversation history

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        raise NotImplementedError


class CharacterExtractionAgent(StoryProcessingAgent):
    """Agent responsible for extracting and maintaining character information"""

    def __init__(self, llm: ChatOpenAI, shared_memory: SharedMemory):
        super().__init__("CharacterExtractor", llm, shared_memory)

        self.prompt = PromptTemplate(
            input_variables=["story_text", "existing_characters"],
            template="""
            شما یک متخصص تحلیل کاراکترهای داستان هستید. از متن داستان زیر، کاراکترها را استخراج کرده و اطلاعات آنها را تحلیل کنید.

            داستان:
            {story_text}

            کاراکترهای موجود تاکنون:
            {existing_characters}

            لطفا برای هر کاراکتر جدید یا بروزرسانی کاراکتر موجود، اطلاعات زیر را استخراج کنید:
            - نام
            - سن (اگر مشخص شده)
            - ظاهر (توضیح فیزیکی)
            - شخصیت (ویژگی‌های رفتاری)
            - نقش در داستان
            - روابط با دیگر کاراکترها

            خروجی را به صورت JSON بدهید:
            {{
                "characters": [
                    {{
                        "name": "نام کاراکتر",
                        "age": عدد یا null,
                        "appearance": "توضیح ظاهر",
                        "personality": "توضیح شخصیت",
                        "role": "نقش در داستان",
                        "relationships": {{"نام_دیگری": "نوع_رابطه"}}
                    }}
                ]
            }}
            """
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        existing_chars = self.shared_memory.get_all_characters()
        existing_chars_json = json.dumps(
            [char.to_dict() for char in existing_chars.values()],
            ensure_ascii=False,
            indent=2
        )

        # Create prompt
        prompt_text = self.prompt.format(
            story_text=input_data["story_text"],
            existing_characters=existing_chars_json
        )

        # Generate response using local model
        outputs = self.generator(prompt_text, max_new_tokens=256, do_sample=True, temperature=0.7)
        result = outputs[0]['generated_text']

        # Extract JSON from response (simple approach)
        try:
            # Try to find JSON in the response
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                parsed_result = json.loads(json_str)

                # Update shared memory with new characters
                for char_data in parsed_result.get("characters", []):
                    char = Character(**char_data)
                    self.shared_memory.add_character(char)

                return {"characters_extracted": len(parsed_result.get("characters", []))}
            else:
                return {"error": "No JSON found in response", "raw_response": result[:500]}
        except json.JSONDecodeError:
            return {"error": "Failed to parse character extraction result", "raw_response": result[:500]}


class ScenePlanningAgent(StoryProcessingAgent):
    """Agent responsible for breaking story into consistent scenes"""

    def __init__(self, llm: ChatOpenAI, shared_memory: SharedMemory):
        super().__init__("ScenePlanner", llm, shared_memory)

        self.prompt = PromptTemplate(
            input_variables=["story_text", "characters_info", "previous_scenes"],
            template="""
            شما یک کارگردان فیلم هستید که داستان را به صحنه‌های ویدیو تبدیل می‌کنید.
            داستان را به صحنه‌های منطقی تقسیم کنید و از consistency کاراکترها اطمینان حاصل کنید.

            داستان:
            {story_text}

            اطلاعات کاراکترها:
            {characters_info}

            صحنه‌های قبلی:
            {previous_scenes}

            برای هر صحنه، اطلاعات زیر را مشخص کنید:
            - شماره صحنه
            - توصیف صحنه
            - کاراکترهای حاضر
            - موقعیت مکانی
            - زمان روز
            - حال و هوا
            - اقدامات کلیدی

            اطمینان حاصل کنید که ظاهر و رفتار کاراکترها با اطلاعات موجود consistency دارد.

            خروجی را به صورت JSON بدهید:
            {{
                "scenes": [
                    {{
                        "scene_id": عدد,
                        "description": "توضیح صحنه",
                        "characters_present": ["نام1", "نام2"],
                        "location": "موقعیت",
                        "time_of_day": "صبح/عصر/شب",
                        "mood": "حال و هوا",
                        "key_actions": ["اقدام1", "اقدام2"]
                    }}
                ]
            }}
            """
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        characters = self.shared_memory.get_all_characters()
        characters_json = json.dumps(
            [char.to_dict() for char in characters.values()],
            ensure_ascii=False,
            indent=2
        )

        recent_scenes = self.shared_memory.get_recent_scenes()
        scenes_json = json.dumps(
            [asdict(scene) for scene in recent_scenes],
            ensure_ascii=False,
            indent=2
        )

        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        result = await chain.arun(
            story_text=input_data["story_text"],
            characters_info=characters_json,
            previous_scenes=scenes_json
        )

        try:
            parsed_result = json.loads(result)
            # Add scenes to shared memory
            for scene_data in parsed_result.get("scenes", []):
                scene = Scene(**scene_data)
                self.shared_memory.add_scene(scene)

            return {"scenes_planned": len(parsed_result.get("scenes", []))}
        except json.JSONDecodeError:
            return {"error": "Failed to parse scene planning result"}


class ConsistencyValidationAgent(StoryProcessingAgent):
    """Agent responsible for validating character consistency across scenes"""

    def __init__(self, llm: ChatOpenAI, shared_memory: SharedMemory):
        super().__init__("ConsistencyValidator", llm, shared_memory)

        self.prompt = PromptTemplate(
            input_variables=["scenes", "characters_info"],
            template="""
            شما یک validator consistency هستید. صحنه‌های زیر را بررسی کنید و اطمینان حاصل کنید که کاراکترها در همه صحنه‌ها consistent هستند.

            اطلاعات کاراکترها:
            {characters_info}

            صحنه‌ها:
            {scenes}

            برای هر inconsistency، مشکل را شناسایی کرده و پیشنهاد اصلاح بدهید.

            خروجی را به صورت JSON بدهید:
            {{
                "validation_results": [
                    {{
                        "scene_id": عدد,
                        "is_consistent": true/false,
                        "issues": ["مشکل1", "مشکل2"],
                        "suggestions": ["پیشنهاد1", "پیشنهاد2"]
                    }}
                ],
                "overall_consistency": "نسبت consistency کلی (مثال: 85%)"
            }}
            """
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        characters = self.shared_memory.get_all_characters()
        characters_json = json.dumps(
            [char.to_dict() for char in characters.values()],
            ensure_ascii=False,
            indent=2
        )

        scenes = self.shared_memory.scenes
        scenes_json = json.dumps(
            [asdict(scene) for scene in scenes],
            ensure_ascii=False,
            indent=2
        )

        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        result = await chain.arun(
            characters_info=characters_json,
            scenes=scenes_json
        )

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Failed to parse validation result"}


class MultiAgentOrchestrator:
    """Orchestrates the multi-agent system for video generation"""

    def __init__(self):
        # Use local GPT-2 model (no API key required)
        print("🔄 Loading local GPT-2 model... (this may take a moment)")
        self.generator = pipeline(
            "text-generation",
            model="gpt2",
            max_new_tokens=256,  # Limit output length
            temperature=0.7,
            do_sample=True,
            pad_token_id=50256,
            repetition_penalty=1.1  # Reduce repetition
        )
        self.shared_memory = SharedMemory()
        self.agents = {}

    def initialize_agents(self):
        """Initialize all agents"""
        self.agents["character_extractor"] = CharacterExtractionAgent(
            self.generator, self.shared_memory
        )
        self.agents["scene_planner"] = ScenePlanningAgent(
            self.generator, self.shared_memory
        )
        self.agents["consistency_validator"] = ConsistencyValidationAgent(
            self.generator, self.shared_memory
        )

    async def process_story(self, story_text: str) -> Dict[str, Any]:
        """Process a story through the multi-agent pipeline"""

        print("🚀 شروع پردازش داستان...")
        print(f"📖 طول داستان: {len(story_text)} کاراکتر")

        # Phase 1: Character Extraction
        print("\n📝 مرحله 1: استخراج کاراکترها...")
        char_result = await self.agents["character_extractor"].process({
            "story_text": story_text
        })
        print(f"✅ {char_result.get('characters_extracted', 0)} کاراکتر استخراج شد")

        # Phase 2: Scene Planning
        print("\n🎬 مرحله 2: برنامه‌ریزی صحنه‌ها...")
        scene_result = await self.agents["scene_planner"].process({
            "story_text": story_text
        })
        print(f"✅ {scene_result.get('scenes_planned', 0)} صحنه برنامه‌ریزی شد")

        # Phase 3: Consistency Validation
        print("\n🔍 مرحله 3: بررسی consistency...")
        validation_result = await self.agents["consistency_validator"].process({})
        consistency_score = validation_result.get("overall_consistency", "نامشخص")
        print(f"✅ امتیاز consistency: {consistency_score}")

        # Prepare final output
        output = {
            "metadata": {
                "processing_timestamp": datetime.now().isoformat(),
                "story_length": len(story_text),
                "agents_used": list(self.agents.keys())
            },
            "characters": [char.to_dict() for char in self.shared_memory.characters.values()],
            "scenes": [asdict(scene) for scene in self.shared_memory.scenes],
            "validation": validation_result,
            "summary": {
                "total_characters": len(self.shared_memory.characters),
                "total_scenes": len(self.shared_memory.scenes),
                "consistency_score": consistency_score
            }
        }

        print("\n🎉 پردازش کامل شد!")
        return output


async def main():
    """Main function to demonstrate the PoC"""

    print("🚀 شروع سیستم Multi-Agent با مدل محلی GPT-2")
    print("📝 نیازی به API key نیست - از مدل محلی استفاده می‌شود")

    # Initialize orchestrator (no API key needed)
    orchestrator = MultiAgentOrchestrator()
    orchestrator.initialize_agents()

    # Sample story (Persian)
    sample_story = """
    در شهری بزرگ، پسرکی به نام علی زندگی می‌کرد. علی ۱۲ ساله بود و موهای سیاه و چشمانی باهوش داشت.
    او همیشه ماجراجو و کنجکاو بود. یک روز علی تصمیم گرفت به公园 برود و ماجراجویی کند.

    در پارک، علی با دختری به نام سارا آشنا شد. سارا ۱۱ ساله بود و موهای بلوند و چشمانی آبی داشت.
    او آرام و کتابخوان بود. آنها با هم شروع به بازی کردند و دوستی نزدیکی پیدا کردند.

    ناگهان هوا ابری شد و باران شروع به باریدن کرد. علی و سارا زیر درختی پناه گرفتند.
    علی با وجود ترس از رعد و برق، سعی کرد سارا را آرام کند. سارا هم با خواندن داستان، جو را بهتر کرد.

    بعد از گذشت باران، آنها به خانه‌هایشان برگشتند و قول دادند دوباره همدیگر را ببینند.
    """

    print("📚 داستان نمونه:")
    print(sample_story)
    print("\n" + "="*50)

    # Process the story
    result = await orchestrator.process_story(sample_story)

    # Save results
    output_file = "storyboard_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 نتیجه در فایل {output_file} ذخیره شد")

    # Display summary
    print("\n📊 خلاصه نتایج:")
    print(f"• تعداد کاراکترها: {result['summary']['total_characters']}")
    print(f"• تعداد صحنه‌ها: {result['summary']['total_scenes']}")
    print(f"• امتیاز consistency: {result['summary']['consistency_score']}")


if __name__ == "__main__":
    # Set up event loop for async execution
    asyncio.run(main())
