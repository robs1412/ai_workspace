import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from allianz_stop_ship_weekly_report import refresh_candidate_payment_checks


class Qbo:
    def __init__(self, company="KOVAL DISTILLERY", invoice_id="119376", balance=0, fail=False):
        self.company, self.invoice_id, self.balance, self.fail = company, invoice_id, balance, fail
        self.saved = []

    def current_token(self):
        return {}, {}

    def qbo_query(self, config, token, query):
        if "CompanyInfo" in query:
            return {"QueryResponse": {"CompanyInfo": [{"CompanyName": self.company}]}}
        if self.fail:
            raise RuntimeError("QBO unavailable")
        return {"QueryResponse": {"Invoice": [{
            "Id": self.invoice_id, "DocNumber": "6632", "TotalAmt": 4413,
            "Balance": self.balance, "LinkedTxn": [{"TxnId": "121070", "TxnType": "Payment"}],
        }]}}

    def persist_qbo_payment_checks(self, checks):
        self.saved = checks
        return {"saved": len(checks)}


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"payment_check_candidates": [{
            "invoice_number": 8233, "qb_number": 6632, "portal_total": 4398,
            "allianz_payment_check": {"qbo_invoice_id": "119376", "qbo_doc_number": "6632"},
        }]}

    def test_paid_with_fee_discrepancy(self):
        qbo = Qbo()
        result = refresh_candidate_payment_checks(self.payload, qbo)
        self.assertEqual(result["saved"], 1)
        self.assertEqual(qbo.saved[0]["qbo_payment_status"], "PAID")
        self.assertEqual(qbo.saved[0]["status"], "AMOUNT_MISMATCH")

    def test_partial_and_open(self):
        for balance, status in [(100, "PARTIAL"), (4413, "OPEN")]:
            qbo = Qbo(balance=balance)
            refresh_candidate_payment_checks(self.payload, qbo)
            self.assertEqual(qbo.saved[0]["qbo_payment_status"], status)

    def test_failures_abort_before_persistence(self):
        for qbo in [Qbo(company="Other Company"), Qbo(invoice_id="wrong"), Qbo(fail=True), Qbo(balance=None)]:
            with self.assertRaises(RuntimeError):
                refresh_candidate_payment_checks(self.payload, qbo)
            self.assertEqual(qbo.saved, [])

    def test_missing_identity_stays_unverified(self):
        self.payload["payment_check_candidates"][0]["allianz_payment_check"] = {}
        qbo = Qbo()
        result = refresh_candidate_payment_checks(self.payload, qbo)
        self.assertEqual(result["unestablished"], 1)
        self.assertEqual(qbo.saved, [])

    def test_read_only_mode(self):
        qbo = Qbo()
        result = refresh_candidate_payment_checks(self.payload, qbo, persist=False)
        self.assertEqual(result["queried"], 1)
        self.assertEqual(qbo.saved, [])


if __name__ == "__main__":
    unittest.main()
