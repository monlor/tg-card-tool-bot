import unittest
from unittest.mock import patch
from rates import get_rates, format_rate_response

class TestRates(unittest.TestCase):

    @patch('rates.requests.get')
    def test_get_rates(self, mock_get):
        mock_get.return_value.json.return_value = [
            {
                "code": "USD",
                "codein": "CNY",
                "name": "Dólar Americano/Yuan Chinês",
                "high": "7.2429",
                "low": "7.2386",
                "varBid": "0.0022",
                "pctChange": "0.03",
                "bid": "7.2403",
                "ask": "7.2404",
                "timestamp": "1713535833",
                "create_date": "2024-04-19 11:10:33"
            },
            {
                "high": "7.2429",
                "low": "7.2386",
                "varBid": "0.0022",
                "pctChange": "0.03",
                "bid": "7.2403",
                "ask": "7.2404",
                "timestamp": "1713535833"
            },
            {
                "high": "7.2397",
                "low": "7.2333",
                "varBid": "0.0005",
                "pctChange": "0.01",
                "bid": "7.2382",
                "ask": "7.2392",
                "timestamp": "1713464264"
            }
        ]
        
        rates = get_rates("CNY")
        print(rates)
        self.assertEqual(len(rates), 3)
        # self.assertEqual(rates[0]["date"], "2023-04-12")
        # self.assertEqual(rates[0]["rate"], 1.2345)
        
    def test_format_rate_response(self):
        rates = [{'date': '2024-04-19', 'rate': 7.2403}, {'date': '2024-04-19', 'rate': 7.2403}, {'date': '2024-04-19', 'rate': 7.2382}]
        
        response = format_rate_response("CNY", 100, rates)
        print(response)
        
if __name__ == "__main__":
    unittest.main()