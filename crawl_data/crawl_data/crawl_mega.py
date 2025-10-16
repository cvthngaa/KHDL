import time
import random
import re
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_product_name(product_name):
    """Làm sạch tên sản phẩm, bỏ phần trong ngoặc."""
    return re.sub(r"\(.*\)", "", product_name).strip()

def crawl_page(url):
    options = webdriver.ChromeOptions()
    options.headless = False  
    driver = webdriver.Chrome(options=options)

    result = {
        "Product Name": None,
        "Price": None,
        "Specifications": {}
    }

    try:
        driver.get(url)
        sleep(3)  

        # Lấy tên sản phẩm và làm sạch tên
        try:
            product_name = driver.find_element(By.CSS_SELECTOR, "h1.product-name").text
            result["Product Name"] = get_product_name(product_name)
        except Exception as e:
            print(f"[!] Không lấy được tên sản phẩm: {e}")

        # Lấy giá sản phẩm
        try:
            price = driver.find_element(By.CSS_SELECTOR, "#product-info-price .text-20.red").text.strip()
            result["Price"] = price
        except Exception as e:
            print(f"[!] Không lấy được giá: {e}")

        for _ in range(10):
            try:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.viewmore.btn.red"))
                )
                button.click()
                sleep(1)
                break
            except:
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                sleep(0.5)

        # Lấy bảng thông số kỹ thuật
        try:
            table = driver.find_element(By.CSS_SELECTOR, "#full-spec table")
            for row in table.find_elements(By.TAG_NAME, "tr"):
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    result["Specifications"][key] = value
        except Exception as e:
            print(f"[!] Không thể lấy thông số kỹ thuật: {e}")

    finally:
        driver.quit()

    return result

def crawl_all_products(start_page_url, max_pages):
    options = webdriver.ChromeOptions()
    options.headless = False
    driver = webdriver.Chrome(options=options)

    all_products = []
    page = 1

    try:
        while page <= max_pages:
            if page == 1:
                page_url = start_page_url
            else:
                page_url = f"{start_page_url}?page={page}"

            print(f"🔄 Đang cào trang {page}: {page_url}")
            driver.get(page_url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".p-container"))
                )
            except:
                print("❌ Không có thêm sản phẩm, dừng lại.")
                break

            # Lấy danh sách các sản phẩm trên trang
            try:
                product_elements = driver.find_elements(By.CSS_SELECTOR, ".p-container")
                for product_element in product_elements:
                    try:
                        link = product_element.find_element(By.CSS_SELECTOR, ".p-name a").get_attribute("href")
                        product_details = crawl_page(link) 
                        all_products.append(product_details) 
                    except Exception as e:
                        print(f"⚠️ Lỗi khi lấy thông tin sản phẩm: {e}")
                        continue

            except Exception as e:
                print(f"⚠️ Lỗi khi lấy danh sách sản phẩm: {e}")
                break

            page += 1
            time.sleep(random.uniform(1, 3))

    finally:
        driver.quit()

    return all_products

def save_to_csv(data_list, filename="products.csv"):
    """
    Lưu danh sách sản phẩm vào file CSV.
    Tách 'Specifications' thành các cột riêng biệt.
    """
    if not data_list:
        print("Không có dữ liệu để lưu.")
        return

    flat_data_list = []
    for item in data_list:
        flat_item = item.copy()
        
        if "Specifications" in flat_item and isinstance(flat_item["Specifications"], dict):
            for key, value in flat_item["Specifications"].items():
                flat_item[key] = value
            del flat_item["Specifications"]
        
        flat_data_list.append(flat_item)

    # Chuyển thành DataFrame
    df = pd.DataFrame(flat_data_list)

    # Lưu DataFrame vào CSV
    df.to_csv(filename, index=False, encoding="utf-8")

    print(f" Đã lưu dữ liệu vào file '{filename}'.")

if __name__ == "__main__":
    start_page_url = "https://mega.com.vn/may-tinh-xach-tay.html"  # Thay bằng URL thật
    max_pages = 39  # Số lượng trang tối đa muốn cào
    all_products = crawl_all_products(start_page_url, max_pages)

    # In thông tin chi tiết từng sản phẩm
    for product in all_products:
        print(f"\n=== Đang cào sản phẩm: {product['Product Name']} ===")
        print(f"Product Name: {product['Product Name']}")
        print(f"Price: {product['Price']}")
        if product['Specifications']:
            print("Specifications:")
            for key, value in product['Specifications'].items():
                print(f"  - {key}: {value}")
    
    # Lưu kết quả vào CSV
    save_to_csv(all_products, "../raw_data/mega.csv")
    print(" Hoàn tất cào dữ liệu.")

