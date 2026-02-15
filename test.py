import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.binary_location = "/usr/bin/chromium"

driver = uc.Chrome(options=options)
driver.get("https://google.com")
print(driver.title)
driver.quit()
