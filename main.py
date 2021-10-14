#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import argparse
import sys
import re
import os

"""
Glassdoor Interview Questions Scrapper

Copyright 2021 Ronald Cotton. All Rights Reserved.
"""

# functions
def load_site(u):
    options = Options()
    options.add_argument("--silent")
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    #options.add_argument('--headless') 
    options.add_argument('--disable-software-rasterizer')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
    try:
        if sys.platform == 'win32':
            site = webdriver.Chrome('.\chromedriver.exe', options=options)
        else:
            site = webdriver.Chrome('.\chromedriver', options=options)
    except:
        print('Need to install the webdriver and place into local folder')
        print('go to https://chromedriver.chromium.org/downloads (install correct version, place into current folder)')
        sys.exit(2)
    site.get(u)
    return site

def program_args():
    parse = argparse.ArgumentParser(description='Glassdoor Interview Scrapper using Selenium')

    parse.add_argument('-u','--url', type = str, default = None, help = 'First URL for Interview Questions')
    parse.add_argument('-o','--output', type = str, default = 'results.csv', help = 'Name of output file (csv format)')
    parse.add_argument('-n','--num', type = int, default = 1, help = 'Max of pages to scrape')

    return vars(parse.parse_args())


def convert_list_webelement(lst):
    return [l.text.replace('"','\'') for l in lst] # convert all quotes to single quote, double quote for csv


def csv_header(filename):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        col_names = ['date', 'title', 'application', 'interview', 'interview_question']
        last_col = len(col_names)-1
        for i,f in enumerate(col_names):
            if i == last_col:
                csvfile.write(f'"{f}"')
            else:
                csvfile.write(f'"{f}",')
        csvfile.write('\n')

def dict_to_csv(filename, lst_dct):
    with open(filename, 'a', encoding='utf-8') as csvfile:
        for dct in lst_dct:
            for k,v in dct.items():
                csvfile.write(f'"{v}",') # fix later...
            csvfile.write('\n')
        

# main
if __name__ == "__main__":
    args = program_args()
    if not args['url']:
        print('No URL given - should be first page at Glassdoor - example format: https://www.glassdoor.com/Interview/Amazon-Interview-Questions-E6036.htm')
        print('Use the -h parameter for help')
        sys.exit(1)

    if(os.path.exists(args['output']) and os.path.isfile(args['output'])):
        os.remove(args['output'])
        print(f'removed {args["output"]}... generating new {args["output"]}')
    else:
        print(f'{args["output"]} doesn\'t exist... creating.')

    # make header
    csv_header(args["output"])

    gd = load_site(args['url'])
    print(gd)
    scrape_num_of_pages = gd.find_element_by_class_name('paginationFooter').text.replace(',','')  # number of results, and remove any commas
    num_of_pages = [int(s) for s in scrape_num_of_pages.split() if s.isdigit()].pop() // 10 # number of pages = (last number results) / 10
    
    if args['num'] > num_of_pages:
        print(f'requested more pages than available, scraping only {num_of_pages}.')
        args['num'] = num_of_pages

    scraping_page = args['url']
    for i in range(1,args['num']+1):
        if i > 1:
            if ',' not in args['url']:
                scraping_page = args['url'][:len(args['url'])-4] + f'_P{i}.htm'
            else:
                scraping_page = args['url'][:len(args['url'])-4] + f'_IP{i}.htm'
        print(f'Scraping Page: {i} of {args["num"]} - {scraping_page}')
        gd = load_site(scraping_page)
        title = convert_list_webelement(gd.find_elements_by_class_name('css-5j5djr')[-11:-1])
        interview_application = convert_list_webelement(gd.find_elements_by_css_selector("p.mt-xsm.mb-std"))
        date = convert_list_webelement(gd.find_elements_by_css_selector("p.mt-0.mb-xxsm.d-flex.justify-content-between.css-13r90be.e1lscvyf1"))
        interview_questions = convert_list_webelement(gd.find_elements_by_css_selector("span.d-inline-block.mb-sm"))

        interview = []
        application = []
        for i, ia in enumerate(interview_application):
            if i%2 == 1:
                interview.append(ia)
            else:
                application.append(ia)

        # interview questions is not required for each post
        # adding blank index if less than 10
        interview_questions = interview_questions[-10:]
        num_iq = len(interview_questions)
        if num_iq < 10:
            for i in range(10-num_iq):
                interview_questions.append('No Question')

        # we only want 10 results per page
        interview = interview[-10:]
        application = application[-10:]
        date = date[-10:]

        # create dict
        lst_dct = []
        dct = {}
        for i in range(10):
            try:
                dct['date'] = date[i]
            except:
                dct['date'] = 'ERROR'
            try:
                dct['title'] = title[i]
            except:
                dct['title'] = 'ERROR'
            try:
                dct['application'] = application[i]
            except:
                dct['application'] = 'ERROR'
            try:
                dct['interview'] = interview[i]
            except:
                dct['interview'] =  'ERROR'
            try:
                dct['interview_question'] = interview_questions[i]
            except:
                dct['interview'] =  'ERROR'
            lst_dct.append(dct)
            dct = {}
        
        # save dict as csv
        dict_to_csv(args['output'], lst_dct)

        # clear out lists (not needed)    
        title = []
        application = []
