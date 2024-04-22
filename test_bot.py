import unittest
from unittest.mock import patch
from rates import get_rates, format_rate_response
import re

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
        
        rate = get_rates("CNY", "USD")
        print(rate)
        # self.assertEqual(len(rates), 3)
        # self.assertEqual(rates[0]["date"], "2023-04-12")
        # self.assertEqual(rates[0]["rate"], 1.2345)
        
    def test_format_rate_response(self):
        rates = 7.24
        
        response = format_rate_response("USD", "CNY", 100, 5, rates)
        print(response)


    def valide_input_text(self, input_text):
        source = ""
        target = "USD"
        amount = 0
        if len(input_text) == 3:
            if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^\d+$', input_text[2]):
                self.fail('参数错误')
                self.fail()
                return
            source = input_text[1].upper()
            amount = float(input_text[2])
        elif len(input_text) == 4:
            if not re.match(r'^[A-Za-z]{3}$', input_text[1]) or not re.match(r'^[A-Za-z]{3}$', input_text[2]) or not re.match(r'^\d+$', input_text[3]):
                self.fail('参数错误')
                return
            source = input_text[1].upper()
            target = input_text[2].upper()
            amount = float(input_text[3])
        else:
            self.fail('参数错误')
            return 

        print(source, target, amount)

    def test_input_text(self):
        
        self.valide_input_text([ "0", "GBP", "100" ])
        self.valide_input_text([ "0", "GBP", "CNY", "100" ])
        
if __name__ == "__main__":
    unittest.main()