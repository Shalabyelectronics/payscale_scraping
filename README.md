# Pay Scale 2018  data scraping

In this repository I'm going to practice web scraping and I will use this website 

[The Highest-Paying Careers with a Bachelor's Degree for 2018 | Payscale](https://www.payscale.com/college-salary-report/majors-that-pay-you-back/bachelors#csr-gridpage-bottom)

If you are interesting with data science you can download the CSV file and start answers some questions regarding this data like:

- What college major has the highest mid-career pay?
- How much do graduates with this major earn?
- Which college major has the lowest early pay salary?

and much more especially if you already finished your high school and thinking about which major you going to choose? 

### How I did Scrapped data from this site?

You can check the script a do some experiments to understand How this script did work?

First you need to install all the requirements by this magic command: 

```shell
pip install -r requirements.txt
```

first we need to create a beautiful soup instance and we will do that by this function called `request_pyscale_data` as below:

```python
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
```

and because the site have many pages I add a page parameter so we can use it if we need to request specific page .

![pages](https://user-images.githubusercontent.com/57592040/171741074-fb6ea1dd-e1d4-4c61-9900-ac19cd8847fc.png)


then we created a soup instance and finally if something went wrong and we didn't get success code of http request `200` we will return `NoneType`



After that we need to know how many pages does Pay scale web app does have, so I wrote another function to get the first and the last page for me as below:

```python
# Get All Pages numbers
def pay_scale_pages_numbers(data: object) -> dict:
    """Get the first and last page from a payscale data table"""
    all_table_pages = [int(number.text) for number in data.find_all("div", "pagination__btn--inner") if
                       number.text.isdigit()]
    first_page = min(all_table_pages)
    last_page = max(all_table_pages)
    return {"first page": first_page, "last page": last_page}
```

So this function as we see will take the soup object from the `request_payscale_data` and do some filters get the first and last page.

**Then** we are going to get all data we need from the pay scale web app by creating a `data_collection` function that will do this mission for us as below:

```python
# create a data collection form a pay scale website
def data_collections(data: object) -> dict:
    """Will get all main data and arrange it in a dictionary"""
    ranks = [re.findall(r"\d+", rank.get_text())[0] for rank in data.find_all("td", "csr-col--rank")]
    majors = [re.findall(r":\w+", major.get_text())[0].lstrip(":") for major in
              data.find_all("td", "csr-col--school-name")]
    
    school_types = [re.findall(r":\w+", school_type.get_text())[0].lstrip(":") for 		               school_type in data.find_all("td", "csr-col--school-type")]
                  
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
```

I used a lot of list comprehension here to get each columns data you can check this [video](https://www.youtube.com/watch?v=3dt4OGnU5sM) to understand how list comprehension work.

After having all this data in a dictionary we need to save this dictionary as a json file in our machine and to do so I create a `save_data` function as below:

```python
def save_data(data: dict):
    """Save pay scale data that sending from data_collection function"""
    if os.path.isfile("payscale_data.json"):
        # Update the current json file
        with open("payscale_data.json") as data_file:
            data_content = json.load(data_file)
            data_content["Ranks"].extend(data["Ranks"])
            data_content["High Meaning"].extend(data["High Meaning"])
            data_content["Majors"].extend(data["Majors"])
            data_content["School Types"].extend(data["School Types"])
            data_content["Early Pay"].extend(data["Early Pay"])
            data_content["Mid Career Pay"].extend(data["Mid Career Pay"])
        with open("payscale_data.json", mode="w") as data_file:
            json.dump(data_content, data_file, indent=4)
    else:
        # create a new file
        with open("payscale_data.json", mode="w") as data_file:
            json.dump(data, data_file, indent=4)
```

In this function we are going to check if the file already exist if so we will update the current file if not we are going to create a new json file.

And because we want to study that data we can't do that using the json file so we are going to convert it to a CSV file by `convert_json_to_csv` function as below:

```python
# convert the json file to csv
def convert_json_to_csv(json_file: str):
    """Covert the Json file to a CSV file"""
    df = pd.read_json(json_file)
    file_name = Path(json_file).stem
    df.to_csv(f"{file_name}.csv", index=None)
```

Finally we want to put all together to do our mission that having all pay scale data as a CSV file so we can study this data and answers about our questions, and I do arrange the Instructions as below:

```python
# Run all the previous steps to create a full json file that includes the full table data
def run_pay_scale_scraping_app():
    """Run The Instructions  in right order"""
    data = request_payscale_data(PAY_SCALE_URI)
    json_file_name = save_data(data_collections(data))
    pages_range = pay_scale_pages_numbers(data)
    first_page = pages_range["first page"] + 1
    last_page = pages_range["last page"] + 1

    for page_number in range(first_page, last_page):
        update_data = request_payscale_data(PAY_SCALE_URI, page=page_number)
        save_data(data_collections(update_data))
    convert_json_to_csv(json_file_name)
```

and you will ask me why do you add one to the first page? that because first page endpoint does not have a page number as you see here:

![first page](https://user-images.githubusercontent.com/57592040/171838489-28ef9adb-9582-4bd3-9b59-f1108684892f.png)


but other pages endpoint will look like this 


![other pages](https://user-images.githubusercontent.com/57592040/171838519-3cc40004-00dd-44f7-a5b0-cef32abdc2d0.png)


so that why we request the first page alone then we run with the loop to collect the data from other pages as well.

After all instructions done you will got `payscale_data.json` and `payscale_data.csv` as below:

![final output](https://user-images.githubusercontent.com/57592040/171838549-b353bb77-26dc-4827-aa2b-f4ddfda5daa5.png)


## Resources

- [How to Convert a JSON String to CSV using Python - Data to Fish](https://datatofish.com/json-string-to-csv-python/)
- [Python Dictionary update() method - GeeksforGeeks](https://www.geeksforgeeks.org/python-dictionary-update-method/)
- [Python - Regular Expressions (tutorialspoint.com)](https://www.tutorialspoint.com/python/python_reg_expressions.htm)
- [Beautiful Soup Documentation — Beautiful Soup 4.9.0 documentation (crummy.com)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [pathlib — Object-oriented filesystem paths — Python 3.10.4 documentation](https://docs.python.org/3/library/pathlib.html)
