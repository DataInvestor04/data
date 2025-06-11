from DownloadCsv import download_csv
from Scrape import scraping
import os
from Commit import commit_to_github

filename = download_csv()
# filename = '2025-05-23.csv'
scraping(filename)
os.remove(filename)
# os.remove("b_2025_05_28.csv")


file_to_commit = "financial_metrics.csv"
commit_to_github(file_to_commit)

