import unittest

import main


class NarrativeMaterialScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = main.load_narrative_materials_config()

    def score(self, title, rank=1, source_id="douyin"):
        return main.score_narrative_material(
            title,
            source_id,
            "抖音" if source_id == "douyin" else source_id,
            {"ranks": [rank], "count": 1, "url": "https://example.com/source"},
            False,
            self.config,
        )

    def test_reference_topics_are_worth_doing(self):
        titles = [
            "5万人小城一天涌入10万游客",
            "阿尔山200元简陋大酒店",
            "两匹马跑进城市",
            "小孩拿新能源汽车充电枪荡秋千",
            "把暑假作业做成蛋挞",
            "AI给乐山大佛掏耳朵",
        ]
        for title in titles:
            with self.subTest(title=title):
                result = self.score(title)
                self.assertEqual("worth_doing", result["tier"])
                self.assertTrue(result["requires_original_video_review"])

    def test_high_heat_without_signal_is_kept_for_review(self):
        result = self.score("某球队获得比赛胜利")
        self.assertEqual("reserve", result["tier"])
        self.assertEqual([], result["matched_dimensions"])

    def test_low_heat_without_signal_is_not_recommended(self):
        result = self.score("某球队获得比赛胜利", rank=20)
        self.assertEqual("not_recommended", result["tier"])
        self.assertEqual([], result["matched_dimensions"])

    def test_official_sports_punishment_is_not_promoted_to_worth_doing(self):
        result = self.score("葡萄牙足协公布C罗处罚结果", source_id="weibo")
        self.assertNotEqual("worth_doing", result["tier"])

    def test_douyin_link_is_not_claimed_as_original_video(self):
        self.assertEqual("hot_topic_page", self.score("两匹马跑进城市")["link_type"])

    def test_discussion_source_is_capped_as_a_lead(self):
        result = self.score("5万人小城一天涌入10万游客", source_id="zhihu")
        self.assertEqual("reserve", result["tier"])
        self.assertEqual("可备选", result["recommendation"])

    def test_builder_deduplicates_same_title(self):
        title = "两匹马跑进城市"
        results = {
            "douyin": {title: {"ranks": [3], "url": "https://example.com/d"}},
            "weibo": {title: {"ranks": [5], "url": "https://example.com/w"}},
        }
        info = {
            "douyin": {title: {"ranks": [3], "count": 1}},
            "weibo": {title: {"ranks": [5], "count": 1}},
        }
        output = main.build_narrative_materials(
            results, {"douyin": "抖音", "weibo": "微博"}, info,
            scoring_config=self.config,
        )
        self.assertEqual(1, output["summary"]["total_scanned"])
        self.assertEqual("抖音", output["worth_doing"][0]["source"])
        self.assertIn("微博", output["worth_doing"][0]["also_seen_on"])


if __name__ == "__main__":
    unittest.main()
