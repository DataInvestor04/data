import subprocess
import time
import pyautogui
import os
from datetime import datetime
import shutil

def download_csv():
    url = 'https://www.nseindia.com/market-data/52-week-high-equity-market'
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'

    # Start Chrome and keep a reference to the process
    chrome_process = subprocess.Popen([chrome_path, "--start-maximized", url])
    time.sleep(15)

    # Automate the click (adjust coordinates if needed)
    x, y = 446, 592
    pyautogui.moveTo(x, y, duration=1)
    pyautogui.click()
    time.sleep(5)

    chrome_process.terminate()  # or use chrome_process.kill()
    print("Chrome has been closed.")

    # Find the most recent file in Downloads
    download_folder = os.path.expanduser("~/Downloads")
    list_of_files = os.listdir(download_folder)
    full_paths = [os.path.join(download_folder, file) for file in list_of_files]

    if full_paths:
        latest_file = max(full_paths, key=os.path.getctime)
        today_date = datetime.today().strftime("%Y-%m-%d")

        confirm_date = input(f"{today_date} Confirm Date Press Y. To change Press N: ")

        if confirm_date != 'Y':
            today_date = input("Enter in this format YYYY-MM-DD: ")

        new_filename = f"{today_date}.csv"
        dest_path = os.path.join(os.getcwd(), new_filename)
        shutil.move(latest_file, dest_path)
        print("CSV file has been successfully downloaded")

        # Kill the Chrome process after download
        # chrome_process.terminate()  # or use chrome_process.kill()
        # print("Chrome has been closed.")

        return new_filename
    else:
        print("Unable to find the file.")
        chrome_process.terminate()
        return None

