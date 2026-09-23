import unittest
from agent import get_latest_ranked_opportunities, get_opportunity_by_title

class TestOpportunityRouterAgent(unittest.TestCase):
    def test_sorted_by_final(self):
        ops = get_latest_ranked_opportunities()
        finals = [op["final"] for op in ops]
        self.assertEqual(finals, sorted(finals, reverse=True))

    def test_limit(self):
        ops = get_latest_ranked_opportunities(limit=3)
        self.assertEqual(len(ops), 3)
        self.assertEqual(ops[0]["final"], 76.2)

    def test_get_by_title(self):
        title = "Amazon Alexa+ + Open Source Hackathon — up to $30,000 cash"
        op = get_opportunity_by_title(title)
        self.assertIsNotNone(op)
        self.assertEqual(op["reward_signal"], 138_000)

    def test_nonexistent_title(self):
        op = get_opportunity_by_title("Nonexistent")
        self.assertIsNone(op)

if __name__ == "__main__":
    unittest.main()
