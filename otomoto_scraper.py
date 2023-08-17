from bs4 import BeautifulSoup
from urllib.request import urlopen
import ssl 
import certifi
import http.client  
import regex as re
import pandas as pd
import os
from multiprocessing.pool import ThreadPool
from datetime import datetime
import numpy as np
import database

pd.options.mode.copy_on_write = True
pd.options.mode.chained_assignment = None
http.client._MAXHEADERS = 1000


class Links:
    def __init__(self, starting_url : str = "", filename = ""):
        self.url = starting_url
        self.soup = ''
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.file_name = "data\\" + f"otomoto_{self.date}.csv"
        self.headers = ['make', 'model', 'price', 'currency', 'year', 'power', 'mileage',
                        'mileage_unit', 'gearbox', 'eng_cap', 'fuel_type', 'accident', 'date', 'link']


    def get_soup(self):
        r = urlopen(self.url, context=ssl.create_default_context(cafile=certifi.where()))
        self.soup = BeautifulSoup(r, "html.parser")
        
        return self.soup


    def get_listings(self, soup):
        listings = soup.find_all("article", {"class":"ooa-1t80gpj ev7e6t818"})
        
        return listings


    def get_value_and_unit(self, text):
        i = len(text) - 1
        
        while(text[i].isalpha()):
            i=i-1
        
        number = text[:i + 1].replace(" ", "")
        unit = text[i + 1:]
        
        return number, unit
    
    def get_price(self, car):
        price = car.find_all("div", {"class": 'ooa-1wb7q8u ev7e6t814'})[0]
        price = price.text
        
        return price
    
    def get_fuel_type(self, car):
        fuel_type = car.find_all("dd", {"data-parameter": 'fuel_type'})[0]
        fuel_type = fuel_type.text
        
        return fuel_type

    def get_mileage(self, car):
        mileage = car.find_all("dd", {"data-parameter": 'mileage'})[0]
        mileage = mileage.text
        
        return mileage
    
    def get_gearbox(self, car):
        gearbox = car.find_all("dd", {"data-parameter": 'gearbox'})[0]
        gearbox = gearbox.text
        
        return gearbox
    
    def get_year(self, car):
        year = car.find_all("dd", {"data-parameter": 'year'})[0]
        year = int(year.text)
        
        return str(year)
 
    def get_link(self, car):
        pattern = re.compile('(?<=<a href=\")(.*?)(?=\" rel=\"noreferrer\" target=\")')
        link = re.findall(pattern, str(car))[0]
        
        return link
            
    def get_power_engcap_from_info_under_title(self, car):
        info = car.find_all("p", {"class": 'ev7e6t88 ooa-17thc3y er34gjf0'})[0]
        info = info.text
        
        power = 0
        eng_cap = 0
        info = info.split(" • ")[:2]
        for word in info:
            if "KM" in word:
                power = word
            if "cm3" in word:
                eng_cap = word
                
        res = {"power" : power, "eng_cap" : eng_cap}
        
        return res
    
    
    def get_tech_spec(self, soup, make, model, accident, gearbox):
        listings =  self.get_listings(soup)

        price = ""
        specs = {}
        df = pd.DataFrame()
        
        for car in listings:
            link = self.get_link(car)
            price = self.get_price(car)
            year = self.get_year(car)
            fuel_type = self.get_fuel_type(car)
            powercap = self.get_power_engcap_from_info_under_title(car)
            
            try:
                mileage = self.get_mileage(car)
                mileage, mileage_unit = self.get_value_and_unit(mileage)
            except IndexError:
                mileage = 0
                mileage_unit = 'km'
            
            price, currency =  self.get_value_and_unit(price)
                        
            specs = {
                "make" : [make], 
                "model" : [model], 
                "price" : [price],
                "currency" : [currency],
                "year" : [year],
                "power" : [powercap["power"]],
                "mileage" : [mileage],
                "mileage_unit" : [mileage_unit],
                "gearbox" : [gearbox],
                "eng_cap" : [powercap["eng_cap"]],
                "fuel_type" : [fuel_type],
                "accident" : [accident],
                "date" : [self.date],
                "link" : [link],
            }
            temp = pd.DataFrame(specs)
            
            df = pd.concat([df, temp], ignore_index=True)
              
        return df


    def get_make_and_model(self):
        
        brand_pattern = re.compile('(?<=https:\/\/www\.otomoto\.pl\/osobowe\/)(.*?)(?=\/)')
        make = re.search(brand_pattern, self.url)
        make = str(make.group(0))
        
        model_pattern = re.compile(f'(?<=https:\/\/www\.otomoto\.pl\/osobowe\/{make}\/)(.*?)(?=\?)')
        model = re.search(model_pattern, self.url)
        model = str(model.group(0))

        return make, model


    def get_number_of_pages(self):
        pages = self.get_soup().find_all("li", {"data-testid": 'pagination-list-item'})
        page_pattern = re.compile('(?<=<li aria-label=\"Page )(.*?)(?=\" class=\"pagination)')
        page = re.findall(page_pattern, str(pages[-1]))

        return int(page[0])


    def get_listing_df(self):
        
        accident_dic = {"Had accident": 0, "No accident" : 1}
        gearbox_list = ["manual", "automatic"]
        
        car_df = pd.DataFrame()
        for accident in accident_dic.keys():
            for gearbox in gearbox_list:
                postfix = f'?search[filter_enum_gearbox]={gearbox}&search[filter_enum_no_accident]={accident_dic[accident]}'
                self.url = self.url + postfix
                       
                make, model = self.get_make_and_model()
                
                number_of_pages = 1
                try:
                    number_of_pages = self.get_number_of_pages()
                except IndexError:
                    pass
                
                for page in range(1, number_of_pages + 1):
                    
                    self.url = f'{self.url}&page={page}'
                    
                    soup = self.get_soup()
                    scrap_df = self.get_tech_spec(soup, make, model, accident, gearbox)
                    car_df = pd.concat([car_df, scrap_df], ignore_index=True)
                    
                    self.url = self.url.replace(f'&page={page}', '')
                
                self.url = self.url.replace(f'&page={number_of_pages}', '')
                self.url = self.url.replace(postfix, '')

        car_df = car_df.drop_duplicates()
        return car_df

    def make_csv(self, starting_url : str):
        self.url = starting_url
        df = self.get_listing_df()
        df.drop_duplicates(inplace=True)
        
        if os.path.exists(self.file_name):
            df.to_csv(self.file_name, mode = 'a', index = False, header = False)
        else:
            df.to_csv(self.file_name, mode = 'a', index = False, header = self.headers)



def get_df_without_outliers(df, cols):
    df[cols] = df[cols].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()

    for col in cols:
        df.loc[:, ['log']] = np.log(1 + df.loc[:, col]).apply(pd.to_numeric)
        
        q1 = df["log"].quantile(0.25)
        q3 =  df["log"].quantile(0.75)
        
        iqr = q3 - q1
        q_low = q1 - iqr * 1.5
        q_hi  = q3 + iqr * 1.5

        df = df[(df["log"] < q_hi) & (df["log"] > q_low)]
        
        del df["log"]
    
    return df

def remove_outliers(filename = f"otomoto_{datetime.today().strftime('%Y-%m-%d')}.csv"):
    df = pd.read_csv(filename)
    model_list = df["model"].unique()
    accident_list = df["accident"].unique()
    out = pd.DataFrame()
    
    for accident in accident_list:
        accident_df = df[df["accident"] == accident].copy(deep = True)
        
        for model in model_list:
            model_df = accident_df[accident_df["model"] == model].copy(deep = True)
            year_list = model_df["year"].unique()
            
            for year in year_list:
                year_df = model_df[model_df["year"] == year].copy(deep = True)
                power_list = year_df["power"].unique()
                
                for power in power_list:
                    power_df = year_df[year_df["power"] == power].copy(deep = True)
        
                    if power_df.shape[0] < 30:
                        out = pd.concat([power_df, out], axis = 0)
                        continue
                
                    power_df = get_df_without_outliers(power_df, ["mileage", "price"])
                    out = pd.concat([power_df, out], axis = 0)

    out.to_csv("data\\" + filename, index = False)



def main():
    df = pd.read_csv('otomoto_links.csv', sep = ";", dtype = str)
    link_list = df.iloc[:, 0].tolist()
    
    pool = ThreadPool()
    for link in link_list:
        scraper = Links()
        pool.apply_async(scraper.make_csv, (link, ))
    
    pool.close()
    pool.join()
    
    filename = scraper.file_name
    remove_outliers(filename=filename)
    database.uploadToBlobStorage(file_name=filename)

if __name__ == "__main__":
   main()