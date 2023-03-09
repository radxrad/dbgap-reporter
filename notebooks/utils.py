#!/usr/bin/env python
# coding: utf-8
import os
import shutil
import glob
import time
from tqdm import tqdm
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_binary 

def download_dbgap_studies(query, filepath):
    query_dbgap(query)
    download_studies_file(filepath)


def query_dbgap(query):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.add_experimental_option("prefs", {"download.default_directory": "/tmp"}) # doesn't set download dir?
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.ncbi.nlm.nih.gov/gap/advanced_search/?TERM={query}")
    time.sleep(3)
    #print(driver.title)
    button = driver.find_element(By.CLASS_NAME, "svr_container")
    time.sleep(3)
    button.click()
    time.sleep(15)


def download_studies_file(filepath):
    # there should be only one csv file, but the name is unknown.
    files = glob.glob("*.csv")
    if len(files) > 0:
        shutil.move(files[0], filepath)
    else:
        print("query error")
        
        
def get_download_url(accession):
    return "https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/GetAuthorizedRequestDownload.cgi?study_id=" + accession


def get_authorized_requests(studies):
    authorized_requests = pd.DataFrame()

    for _, row in tqdm(studies.iterrows(), total=studies.shape[0]):
        try:
            df = pd.read_csv(get_download_url(row["accession"]), 
                             usecols=["Requestor", "Affiliation", "Project", "Date of approval", "Request status", 
                                      "Public Research Use Statement", "Technical Research Use Statement"],
                            sep="\t")
            df["accession"] = row["accession"]
            df["name"] = row["name"]
            authorized_requests = pd.concat([authorized_requests, df], ignore_index=True)
        except:
            print(f"Skipping: {row['accession']} - no data.")
                                        
    return authorized_requests