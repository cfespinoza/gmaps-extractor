'''
Created on 14 ene. 2020


@description: Extract the attendance frequency for a list of Bilbao bars with
postal code 48005.

'''
from os.path import dirname
import csv
from itertools import chain
import logging
import time
import re
from typing import List, Tuple

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidSessionIdException

logger = logging.getLogger(__name__)

parent_dir = Path(dirname(__file__))

sentence = "Bar Gure Toki Plaza Nueva 12"

def get_browser(driver_path: str) -> WebDriver:
    """Get Google Chrome web browser

    """
    browser= webdriver.Chrome(driver_path)
    print("Current session is {}".format(browser.session_id))
    browser.maximize_window()
    return browser

def get_page(browser:WebDriver, sentence:str, sleep: int=10)-> str:
    """Download google maps page source for given bar name

    """
    url = 'https://www.google.es/maps/search/{}'.format(sentence)
    browser.get(url)
    time.sleep(sleep)
    source = browser.page_source
    return source

def detect_occupation_for_h(
        page_source: str
        ) -> List[Tuple[str, str, str, str, str]]:
    """Catch "horas puntas" in the source string with a regular expression

    """
    occupation = re.compile(
        r"(Nivel de ocupación: )(\d+)(&nbsp;% \(hora: )(\d{2})(\))"
        )
    return occupation.findall(page_source)

def day_occupation(
        findall_result: List[Tuple[str, str, str, str, str]]
        ) -> List[List[Tuple[str, str]]]:
    """Split a list of hours covering various days in a list of hours per days.

    """
    frequentation = []
    for i, (_, freq, _, hour, *_) in enumerate(findall_result):
        def hour_slice(h, begin):
            return (int(h) - int(begin))%24
        if i == 0:
            day = [(hour, freq)]
            first_hour = hour
        else:
            if hour_slice(hour, first_hour) > precedent_hour:
                day.append((hour, freq))
            else:
                frequentation.append(day)
                first_hour = hour
                day=[(hour, freq)]
        precedent_hour = hour_slice(hour, first_hour)
    frequentation.append(day)
    return frequentation

def day_occupation_24h(frequentation):
    """Pass the frequentation range for exemple 6h -- 23h to the range 1h -- 24h

    """
    freq_24h = []
    for freq in frequentation:
        days_hours = {k+1:0 for k in range(24)}
        for (k,v) in freq:
            days_hours[int(k)]=int(v)
        freq_24h.append(list(days_hours.items()))
    return freq_24h

def number2days(n: int) -> str:
    """Transform day number to day name in spanish

    """
    week_days = [
        'domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'
        ]
    days_of_the_week = {k:v for (k,v) in enumerate(week_days)}
    return days_of_the_week[n]

def get_frequentations(
        occupations: List[List[Tuple[str, str]]]
        ) -> List[List[Tuple[(int,)*24]]]:
    try:
        frequentation = day_occupation_24h(day_occupation(occupations))
        for i, day in enumerate(frequentation):
            n = len(day)
            base_ = '|'.join(['{:3}']*n)
            print(f"\nday: {number2days(i)}\n--------")
            print(base_.format(*[h for (h,f) in day]))
            print(base_.format(*['---']*n))
            print(base_.format(*[f for (h,f) in day]))
    except UnboundLocalError as e:
        logger.warn(f"No frequentation information found for {sentence}")
    except Exception as e:
        logger.exception("other exception")
    return frequentation

def get_freq(sentences: Tuple[str]) -> List[List[Tuple[(int,)*24]]]:
    print('-'*100)
    print(f'{sentences[0]}')
    source = get_page(browser, sentences[0], sleep=10)
    occupations = detect_occupation_for_h(source)
    if occupations:
        freq = get_frequentations(occupations)
    elif len(sentences)>1:
        freq = get_freq((sentences[1],))
    else:
        logger.warning(f"No frequentation information found for {sentence}")
        freq = None
    return freq

def get_bars_names(file_path: str='../data/casco_bars.csv') -> Tuple[str, str]:
    """Get the bars name from the given file_path.

    """
    with open(file_path, newline='') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            bar_address_1 = f"{row['Establecimiento']} 48005"
            bar_address_2 = f"{row['Establecimiento']} {row['Dirección']}"
            yield (bar_address_1, bar_address_2, row['Establecimiento'])

if __name__ == '__main__':

    driver_path = parent_dir / '../drivers/chromedriver_linux64/chromedriver'
    browser= get_browser(driver_path)

    fieldnames = (
                ['Name', '']
                + list(chain(
                    *map(lambda i:[number2days(i)] +['']*23, range(7))
                    ))
                )

    filename = '../data/casco_bars_horas_punta_2.csv'

    with open(filename, newline='', mode='w') as f:

        writer = csv.writer(f, dialect='excel')
        writer.writerow(fieldnames)

        for i, (s1, s2, sentence_original) in enumerate(get_bars_names()):
            freq = get_freq((s1, s2))
            if freq:
                horas_row = (
                    [sentence_original, 'horas']
                    + list(
                        chain(*[[h for (h,f) in day_freq] for day_freq in freq])
                        )
                    )
                frequency_row = (
                    ['', 'puntas']
                    + list(
                        chain(*[[f for (h,f) in day_freq] for day_freq in freq])
                        )
                    )
                writer.writerow(horas_row)
                writer.writerow(frequency_row)
            else:
                pass

    browser.close()









