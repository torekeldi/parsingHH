import requests
import bs4
from fake_headers import Headers
import re
import json


def get_headers():
    return Headers(os="win", browser="chrome").generate()


url = 'https://spb.hh.ru/search/vacancy'
params = {
        "text": 'python',
        "area": [1, 2],
        "per_page": 20,
    }

vacancy_list = []

response = requests.get(url, params=params, headers=get_headers())
soup = bs4.BeautifulSoup(response.text, features='lxml')
main_div_tag = None
while main_div_tag is None:
    main_div_tag = soup.find('div', id='a11y-main-content')
divs = None
while divs is None:
    divs = main_div_tag.find_all('div', class_='serp-item serp-item_link')
for data in divs:
    vacancy_link = data.find('a')['href']
    vacancy_title = data.find('span', class_='serp-item__title-link serp-item__title').text.strip()
    response = requests.get(vacancy_link, headers=get_headers())
    soup = bs4.BeautifulSoup(response.text, features='lxml')
    first_class = ('bloko-column bloko-column_container bloko-column_xs-4 bloko-column_s-8 '
                   'bloko-column_m-12 bloko-column_l-10')
    first_tag = None
    while first_tag is None:
        first_tag = soup.find('div', class_=first_class)
    com_tag = None
    while com_tag is None:
        com_tag = first_tag.find('span', class_='vacancy-company-name')
    vacancy_company = ' '.join(com_tag.text.split())
    loc_tag = None
    while loc_tag is None:
        loc_tag = first_tag.find('div', class_='vacancy-company-redesigned')
    loc_tag2 = loc_tag.find('p', attrs={'data-qa': 'vacancy-view-location'})
    loc_tag3 = loc_tag.find('span', attrs={'data-qa': 'vacancy-view-raw-address'})
    if loc_tag2:
        vacancy_location = loc_tag2.text
    else:
        vacancy_location = loc_tag3.text.split()[0].strip(',')
    sal_tag = first_tag.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
    if sal_tag:
        vacancy_salary = ' '.join(sal_tag.text.split())
    else:
        vacancy_salary = 'Не указано'
    desc_tag = first_tag.find('div', attrs={'data-qa': 'vacancy-description'})
    vacancy_description = desc_tag.text
    my_vacancy = re.findall(r'django|flask', vacancy_description, flags=re.I)
    if len(my_vacancy) > 0:
        vacancy_list.append(
            {
                'link': vacancy_link,
                'title': vacancy_title,
                'salary': vacancy_salary,
                'company': vacancy_company,
                'location': vacancy_location,
            }
        )


json_prep = json.dumps(vacancy_list, indent=2)
with open('vacancy_list.json', 'w') as f:
    json.dump(json_prep, f)
