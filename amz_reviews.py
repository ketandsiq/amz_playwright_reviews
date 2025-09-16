from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapy import Selector
import pyotp
import asyncio
import os
from dotenv import load_dotenv
from attribute_parser import AttributeParser
import json
import re
from datetime import datetime


load_dotenv()

EMAIL = os.getenv('EMAIL').split(',')
PASSWORD = os.getenv('PASSWORD').split(',')
SECRET = os.getenv('SECRET').split(',')



amz_reviews={
  "review_data":{
    "authorId": ["div[data-hook='genome-widget']>a::attr(href)"],
    "reviewId": ["li[data-hook='review']::attr(id)"],
    "isVerified": ["div.a-row.a-spacing-mini.review-data.review-format-strip>a>span[data-hook='avp-badge']::text"],
    "rating": ["a[data-hook='review-title']>i>span.a-icon-alt::text"],
    "authorName": ["div[data-hook='genome-widget']>a>div.a-profile-content>span::text"],
    "reviewTitle": ["a[data-hook='review-title']>span::text"],
    "reviewText": [".span[data-hook='review-body']>span::text"],
    "reviewImages": ["div.review-image-tile-section>span>a>img::attr(src)"],
    "reviewVideos": ["span[data-hook='review-body']>div>div.cr-video-desktop::attr(data-video-url)"],
    "helpfulVoteCount":["span.cr-vote>div>span[data-hook='helpful-vote-statement']::text"],
    "reviewDate": ["span[data-hook='review-date']::text"],
    "reviewCountry": ["span[data-hook='review-date']::text"]
  }
}

class PlaywrightAmzReviews:
    def __init__(self):
        self.urls = [
                {"id": "dad65664-2284-4b11-8095-e1afa1aaee1e", "retailer_product_id": "B0DW48GN42", "retailer_id": "9ad33e7b-1f96-477d-bb95-ee05567a1ec2"},
                {"id": "da16f607-9507-4f89-8891-aa50b23cae5d", "retailer_product_id": "B0B9HTM5GG", "retailer_id": "9ad33e7b-1f96-477d-bb95-ee05567a1ec2"},
                {"id": "da5ad27e-815f-435b-9b19-d2743d04b902", "retailer_product_id": "B00UD4I3FC", "retailer_id": "9ad33e7b-1f96-477d-bb95-ee05567a1ec2"},
                {"id": "de694b0e-49be-4c78-8695-2dc6359f4079", "retailer_product_id": "B0DPJRB5BG", "retailer_id": "9ad33e7b-1f96-477d-bb95-ee05567a1ec2"},
                {"id": "cd05ccfd-1cac-4ae7-bdd0-fb4744cd246c", "retailer_product_id": "B07Q1F8MNH", "retailer_id": "9ad33e7b-1f96-477d-bb95-ee05567a1ec2"},
                {"id": "b7e2e7e7-1054-4448-a8bb-aa3e7ef5aea3", "retailer_product_id": "B09QKGY17H", "retailer_id": "9ad33e7b-1f96-477d-bb95-ee05567a1ec2"},
            ]
        self.attribute_parser = AttributeParser()
    
    async def click_continue_shopping(self, page):
        try:
            continue_shopping = await page.query_selector(".a-button-text[alt='Continue shopping']")
            if continue_shopping:
                await continue_shopping.click()
                await page.wait_for_timeout(2000)
        except Exception as e:
            print("Exception in click shopping method: ",e)

    async def closer(self, context, browser):
        await context.close()
        await browser.close()

    async def sign_in(self, page, id_number=0):
        try:
            totp = pyotp.TOTP(SECRET[id_number])
            await page.fill("input[name='email']", EMAIL[id_number], timeout=4000)
            await page.click("input.a-button-input")

            await page.fill("input[name='password']", PASSWORD[id_number], timeout=4000)
            await page.click("input#signInSubmit")
            await page.wait_for_timeout(2000)

            await page.fill("#auth-mfa-otpcode[name='otpCode']", totp.now(), timeout=4000)
            await page.click("#auth-signin-button[name='mfaSubmit']")
            await page.wait_for_timeout(2000)
            # continue_shopping = await page.query_selector(".a-button-text[alt='Continue shopping']")
            # if continue_shopping:
            #     await continue_shopping.click()
            return page
        except Exception as e:
            print("Exception in Sign in: ",e)
            return page

    async def parse(self, page, product_id, retailer_id, original_url):
        # original = response.request.url
        try:
            page_num = 1
            while True:
                if page_num == 11:
                    break
                await page.wait_for_selector('div#cm_cr-review_list>ul.a-unordered-list.a-nostyle.a-vertical>li[data-hook="review"]', timeout=4000)
                html = await page.content()
                selector = Selector(text=html)

                reviews = selector.css("ul.a-unordered-list.a-nostyle.a-vertical > li[data-hook='review']")
                if not reviews:
                    break
                reviews_data = []
                for r in reviews:
                    item = {}
                    # item['retailerProductId'] = response.meta.get('retailer_product_id')
                    item['productId'] = product_id
                    item['retailerId'] = retailer_id
                    item['sourceUrl'] = original_url
                    # item['responseUrl'] = await page.url
                    item['requestUrl'] = page.url
                    # item['rating_filter'] = rating_filter
                    
                    for key, value in amz_reviews["review_data"].items():
                        if key == "reviewImages":
                            item[key] = self.attribute_parser.css_getall_values_parser(itemlist=value, response=r) or []

                        elif key == "reviewVideos":
                            item[key] = self.attribute_parser.css_getall_values_parser(itemlist=value, response=r) or []

                        elif key == "authorId":
                            full_url = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            if full_url:
                                match = re.search(r'account\.([A-Z0-9]+)', full_url)
                                item[key] = match.group(1) if match else None
                                
                        elif key == "rating":
                            rating_text = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            if rating_text:
                                match = re.search(r'([0-5]\.\d)', rating_text)
                                item[key] = float(match.group(1)) if match else None
                                
                        elif key == "reviewText":
                            item[key] = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            # item[key] = " ".join([text.strip() for text in result.getall()]) if result else None

                        elif key == "helpfulVoteCount":
                            text = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            if text:
                                if "one" in text.lower():
                                    item[key] = 1
                                else:
                                    match = re.search(r'(\d+)', text)
                                    item[key] = int(match.group(1)) if match else 0

                        elif key == "reviewDate":
                            date = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            if date:
                                date_match = re.search(r'on (.+)$', date)
                                if date_match:
                                    raw_date = date_match.group(1).strip()
                                    parsed_date = datetime.strptime(raw_date, "%B %d, %Y")
                                    item[key] = parsed_date.strftime("%Y-%m-%d")
                                else:
                                    item[key] = None

                        elif key == "reviewCountry":
                            country = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            if country:
                                country_match = re.search(r'in (.+?) on', country)
                                item[key] = country_match.group(1).strip() if country_match else None

                        elif key == "isVerified":
                            badge_text = self.attribute_parser.css_value_parser(itemlist=value, response=r)
                            item[key] = badge_text.strip() == "Verified Purchase" if badge_text else False


                        else:
                            item[key] = self.attribute_parser.css_value_parser(itemlist=value, response=r)

                    reviews_data.append(item)
                lines = "\n".join(json.dumps(entry, ensure_ascii=False) for entry in reviews_data) + "\n"
                with open("test.json", "a", encoding="utf-8") as f:
                    f.write(lines)

                # Handle pagination
                next_page_button = page.locator('li.a-last > a')
                if await next_page_button.count() == 0:
                    break
                try:
                    await next_page_button.click()
                    await page.wait_for_timeout(2000)
                    await page.wait_for_selector('div#cm_cr-review_list>ul.a-unordered-list.a-nostyle.a-vertical', timeout=30000)
                    page_num += 1
                except Exception as e:
                    print(e)
                    break
        
        except Exception as e: 
            print("Exception in parse method: ",e)

    async def detect_honeypot(self, page):
        try:
            print("INSIDE HONEYPOT")
            await page.wait_for_timeout(2000)
            continue_shopping = await page.query_selector(".a-button-text[alt='Continue shopping']")
            signin = await page.query_selector("input[name='email']")

            if continue_shopping or signin:
                print(continue_shopping)
                print(signin)
                print("Honeypot not found")
                return False
            else: 
                print(continue_shopping)
                print(signin)
                print("Honeypot found Retrying")
                return True 
            
        except Exception as e:
            print("Error in Honeypot: ", e)
            return page

    async def run(self):
        async with Stealth().use_async(async_playwright()) as p:
            # browser = p.chromium.launch(headless=False, args=["--window-size=1280,800"]) # set to True for headless # context = browser.new_context()
            
            id_number = 0
            for url in self.urls:
                headers = {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "no-cache",
                    "device-memory": "8",
                    "downlink": "10",
                    "dpr": "1",
                    "ect": "4g",
                    "pragma": "no-cache",
                    "priority": "u=0, i",
                    # "referer": "https://www.amazon.com/b/?ie=UTF8&node=19277531011&ref_=af_gw_quadtopcard_f_july_xcat_cml_1&pd_rd_w=Z5OwE&content-id=amzn1.sym.28c8c8b7-487d-484e-96c7-4d7d067b06ed&pf_rd_p=28c8c8b7-487d-484e-96c7-4d7d067b06ed&pf_rd_r=654GDDXPAIA6G9Z3V3G5&pd_rd_wg=RP51i&pd_rd_r=10053101-20a0-4a52-9465-faf1daa6535e",
                    "rtt": "50",
                    "sec-ch-device-memory": "8",
                    "sec-ch-dpr": "1",
                    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Linux"',
                    "sec-ch-viewport-width": "998",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                    "viewport-width": "998",
                }
                full_url = f"https://www.amazon.com/product-reviews/{url['retailer_product_id']}/"
                # url = f"https://ipv4.webshare.io/"
                if id_number == len(EMAIL):
                    id_number = 0
                for tries in range(10):
                    try:
                        browser = await p.chromium.launch(headless=False, args=["--window-size=1280,800"])
                        context = await browser.new_context(
                            proxy={
                                "server": f"{os.getenv('WEBSHARE_SERVER')}",
                                "username": f"{os.getenv('WEBSHARE_USERNAME')}",
                                "password": f"{os.getenv('WEBSHARE_PASSWORD')}",
                            },
                            extra_http_headers={
                                "Authorization": f"Token {os.getenv('WEBSHARE_API_KEY')}"
                            },
                        )
                        page = await context.new_page()

                        await page.set_extra_http_headers(headers)
                        await page.goto(full_url, wait_until="domcontentloaded")
                        await page.wait_for_timeout(2000)

                        res = await self.detect_honeypot(page)
                        if res:
                            await self.closer(context, browser)
                            continue

                        await self.click_continue_shopping(page)


                        res = await self.detect_honeypot(page)
                        if res:
                            await self.closer(context, browser)
                            continue
                        
                        await self.sign_in(page, id_number)

                        await self.parse(page, product_id=url['id'], retailer_id=url['retailer_id'], original_url=full_url)
                        id_number += 1
                        break

                    except Exception as e:
                        print(f" Didn't load page due to: {e}")
                        print(f" Retrying... {tries+1}/10")
                        await self.closer(context, browser)
                        continue
                    
                    finally:
                        await self.closer(context, browser)

if __name__ == "__main__":
    runner = PlaywrightAmzReviews()
    asyncio.run(runner.run())


# # Fill username & password
# totp = pyotp.TOTP(SECRET[0])
# await page.fill("input[name='email']", EMAIL[0])
# await page.click("input.a-button-input")

# await page.fill("input[name='password']", PASSWORD[0])
# await page.click("input#signInSubmit")
# await page.wait_for_timeout(2000)

# await page.fill("#auth-mfa-otpcode[name='otpCode']", totp.now())
# await page.click("#auth-signin-button[name='mfaSubmit']")
# await page.wait_for_timeout(2000)

# await page.wait_for_selector("#nav-global-location-popover-link", timeout=5000)
# await page.click("#nav-global-location-popover-link")

# await page.wait_for_selector("#GLUXZipUpdateInput", timeout=5000)
# await page.fill("#GLUXZipUpdateInput", "10001")

# if await page.query_selector("Button[name='glowDoneButton']"):
#     await page.click("Button[name='glowDoneButton']")
#     await page.wait_for_timeout(3000)

# await page.wait_for_selector("#GLUXZipUpdate", timeout=5000)
# await page.click("#GLUXZipUpdate")
# await page.wait_for_timeout(timeout=3000)

# await page.locator("#GLUXConfirmClose").nth(1).click()

# test = await page.query_selector(".a-unordered-list.a-nostyle.a-vertical.review-views.celwidget")
# if await test:
#     button = await page.locator("div#reviews-medley-footer>div>a[data-hook='see-all-reviews-link-foot']")
#     await button.click()
#     break
# else:
#     continue
    # page.wait_for_timeout(10000)