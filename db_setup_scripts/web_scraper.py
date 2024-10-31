from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time


# Setup the Chrome WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

base_url = 'https://rpc.cfainstitute.org/en/research-foundation/publications#'
url_params = 'sort=%40officialz32xdate%20descending&f:SeriesContent=[Research%20Foundation]'
image_url = 'https://png.pngtree.com/png-clipart/20220612/original/pngtree-pdf-file-icon-png-png-image_7965915.png'   
        
def get_pdf_title(row):
    try:
        pdf_title = row.find_element(By.CLASS_NAME, 'CoveoResultLink').text
        pdf_title = pdf_title.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
        return pdf_title
    except Exception as e:
        print(f"Error retrieving PDF title {e}")
        

def get_pdf_documents(data):
    try:
        for pdf_info in data:
            driver.get(pdf_info['webpage_link'])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href$=".pdf"]')))
            pdf_info['pdf_link'] = driver.find_element(By.CSS_SELECTOR, 'a[href$=".pdf"]').get_attribute('href')
        return data
    except Exception as e:
        print(f"Error extracting PDF document links {e}")
        return data

def get_webpage_link(row):
    try:
        result_link = row.find_element(By.CLASS_NAME, 'CoveoResultLink').get_attribute('href')
        return result_link
    except Exception as e:
        print(f"Error getting webpage link {e}")
        return ""
    
def get_image_link(row):
    try:
        image_link = row.find_element(By.CLASS_NAME,'coveo-result-image').get_attribute('src')
        image_link = image_link.split("?")[0]
        return image_link
    except Exception as e:
        print(f"Error getting image link {e}")
        return image_url
    
 
def get_pdf_summary(row):
    try:
        summary_text = row.find_element(By.CLASS_NAME,'result-body').text
        summary_text = summary_text.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
        
        return summary_text
    except Exception as e:
        print(f"Error getting summary text: {e}")
        return ""
    
def scrape_single_page(page_url):
    driver.get(page_url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.coveo-result-frame.coveoforsitecore-template')))
    rows = driver.find_elements(By.CSS_SELECTOR, '.coveo-result-frame.coveoforsitecore-template')
    page_data = []
    
    for row_num,row in enumerate(rows):
        try:
            row_data = {}
            row_data['webpage_link'] = get_webpage_link(row)
            row_data['title'] = get_pdf_title(row)
            row_data['image_link'] =  get_image_link(row)
            row_data['summary_text'] = get_pdf_summary(row)
            page_data.append(row_data)
            print(f"Row  {row_num}  added ")
        except Exception:
            print(f"Error scraping row {row_num}")
    return page_data


# Function to scrape multiple pages
def scrape_pages(num_pages):
    all_data = []
    for page_num in range(0, num_pages * 10,10):
        page_url = f"{base_url}&first={page_num}&{url_params}"
        page_data = scrape_single_page(page_url)
        all_data.extend(page_data)
        print(f" Page {page_num}  updated")
        time.sleep(10)   
          
    return all_data

        
# Run data ingestion
data = scrape_pages(10)
pdf_data = get_pdf_documents(data)


driver.quit()

with open('scraped_data.json', 'w') as file:
    pdf_data = json.dump(pdf_data,file, indent = 4)



    


