import unittest
import otomoto_scraper
import pandas as pd

class Link_test(unittest.TestCase):

    def setUp(self):
        print('setUp')
        self.link_taycan = otomoto_scraper.Links("https://www.otomoto.pl/osobowe/porsche/taycan")
        self.link_159 = otomoto_scraper.Links("https://www.otomoto.pl/osobowe/alfa-romeo/159")
        
    def test_get_soup(self):
        print('get_soup')
        self.assertNotEqual(self.link_taycan.get_soup(), '')
        self.assertNotEqual(self.link_159.get_soup(), '')
        
        
    def test_listings(self):
        print('test_listings')
        self.assertNotEqual(self.link_taycan.get_listings(self.link_taycan.get_soup()), '')
        self.assertNotEqual(self.link_159.get_listings(self.link_159.get_soup()), '')
        
        
    def test_get_link(self):
        print("get_link")
        car_taycan = self.link_taycan.get_listings(self.link_taycan.get_soup())[0]
        car_159 = self.link_159.get_listings(self.link_159.get_soup())[0]
        
        self.assertNotEqual(self.link_taycan.get_link(car_taycan), '')
        self.assertNotEqual(self.link_159.get_link(car_159), '')
        
        
    def test_year_fuel_type(self):
        print("year_fuel_type")
        car_taycan = self.link_taycan.get_listings(self.link_taycan.get_soup())[0]
        car_159 = self.link_159.get_listings(self.link_159.get_soup())[0]
        
        self.assertNotEqual(self.link_taycan.get_fuel_type(car_taycan), '')
        self.assertNotEqual(self.link_159.get_fuel_type(car_159), '')
        
        self.assertNotEqual(self.link_taycan.get_year(car_taycan), '')
        self.assertNotEqual(self.link_159.get_year(car_159), '')
        
        
    def test_get_power_engcap_from_info_under_title(self):
        print("get_power_engcap_from_info_under_title")
        car_taycan = self.link_taycan.get_listings(self.link_taycan.get_soup())[0]
        car_159 = self.link_159.get_listings(self.link_159.get_soup())[0]
        
        res = {"power" : 0, "eng_cap" : 0}
        self.assertNotEqual(self.link_taycan.get_power_engcap_from_info_under_title(car_taycan), res)
        self.assertNotEqual(self.link_159.get_power_engcap_from_info_under_title(car_159), res)
    
        
    def test_get_price(self):
        print("get_price")
        car_taycan = self.link_taycan.get_listings(self.link_taycan.get_soup())[0]
        car_159 = self.link_159.get_listings(self.link_159.get_soup())[0]
        
        self.assertNotEqual(self.link_taycan.get_price(car_taycan), "")
        self.assertNotEqual(self.link_159.get_price(car_159), "")
        

    def test_get_number_of_pages(self):
        print('get_number_of_pages')
        self.assertNotEqual(self.link_taycan.get_number_of_pages(), 0)
        self.assertNotEqual(self.link_159.get_number_of_pages(), 0)
    
    
    def test_get_listing_df(self):
        print('get_listing_df')
        self.assertNotEqual(self.link_taycan.get_listing_df().shape[0], 0)
        self.assertNotEqual(self.link_159.get_listing_df().shape[0], 0)
        
        
if __name__ == '__main__':
    unittest.main()