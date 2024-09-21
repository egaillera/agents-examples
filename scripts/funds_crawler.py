import os
from altair import Description
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from numpy import average
import requests
import time
import json
import sqlite3
import re

def format_number(number_as_string):

    # If there are digits, remove other chars from the string
    # and convert it to a float
    if any(i.isdigit() for i in number_as_string):
        number = re.sub(r'[a-zA-Z\s\.\%]', '', number_as_string)
        number = number.replace(',', '.')
        return float(number)
    else:
        return None

def create_database():

    os.remove('./dbfunds_new.db')
    conn = sqlite3.connect('./dbfunds_new.db')
    c = conn.cursor()

    # Create funds table
    c.execute('''CREATE TABLE funds (
                isin TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                net_asset_value NUMERIC,
                assets_under_management NUMERIC,
                average_return NUMERIC,
                volatility NUMERIC,
                minimum_investment NUMERIC
                )''')
    
    # Create yearly rentabiliy table
    c.execute('''CREATE TABLE annual_return (
                ID INTEGER PRIMARY KEY,
                isin TEXT,
                year NUMERIC,
                annual_yield NUMERIC
                )''')
    
    # Create accumulated rentability table
    c.execute('''CREATE TABLE cumulative_return (
                ID INTEGER PRIMARY KEY,
                isin TEXT,
                period TEXT,
                return NUMERIC
                )''')
    
    return conn,c

def close_database(conn):
    conn.commit()
    conn.close()

    print("Funds database created and populated")

def insert_fund_data(cursor,isin,nombre,descripcion,valor_liquidativo,patrimonio,
                     rentabilidad_media,volatilidad,aportacion_minima):

    cursor.execute('''INSERT INTO funds (isin, name, description, net_asset_value, assets_under_management,
                    average_return, volatility, minimum_investment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (isin,nombre,descripcion,valor_liquidativo,patrimonio,rentabilidad_media,
                     volatilidad,aportacion_minima))
    

def insert_rentabilities(cursor,isin,year_rentability, acc_rentability):

    for year in year_rentability.keys():
        cursor.execute('''INSERT INTO annual_return (isin, year, annual_yield) 
                        VALUES (?, ?, ?)''',
                        (isin,year,year_rentability[year]))
        
    for period in acc_rentability.keys():
        cursor.execute('''INSERT INTO cumulative_return (ISIN, period, return) 
                        VALUES (?, ?, ?)''',
                        (isin,period,acc_rentability[period]))



def get_isin(docs_path,filename):
    pdf_reader = PdfReader(docs_path+"/"+filename)
    for page in pdf_reader.pages:
       index = page.extract_text().find("ISIN:")
       if index > 0:
           isin = page.extract_text()[index+5:index+18]
           print(f"{filename} --> ISIN: {isin}")
    
    return isin

def get_fund_description(soup):
    description = soup.find("p", class_="coment").text.strip()
    return description

def get_liquidity_value(soup):
    liq_span = soup.find("span",string="Valor liquidativo: ")
    liq_value = liq_span.find_next_sibling('span', class_='floatright').text.strip()
    return format_number(liq_value)

def get_assets_value(soup):
    assets_span = soup.find("span",string="Patrimonio (miles de euros):")
    assets_value = assets_span.find_next_sibling('span', class_='floatright').text.strip()
    return format_number(assets_value)

def get_average_rentability(soup):
    avg_rent_span = soup.find(lambda tag: tag.name == 'span' and 'Rentabilidad media' in tag.text)
    avg_rentability = avg_rent_span.find_next_sibling('span', class_='floatright').text.strip()
    return format_number(avg_rentability)

def get_volatility(soup):
    vol_span = soup.find(lambda tag: tag.name == 'span' and 'Volatilidad' in tag.text)
    volatibility = vol_span.find_next_sibling('span', class_='floatright').text.strip()
    return format_number(volatibility)

def get_mininum_investment(soup):
    min_inv_span = soup.find(lambda tag: tag.name == 'span' and 'Aportación mínima' in tag.text)
    minium_investment = min_inv_span.find_next_sibling('span', class_='floatright').text.strip()
    return format_number(minium_investment)

def get_rentabilities(soup,type="year"):

    if type == "year":
        table_name = "tabla de informe: Rentabilidades anuales"
        index = [2024,2023,2022,2021,2020]
    else:
        table_name = "tabla de informe: Rentabilidades acumuladas"
        index = ["1 month", "3 months", "1 year", "3 years", "5 years"]

    current_year = 2024
    year_rentabilities = {}

    rent_table = soup.find('caption',string=table_name).find_parent('table')
    rows = rent_table.find_all('tr')
    rent_cells = rows[2].find_all('td')
    i = 0
    for cell in rent_cells[1:]:
        year_rentabilities[index[i]] = format_number(cell.text.strip())
        i += 1

    return year_rentabilities

def get_fund_evolution_data(soup):

    evolution_data = {}

    panel_evolucion_div = soup.find('div', class_='panel_evolucion')
    script_tag = panel_evolucion_div.find('script')
    script_content = script_tag.string
    if script_content:
        lines = script_content.split('\n')
        for line in lines:
            if 'var fondo =' in line:
                data_values = line.split('=')[1].strip()
                break

    # Convert string data_values to a list of list, and then
    # to a dictionary with pairs (date,value)
    data_values_list = json.loads(data_values[:-1])
    for point in data_values_list:
        evolution_data[point[0]] = format_number(point[1])

    return evolution_data


def main():

    load_dotenv()
    docs_path = os.getenv('FUNDS_DOC_PATH')

    conn, cursor = create_database()

    # Read fund documents to find the ISIN CODE
    # of each fund. Then scrap info from website
    i = 0
    for filename in os.listdir(docs_path):

        try:
            isin = get_isin(docs_path,filename)
            url = "https://www.quefondos.com/es/fondos/ficha/index.html?isin=" + isin
            page = requests.get(url)
            soup = BeautifulSoup(page.content,"html.parser")
        except:
            print("----> Error processing " + filename)
            continue

        # Check if web responds
        if page.status_code != 200:
            print("---> Server error")
            continue

        # Check if fund exists
        if soup.find(string=re.compile("No se encuentra disponible")):
            print("---> Fondo {isin} doesn't exist")
            continue

        # Collect funds main features
        descripcion = get_fund_description(soup)
        valor_liquidativo = get_liquidity_value(soup)
        patrimonio = get_assets_value(soup)
        volatilidad = get_volatility(soup)
        rentabilidad_media = get_average_rentability(soup)
        aportacion_minima = get_mininum_investment(soup)

        insert_fund_data(cursor,isin,os.path.splitext(filename)[0],descripcion,valor_liquidativo,patrimonio,
                     rentabilidad_media,volatilidad,aportacion_minima)
        
        # Collect fund rentabilities
        year_rentabilities = get_rentabilities(soup)
        acc_rentabilities = get_rentabilities(soup, type="acc")
    
        insert_rentabilities(cursor,isin, year_rentabilities, acc_rentabilities)
        
        i = i + 1
        if i % 10 == 0:
            conn.commit()
            print(f"Commited {i} funds")
        
        time.sleep(1)

    close_database(conn)
        

if __name__ == "__main__":
    main()
