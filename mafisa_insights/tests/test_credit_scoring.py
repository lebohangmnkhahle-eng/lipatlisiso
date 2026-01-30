import unittest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mafisa_insights.data_models import MSME, Financials
from mafisa_insights.credit_scoring import calculate_credit_score

class TestCreditScoring(unittest.TestCase):
    def setUp(self):
        self.base_fin = Financials(
            monthly_revenue=1000, monthly_expenses=1000,
            inventory_value=0, transaction_frequency=10,
            payment_methods=["Cash"]
        )
        self.base_msme = MSME(
            id="1", name="Test", sector="Retail", location="City",
            years_in_business=1, employee_count=1, contact_info="123",
            financials=self.base_fin
        )

    def test_base_score(self):
        # 300 base
        # + 20 (1 year * 20)
        # + 10 (10 transactions)
        # + 10 (1 employee * 10)
        # Ratio 1.0 -> 0 points
        # No mobile money -> 0
        # Total: 300 + 20 + 10 + 10 = 340
        score, risk = calculate_credit_score(self.base_msme, self.base_fin)
        self.assertEqual(score, 340)
        self.assertEqual(risk, "High Risk")

    def test_high_score(self):
        # 300 base
        # + 100 (5 years * 20 = 100 max)
        # + 50 (5 employees * 10 = 50 max)
        # + 100 (200 transactions -> 100 max)
        # + 50 (Mobile Money)
        # + 100 (Revenue 2000 > Expenses 1000 * 1.5 => ratio 2.0 > 1.5)
        # Total: 300 + 100 + 50 + 100 + 50 + 100 = 700
        fin = Financials(monthly_revenue=2000, monthly_expenses=1000,
                         inventory_value=5000, transaction_frequency=200,
                         payment_methods=["Cash", "Mobile Money"])
        msme = MSME(id="2", name="High", sector="Tech", location="City",
                    years_in_business=5, employee_count=5, contact_info="123", financials=fin)

        score, risk = calculate_credit_score(msme, fin)
        self.assertEqual(score, 700)
        self.assertEqual(risk, "Low Risk")

if __name__ == '__main__':
    unittest.main()
