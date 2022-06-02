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



After that we need to know how many pages does Pay scale have>> To be continue LOL
