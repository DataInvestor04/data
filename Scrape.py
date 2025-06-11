import os
import pandas as pd
from datetime import datetime
from jugaad_data.nse import NSELive
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def scraping(filename):
    save_dir = "C:/Users/krish/OneDrive/Desktop/52WH-final/data"
    os.makedirs(save_dir, exist_ok = True)  

    try:

        stock_data = pd.read_csv(filename)
        stock_data.columns = stock_data.columns.str.strip()
        stock_data["Prev. High Date"] = pd.to_datetime(stock_data["Prev. High Date"], format="%d-%b-%Y", errors="coerce")
        date_str = os.path.splitext(filename)[0]  
        reference_date = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = reference_date.strftime("%d-%b-%y")
        stock_data["Prev. High Date"] = pd.to_datetime(stock_data["Prev. High Date"])
        stock_data["Days Since High"] = (reference_date - stock_data["Prev. High Date"]).dt.days
        stock_data["Today's Date"] = formatted_date
        stock_data["Series Type"] = stock_data["Series"].apply(lambda x: "Equity" if x.startswith(("BE", "BZ", "EQ")) else "SME" if x.endswith(("SM", "ST", "SZ")) else "SME")

    except Exception as e:

        print(f"Error reading stock data: {e}")
        return

    def get_financial_metrics(symbol):
        url = f"https://www.screener.in/company/{symbol}/"
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "company-ratios")))
            about_text = driver.find_element(By.CLASS_NAME, "company-ratios").text.split('\n')
            about_section = driver.find_element(By.CLASS_NAME, "sub.show-more-box").text
            sector = driver.find_element(By.XPATH, "//p[@class='sub']/a[1]").text
            industry = driver.find_element(By.XPATH, "//p[@class='sub']/a[2]").text
            driver.quit()

            def extract_value(label):
                try:
                    return about_text[about_text.index(label) + 1].strip()
                except ValueError:
                    return "Not found"

            return {
                "Symbol": symbol,
                "Market Cap": extract_value("Market Cap"),
                "P/E Ratio": extract_value("Stock P/E"),
                "ROE": extract_value("ROE"),
                "ROCE": extract_value("ROCE"),
                "Sector": sector,
                "Industry": industry,
                "About": about_section,
            }
        except:
            return {"Symbol": symbol, "Market Cap": "Failed", "P/E Ratio": "Failed", "ROE": "Failed", "ROCE": "Failed", "Sector": "Failed", "Industry": "Failed", "About": "Failed"}

    scraped_data = [get_financial_metrics(symbol) for symbol in stock_data["Symbol"]]
    scraped_df = pd.DataFrame(scraped_data)
    scraped_1_df = pd.merge(stock_data, scraped_df, on="Symbol", how="left")
    scraped_1_df = scraped_1_df[~scraped_1_df["Market Cap"].isin(["₹ Cr.", "₹ Cr", None])]

    previous_df = pd.read_csv('financial_metrics.csv')
    final_df = pd.concat([previous_df, scraped_1_df], ignore_index= True)

    # if os.path.exists(output_file):
    #     existing_df = pd.read_csv(output_file)
    #     # combined_df = pd.concat([existing_df, final_df], ignore_index=True)
    #     # combined_df.drop_duplicates(subset=["Symbol", "Today's Date"], keep="last", inplace=True)
    # else:
    #     combined_df = final_df


    # ✅ Update 'Latest Price' for ALL symbols (not just today's)
# Load corresponding bhavcopy
    # bhavcopy_filename = f"b_{reference_date.strftime('%Y-%m-%d')}.csv"
    bhavcopy_filename = "b_2025-06-11.csv"
    try:
        bhavcopy_df = pd.read_csv(bhavcopy_filename)
        bhavcopy_df.columns = bhavcopy_df.columns.str.strip()
    except Exception as e:
        print(f"Error loading bhavcopy file {bhavcopy_filename}: {e}")
        return

    # Map bhavcopy close prices to symbols
    symbol_to_price = dict(zip(bhavcopy_df['SYMBOL'].str.upper(), bhavcopy_df['CLOSE_PRICE']))

    # Assign close price as Latest Price
    latest_prices = []
    for symbol in final_df['Symbol']:
        price = symbol_to_price.get(symbol.upper(), "N/A")
        latest_prices.append(price)
        print(f"{symbol}: {price}")


    # for symbol in symbols:
    #     try:
    #         latest_price = n.stock_quote(symbol)['priceInfo']['lastPrice']
    #         if latest_price == 0.00:
    #             latest_prices.append('None')
    #         else:
    #             latest_prices.append(latest_price)
    #         print(f'{symbol}: {latest_price}')
    #     except:
    #         latest_prices.append("N/A")
    #         print(f'{symbol}: N/A')


    # def chunks(lst, n):
    #     for i in range(0, len(lst), n):
    #         yield lst[i:i + n]

    # for batch in chunks(symbols, 500):  # 500 at a time
    #     for symbol in batch:
    #         try:
    #             latest_price = n.stock_quote(symbol)['priceInfo']['lastPrice']
    #             latest_prices.append(latest_price if latest_price != 0.00 else 'None')
    #             print(f'{symbol}: {latest_price}')
    #         except:
    #             latest_prices.append("N/A")
    #             print(f'{symbol}: N/A')
    #         time.sleep(1.5)
    
    #     print("Sleeping for 10 minutes to avoid block...")
    #     time.sleep(600)  # sleep 10 minutes between batches


    # Assign updated prices
    final_df['Latest Price'] = latest_prices
    final_df = final_df[["Symbol", "LTP", "%chng", "Days Since High", "Today's Date", "Series Type", "Market Cap", "P/E Ratio", "ROE", "ROCE", "Sector", "Industry", "About", "Latest Price"]]
    output_file = os.path.join(save_dir, "financial_metrics.csv")

    final_df.to_csv(output_file, index=False)
    print(f"Scraping complete. Data updated and saved to '{output_file}'.")

# scraping('2025-04-07.csv')