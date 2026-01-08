#!/usr/bin/env python3
"""
Edge Cases Testing for Character Consistency PoC

This script tests various edge cases that can break character consistency
in multi-agent video generation systems.
"""

import asyncio
import json
import os
from character_consistency_poc import MultiAgentOrchestrator


class EdgeCaseTester:
    """Test various edge cases for the character consistency system"""

    def __init__(self, openai_api_key: str):
        self.orchestrator = MultiAgentOrchestrator(openai_api_key)
        self.orchestrator.initialize_agents()
        self.test_results = []

    async def run_all_tests(self):
        """Run all edge case tests"""
        print("🧪 شروع تست Edge Cases...")
        print("="*60)

        # Test 1: Sudden Character Changes
        await self.test_sudden_character_changes()

        # Test 2: Multiple Characters with Complex Relationships
        await self.test_complex_relationships()

        # Test 3: Inconsistent Character Descriptions
        await self.test_inconsistent_descriptions()

        # Test 4: Character Name Variations
        await self.test_name_variations()

        # Test 5: Empty or Minimal Story
        await self.test_minimal_story()

        # Save results
        self.save_results()

        print("\n✅ همه تست‌ها کامل شد!")
        print(f"📊 نتایج در فایل edge_case_results.json ذخیره شد")

    async def test_sudden_character_changes(self):
        """Test case: Character suddenly changes without explanation"""
        print("\n🔄 تست 1: تغییرات ناگهانی کاراکتر")

        story = """
        محمد یک پسر ۲۵ ساله با موهای سیاه و چشمانی قهوه‌ای بود. او مهندس نرم‌افزار بود و همیشه کت و شلوار می‌پوشید.

        صبح روز بعد، محمد با موهای بلوند و چشمانی آبی از خواب بیدار شد. او حالا معلم مدرسه بود و تیشرت و شلوار جین می‌پوشید.

        محمد به مدرسه رفت و دانش‌آموزانش را salut کرد.
        """

        result = await self.orchestrator.process_story(story)

        # Analyze results
        issues_found = len(result.get("validation", {}).get("validation_results", []))
        consistency_score = result.get("validation", {}).get("overall_consistency", "0%")

        test_result = {
            "test_name": "sudden_character_changes",
            "description": "تغییرات ناگهانی کاراکتر بدون توضیح",
            "input_length": len(story),
            "issues_detected": issues_found,
            "consistency_score": consistency_score,
            "characters_found": len(result.get("characters", [])),
            "scenes_created": len(result.get("scenes", [])),
            "passed": issues_found > 0  # Should detect issues
        }

        self.test_results.append(test_result)
        print(f"   ✅ Issues detected: {issues_found}")
        print(f"   📊 Consistency Score: {consistency_score}")

    async def test_complex_relationships(self):
        """Test case: Multiple characters with complex family relationships"""
        print("\n👨‍👩‍👧‍👦 تست 2: روابط پیچیده خانوادگی")

        story = """
        در خانواده بزرگی زندگی می‌کردند: پدر (احمد، ۵۰ ساله، مهندس)، مادر (فاطمه، ۴۸ ساله، معلم)، پسر بزرگ (علی، ۲۰ ساله، دانشجو)، دختر (مریم، ۱۸ ساله، هنرمند)، و پسر کوچک (حسین، ۱۲ ساله، دانش‌آموز).

        احمد همیشه زود از خواب بیدار می‌شد و صبحانه خانواده را آماده می‌کرد. فاطمه پس از بیدار شدن، به فرزندان کمک می‌کرد تا آماده مدرسه شوند.

        علی، پسر بزرگ، به دانشگاه رفت. مریم در حال نقاشی کردن بود. حسین مشغول بازی با دوستانش بود.

        عصر که خانواده دور هم جمع شدند، احمد از پروژه جدیدش گفت. فاطمه از کلاس‌هایش تعریف کرد. فرزندان هم از روزشان صحبت کردند.
        """

        result = await self.orchestrator.process_story(story)

        characters = result.get("characters", [])
        relationships_total = sum(len(char.get("relationships", {})) for char in characters)

        test_result = {
            "test_name": "complex_relationships",
            "description": "مدیریت روابط پیچیده بین چندین کاراکتر",
            "input_length": len(story),
            "characters_found": len(characters),
            "relationships_tracked": relationships_total,
            "expected_characters": 5,
            "passed": len(characters) >= 4  # Should find most characters
        }

        self.test_results.append(test_result)
        print(f"   ✅ Characters found: {len(characters)}")
        print(f"   🔗 Relationships tracked: {relationships_total}")

    async def test_inconsistent_descriptions(self):
        """Test case: Same character described differently in different scenes"""
        print("\n🎭 تست 3: توصیفات متناقض کاراکتر")

        story = """
        سارا یک دختر ۱۶ ساله با موهای بلند مشکی و چشمانی سبز بود. او همیشه لباس‌های رنگارنگ می‌پوشید و بسیار اجتماعی بود.

        در مدرسه، سارا با موهای کوتاه blond و چشمانی آبی دیده شد. او لباس‌های سیاه می‌پوشید و بسیار introvert بود.

        عصر در پارک، سارا دوباره با موهای بلند مشکی و چشمانی سبز ظاهر شد و با دوستانش بازی می‌کرد.
        """

        result = await self.orchestrator.process_story(story)

        validation_results = result.get("validation", {}).get("validation_results", [])
        has_consistency_issues = any(
            not scene.get("is_consistent", True) for scene in validation_results
        )

        test_result = {
            "test_name": "inconsistent_descriptions",
            "description": "توصیفات متناقض یک کاراکتر در صحنه‌های مختلف",
            "input_length": len(story),
            "consistency_issues_detected": has_consistency_issues,
            "scenes_analyzed": len(validation_results),
            "passed": has_consistency_issues  # Should detect inconsistencies
        }

        self.test_results.append(test_result)
        print(f"   ✅ Consistency issues detected: {has_consistency_issues}")

    async def test_name_variations(self):
        """Test case: Character referred to with different names/variations"""
        print("\n📝 تست 4: تغییرات نام کاراکتر")

        story = """
        دکتر احمد حسینی، متخصص قلب، در بیمارستان مشغول کار بود. آقای حسینی همیشه کتش سفید پزشکی می‌پوشید.

        احمد در اتاق عمل بود و جراحی پیچیده‌ای انجام می‌داد. دکتر حسینی بسیار متمرکز و حرفه‌ای بود.

        بعد از جراحی، آقای احمد با خانواده‌اش ملاقات کرد. او مردی ۴۵ ساله با ریش و چشمانی پشت عینک بود.
        """

        result = await self.orchestrator.process_story(story)

        characters = result.get("characters", [])
        # Check if system recognizes these are the same character
        character_names = [char.get("name", "") for char in characters]
        unique_persons = len(set(character_names))

        test_result = {
            "test_name": "name_variations",
            "description": "تشخیص کاراکتر یکسان با نام‌های مختلف",
            "input_length": len(story),
            "character_names_found": character_names,
            "unique_characters": unique_persons,
            "passed": unique_persons == 1  # Should recognize as one character
        }

        self.test_results.append(test_result)
        print(f"   ✅ Unique characters identified: {unique_persons}")
        print(f"   📋 Names found: {character_names}")

    async def test_minimal_story(self):
        """Test case: Very short story with minimal information"""
        print("\n📖 تست 5: داستان بسیار کوتاه")

        story = "علی رفت公园. سارا آمد. آنها بازی کردند."

        result = await self.orchestrator.process_story(story)

        characters = result.get("characters", [])
        scenes = result.get("scenes", [])

        test_result = {
            "test_name": "minimal_story",
            "description": "پردازش داستان بسیار کوتاه با اطلاعات محدود",
            "input_length": len(story),
            "characters_extracted": len(characters),
            "scenes_created": len(scenes),
            "passed": len(characters) >= 2 and len(scenes) >= 1  # Should extract basic info
        }

        self.test_results.append(test_result)
        print(f"   ✅ Characters extracted: {len(characters)}")
        print(f"   🎬 Scenes created: {len(scenes)}")

    def save_results(self):
        """Save test results to file"""
        summary = {
            "test_timestamp": "2025-01-08T07:30:00",
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for test in self.test_results if test["passed"]),
            "failed_tests": sum(1 for test in self.test_results if not test["passed"]),
            "success_rate": f"{sum(1 for test in self.test_results if test['passed']) / len(self.test_results) * 100:.1f}%",
            "detailed_results": self.test_results
        }

        with open("edge_case_results.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    def print_summary(self):
        """Print test summary"""
        print("\n📊 خلاصه نتایج تست:")
        print("="*40)

        passed = sum(1 for test in self.test_results if test["passed"])
        total = len(self.test_results)

        print(f"کل تست‌ها: {total}")
        print(f"تست‌های موفق: {passed}")
        print(f"تست‌های ناموفق: {total - passed}")
        print(f"درصد موفقیت: {passed/total*100:.1f}%")

        print("\n📋 جزئیات هر تست:")
        for test in self.test_results:
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['test_name']}: {test['description']}")


async def main():
    """Main function to run edge case tests"""

    # Check for API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ خطا: OPENAI_API_KEY تنظیم نشده است")
        print("لطفا متغیر محیطی OPENAI_API_KEY را تنظیم کنید")
        return

    # Run tests
    tester = EdgeCaseTester(openai_api_key)
    await tester.run_all_tests()
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
