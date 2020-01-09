import requests
from bs4 import BeautifulSoup as BS
from datetime import timedelta, date


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


# convert month string to number
def month_string_to_number(string):
    m = {
        'jan': "01", 'feb': "02", 'mar': "03", 'apr': "04",
        'may': "05", 'jun': "06", 'jul': "07", 'aug': "08",
        'sep': "09", 'oct': "10", 'nov': "11", 'dec': "12"
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')


if __name__ == "__main__":
    url = 'https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches'
    html = requests.get(url).text
    soup = BS(html, 'html.parser')
    table = soup.find_all("table", { "class" : "wikitable collapsible" })[0]
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    # intermediate result [time, success, time, success...]
    tmp_result = []
    rowspan_num = 0
    is_success = False

    for row in rows:
        cols = row.find_all('td')
        # How many following rows need to check
        if len(cols) > 0 and cols[0].has_attr("rowspan"):
            current_time = cols[0].text.strip()
            tmp_result.append(current_time)
            rowspan_num = int(cols[0]['rowspan'])

        cols = [ele.text.strip() for ele in cols]
        for col in cols:
            if "Operational" in col or "Successful" in col or "En Route" in col:
                is_success = True

        if rowspan_num == 1:
            tmp_result.append(is_success)

        rowspan_num -= 1

        # Get to last payload of one launch
        if rowspan_num == 0:
            rowspan_num = 0
            is_success = False

    # launch_count{ key:day_time, value:count }
    launch_count = dict([])
    odd_even_flag = True
    for item in tmp_result:
        if odd_even_flag:
            time_str = item.split(" ")
            month_str = month_string_to_number(time_str[1])
            day_str = str(time_str[0]).zfill(2)
            key = "2019-" + month_str + "-" + day_str
            if key not in launch_count:
                launch_count[key] = 0
            odd_even_flag = False
        else:
            if item == True:
                launch_count[key] += 1
            odd_even_flag = True

    # print(launch_count)
    start_date = date(2019, 1, 1)
    end_date = date(2020, 1, 1)

    file = open("output.csv", "w")
    file.write("date,value\n")
    for single_date in daterange(start_date, end_date):
        day_time = single_date.strftime("%Y-%m-%d")
        if day_time in launch_count:
            res_str = day_time + "T00:00:00+00:00," + str(launch_count[day_time])
            file.write(res_str + "\n")
        else:
            res_str = day_time + "T00:00:00+00:00,0"
            file.write(res_str + "\n")
