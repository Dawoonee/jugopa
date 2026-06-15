from django.test import SimpleTestCase

from news.selection import classify_text, select_sectors


class ClassifyTextTests(SimpleTestCase):
    SECTOR_KEYWORDS = {
        "반도체": ["반도체", "HBM", "엔비디아"],
        "2차전지": ["배터리", "양극재"],
        "금융": ["금리", "은행"],
    }

    def test_single_match(self):
        result = classify_text("엔비디아 실적 호조에 반도체주 강세", self.SECTOR_KEYWORDS)
        self.assertEqual(set(result), {"반도체"})

    def test_multiple_matches(self):
        result = classify_text("배터리 업체 금리 부담 확대", self.SECTOR_KEYWORDS)
        self.assertEqual(set(result), {"2차전지", "금융"})

    def test_no_match_returns_empty(self):
        self.assertEqual(classify_text("날씨가 맑습니다", self.SECTOR_KEYWORDS), [])

    def test_case_insensitive(self):
        self.assertEqual(classify_text("hbm 수요 급증", self.SECTOR_KEYWORDS), ["반도체"])


class SelectSectorsTests(SimpleTestCase):
    def test_picks_top_four_above_threshold(self):
        counts = {"A": 10, "B": 8, "C": 6, "D": 4, "E": 3}
        selected = select_sectors(counts)
        self.assertEqual(selected, ["A", "B", "C", "D"])  # 최대 4개

    def test_orders_by_score_when_provided(self):
        counts = {"A": 5, "B": 5, "C": 5}
        scores = {"A": 1.0, "B": 9.0, "C": 5.0}
        self.assertEqual(select_sectors(counts, scores), ["B", "C", "A"])

    def test_excludes_below_threshold_but_keeps_min_two(self):
        # 임계치(3) 이상은 A 하나뿐 → 최소 2개 보장을 위해 B를 채운다.
        counts = {"A": 5, "B": 2, "C": 1}
        selected = select_sectors(counts)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0], "A")
        self.assertEqual(selected[1], "B")  # 점수 차순으로 다음 후보

    def test_no_qualified_fills_min_two(self):
        counts = {"A": 2, "B": 1}
        selected = select_sectors(counts)
        self.assertEqual(selected, ["A", "B"])

    def test_returns_all_when_fewer_than_min(self):
        counts = {"A": 1}
        self.assertEqual(select_sectors(counts), ["A"])

    def test_respects_max_n(self):
        counts = {n: 5 for n in "ABCDEF"}
        self.assertEqual(len(select_sectors(counts)), 4)
