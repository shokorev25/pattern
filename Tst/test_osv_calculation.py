import unittest
from datetime import datetime as dt
from Src.start_service import start_service
from Src.settings_manager import settings_manager
from Src.Core.prototype import prototype

class TestOSVCalculation(unittest.TestCase):
    def setUp(self):
        self.service = start_service()
        self.service.start()
        self.transactions = self.service.data['transaction_key']
        self.settings = settings_manager().settings

    def test_osv_independent_of_block_period(self):
        target_date = dt.strptime("2024-10-01", "%Y-%m-%d").date()
        full_osv = prototype.generate_osv(self.transactions)

        for block_str in ["2023-01-01", "2023-06-01"]:
            block_date = dt.strptime(block_str, "%Y-%m-%d").date()
            self.settings.block_period = block_date
            osv_up_to_block = prototype.generate_osv_up_to_block(self.transactions, block_date)
            prototype.save_blocked_osv(osv_up_to_block)
            combined_osv = prototype.generate_osv_with_block(self.transactions, target_date, block_date)
            self.assertEqual(sorted(full_osv, key=lambda x: x['nomenclature_id']), 
                             sorted(combined_osv, key=lambda x: x['nomenclature_id']))