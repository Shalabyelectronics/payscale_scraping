import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import json
import os
import pandas as pd

PAY_SCALE_URI = "https://www.payscale.com/college-salary-report/majors-that-pay-you-back/bachelors"


# Create soup object
def request_pyscale_data(url: str, page=None) -> object:
    """This function will return an object for the requested page soup."""
    if page:
        url = url + f"/page/{page}"
    pay_scale_data_request = requests.get(url)
    request_state = pay_scale_data_request.status_code
    request_content = pay_scale_data_request.text
    soup = BeautifulSoup(request_content, 'html.parser')
    if request_state == 200:
        return soup
    return None


# Get All Pages numbers
def pay_scale_pages_numbers(data: object) -> dict:
    """Get the first and last page from a pyscale table"""
    all_table_pages = [int(number.text) for number in data.find_all("div", "pagination__btn--inner") if
                       number.text.isdigit()]
    first_page = min(all_table_pages)
    last_page = max(all_table_pages)
    return {"first page": first_page, "last page": last_page}


# create a data collection form a pay scale website
def data_collections(data: object) -> dict:
    ranks = [re.findall(r"\d+", rank.get_text())[0] for rank in data.find_all("td", "csr-col--rank")]
    majors = [re.findall(r":\w+", major.get_text())[0].lstrip(":") for major in
              data.find_all("td", "csr-col--school-name")]
    school_types = [re.findall(r":\w+", school_type.get_text())[0].lstrip(":") for school_type in
                    data.find_all("td", "csr-col--school-type")]
    early_career_pays = [re.findall(r"\d+,\d+", str(career_pay))[0] for career_pay in
                         data.find_all("td", "csr-col--right") if "Early Career Pay" in str(career_pay)]
    early_career_pays_filter = [amount.replace(",", "") for amount in early_career_pays]
    mid_career_pays = [re.findall(r"\d+,\d+", str(mid_career))[0] for mid_career in
                       data.find_all("td", "csr-col--right")
                       if "Mid-Career Pay" in str(mid_career)]
    mid_career_pays_filter = [amount.replace(",", "") for amount in mid_career_pays]
    high_meanings = [re.findall(r"\d+\W", str(high_meaning)) for high_meaning in
                     data.find_all("td", "csr-col--right") if "High Meaning" in str(high_meaning)]
    high_meanings_clean_up = [high_meaning[0] if len(high_meaning) != 0 else "-" for high_meaning in high_meanings]
    pay_scale_columns_data = {
        "Ranks": ranks,
        "Majors": majors,
        "School Types": school_types,
        "Early Pay": early_career_pays_filter,
        "Mid Career Pay": mid_career_pays_filter,
        "High Meaning": high_meanings_clean_up
    }
    return pay_scale_columns_data


# Get All Columns
def pay_scale_columns(data: object) -> list:
    """Get a list of columns from payscale table"""
    data_columns = [title.text for title in data.find_all("th", "data-table__header")]
    return data_columns


# save data as json
def save_data(data: dict):
    if os.path.isfile("pyscale_data.json"):
        # Update the current json file
        with open("pyscale_data.json") as data_file:
            data_content = json.load(data_file)
            data_content["Ranks"].extend(data["Ranks"])
            data_content["High Meaning"].extend(data["High Meaning"])
            data_content["Majors"].extend(data["Majors"])
            data_content["School Types"].extend(data["School Types"])
            data_content["Early Pay"].extend(data["Early Pay"])
            data_content["Mid Career Pay"].extend(data["Mid Career Pay"])
        with open("pyscale_data.json", mode="w") as data_file:
            json.dump(data_content, data_file, indent=4)
    else:
        # create a new file
        with open("pyscale_data.json", mode="w") as data_file:
            json.dump(data, data_file, indent=4)


# Run all the previous steps to create a full json file that includes the full table data
def run_pay_scale_scraping_app():
    data = request_pyscale_data(PAY_SCALE_URI)
    save_data(data_collections(data))
    pages_range = pay_scale_pages_numbers(data)
    first_page = pages_range["first page"] + 1
    last_page = pages_range["last page"] + 1

    for page_number in range(first_page, last_page):
        update_data = request_pyscale_data(PAY_SCALE_URI, page=page_number)
        save_data(data_collections(update_data))


# convert the json file to csv
def convert_json_to_csv(json_file):
    df = pd.read_json(json_file)
    file_name = Path(json_file).stem
    df.to_csv(f"{file_name}.csv", index=None)
