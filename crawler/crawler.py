import datetime
import os
import re
import time

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

now = str(datetime.datetime.now())[:-7]

locations = ["신촌", "서강대", "대흥"]
# locations = ["신촌"]

for location in locations:
    url = f"https://map.naver.com/v5/search/{location} 음식점"
    driver.get(url)
    time.sleep(5)
    frame = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
    time.sleep(2)
    driver.switch_to.frame(frame)
    time.sleep(2)

    for page in range(1, 7):  # 네이버지도의 최대 페이지는 6페이지임.
        current_page_num = driver.find_element(By.CSS_SELECTOR, ".qxokY")
        print(current_page_num.text)
        current_page_num = int(current_page_num.text)
        print(f"page for문 변수 : {page}, 실제 페이지 : {current_page_num}")
        if page != current_page_num:  # page 변수와 실제 page 숫자가 다르다면 마지막페이지인 것이므로 break
            break
        scroll_container = driver.find_element(
            By.CSS_SELECTOR, "#_pcmap_list_scroll_container"
        )
        scroll_container_height = (
            'document.body.querySelector("#_pcmap_list_scroll_container").scrollHeight'
        )
        for _ in range(5):
            driver.execute_script(
                f"arguments[0].scrollBy(0,{scroll_container_height})", scroll_container
            )
            time.sleep(0.1)

        restaurant_container = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS")

        # restaurant = {
        #     'naver_restaurant_id': [],
        #     'name' : [],
        #     'location': [],
        #     'restaurant_type': [],
        #     'address': [],
        #     'contact': [],
        #     'rating': [],
        #     'total_review_num': [],
        #     'user_review': [],
        #     'menu_list': []
        # }

        # li 태그들 순회
        for r in restaurant_container:

            restaurant = {
                "naver_restaurant_id": "",
                "name": "",
                "location": "",
                "restaurant_type": "",
                "address": "",
                "contact": "",
                "rating": "",
                "total_review_num": "",
                "menu_list": [],
                "음식이 맛있어요": 0,
                "특별한 메뉴가 있어요": 0,
                "친절해요": 0,
                "재료가 신선해요": 0,
                "양이 많아요": 0,
                "가성비가 좋아요": 0,
                "매장이 넓어요": 0,
                "단체모임 하기 좋아요": 0,
                "특별한 날 가기 좋아요": 0,
                "매장이 청결해요": 0,
                "인테리어가 멋져요": 0,
                "혼밥하기 좋아요": 0,
                "주차하기 편해요": 0,
                "화장실이 깨끗해요": 0,
                "뷰가 좋아요": 0,
                "음식이 빨리 나와요": 0,
                "현지 맛에 가까워요": 0,
                "사진이 잘 나와요": 0,
            }

            try:
                name = r.find_element(By.CSS_SELECTOR, "span.place_bluelink")
                # 음식점 클릭 후 iframe 이동
                name.click()
                time.sleep(3)
                driver.switch_to.default_content()
                time.sleep(2)
                entryIframe = driver.find_element(By.CSS_SELECTOR, "#entryIframe")
                time.sleep(2)
                driver.switch_to.frame(entryIframe)

                # 네이버 상 음식점 id
                url_token = driver.current_url.split("/")
                idx = url_token[-1].index("?")
                naver_restaurant_id = int(url_token[-1][:idx])
                # restaurant["naver_restaurant_id"].append(naver_restaurant_id)
                restaurant["naver_restaurant_id"] = naver_restaurant_id
                print("naver_restaurant_id", naver_restaurant_id)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # 음식점 상호명
                name = soup.select_one("span.Fc1rA").get_text()
                # restaurant["name"].append(name)
                restaurant["name"] = name
                print("음식점 상호명", name)

                # 음식점 위치
                # restaurant["location"].append(location) # 음식점 위치
                restaurant["location"] = location  # 음식점 위치

                # 음식점 종류
                restaurant_type = ""
                try:
                    restaurant_type = soup.select_one("span.DJJvD").get_text()
                except Exception as e:
                    print("음식점 종류 예외발생 : ", e)
                    pass
                # restaurant["restaurant_type"].append(restaurant_type)
                restaurant["restaurant_type"] = restaurant_type
                print("종류", restaurant_type)

                # 주소
                address = ""
                try:
                    address = soup.select_one("span.IH7VW").get_text()
                except Exception as e:
                    print("주소 예외발생 : ", e)
                    pass
                # restaurant["address"].append(address)
                restaurant["address"] = address
                print("주소", address)

                # 별점
                rating = ""
                try:
                    rating = soup.select_one("span.PXMot.LXIwF em").get_text()
                except Exception as e:
                    print("별점 예외발생 : ", e)
                    pass
                # restaurant["rating"].append(rating)
                restaurant["rating"] = rating
                print("별점", rating)

                # 리뷰 수
                total_review_num = ""
                try:
                    review_num = soup.select("span.PXMot em")
                    try:
                        visitor_review_num = int(
                            review_num[1].get_text().replace(",", "")
                        )
                    except:
                        visitor_review_num = 0

                    try:
                        blog_review_num = int(review_num[2].get_text().replace(",", ""))
                    except:
                        blog_review_num = 0

                    total_review_num = visitor_review_num + blog_review_num
                except Exception as e:
                    print("리뷰 수 예외발생 : ", e)
                    pass
                # restaurant["total_review_num"].append(total_review_num)
                restaurant["total_review_num"] = total_review_num
                print("리뷰합계", total_review_num)

                # 전화번호
                contact = ""
                try:
                    contact = soup.select_one("span.dry01").get_text()
                except Exception as e:
                    print("전화번호 예외발생 : ", e)
                    pass
                # restaurant["contact"].append(contact)
                restaurant["contact"] = contact
                print("전화번호", contact)

                # 메뉴
                try:
                    menu_link = (
                        "https://pcmap.place.naver.com/restaurant/"
                        + str(naver_restaurant_id)
                        + "/menu/list"
                    )
                    req = requests.get(menu_link)
                    html = req.content
                    menu_soup = BeautifulSoup(html, "html.parser")
                    menu_list = menu_soup.select("ul.ZUYk_ li.P_Yxm")
                    temp = []
                    for menu in menu_list:
                        menu_name = ""
                        menu_price = ""
                        menu_img_url = ""

                        menu_dict = {
                            "menu_name": "",
                            "menu_price": "",
                            "menu_img_url": "",
                        }

                        menu_name = menu.select_one("span.Sqg65").get_text()
                        if menu.select_one("span.GPETv"):
                            menu_name += " [대표]"

                        # 메뉴 가격
                        try:
                            menu_price = menu.select_one("div.SSaNE").get_text()
                        except:
                            menu_price = ""

                        try:
                            menu_img = menu.find(
                                "div", attrs={"class": "K0PDV", "style": True}
                            )
                            if menu_img:
                                menu_img_url = re.search(
                                    r'url\("(.+)"\)', menu_img["style"]
                                ).group(1)
                            else:
                                menu_img_url = ""
                        except:
                            menu_img_url = ""
                        menu_dict["menu_name"] = menu_name
                        menu_dict["menu_price"] = menu_price
                        menu_dict["menu_img_url"] = menu_img_url
                        temp.append(menu_dict)
                    restaurant["menu_list"].append(temp)
                    print(temp)
                except Exception as e:
                    print("메뉴 예외발생 : ", e)
                    restaurant["menu_list"].append("")
                    # restaurant["menu_list"] = ""

                # 사용자 리뷰 (user_review)
                try:
                    review_tab = driver.find_element(
                        By.CSS_SELECTOR, 'a[href*="review"]'
                    )
                    if review_tab:
                        review_tab.click()
                        time.sleep(3)
                        review_load_btn = driver.find_element(
                            By.CSS_SELECTOR, "a.Tvx37"
                        )

                        try:
                            for _ in range(3):
                                if review_load_btn:
                                    review_load_btn.click()
                                    time.sleep(3)
                        except Exception as e:
                            print("review_load_btn 예외발생 (큰 문제 아님) : ", e)

                        review_list = driver.find_elements(
                            By.CSS_SELECTOR, "ul.uNsI9 li.nbD78"
                        )
                        time.sleep(3)

                        review_dict = {}
                        for review in review_list:
                            review_feature = review.find_element(
                                By.CSS_SELECTOR, "span.nWiXa"
                            ).text.replace('"', "")
                            review_cnt = int(
                                review.find_element(
                                    By.CSS_SELECTOR, "span.TwM9q"
                                ).text.split("\n")[1]
                            )
                            # review_dict[review_feature] = review_cnt
                            if review_feature in restaurant:
                                # restaurant[review_feature].append(review_cnt)
                                restaurant[review_feature] = review_cnt
                                print(review_feature, ":", review_cnt)
                        # restaurant["user_review"].append(review_dict)
                        # restaurant["user_review"] = review_dict
                except Exception as e:
                    print("사용자 리뷰 예외발생 : ", e)
                    # restaurant["user_review"].append("")
                    # restaurant["user_review"] = ""

                driver.switch_to.default_content()
                time.sleep(3)
                driver.switch_to.frame(frame)
                time.sleep(3)
                print("")

                df = pd.DataFrame(restaurant)

                if not os.path.exists(
                    f"{os.path.dirname(os.path.realpath(__file__))}/restaurant_{now}.csv"
                ):
                    df.to_csv(
                        f"{os.path.dirname(os.path.realpath(__file__))}/restaurant_{now}.csv",
                        mode="w",
                        index=False,
                        encoding="utf-8-sig",
                    )
                else:
                    df.to_csv(
                        f"{os.path.dirname(os.path.realpath(__file__))}/restaurant_{now}.csv",
                        mode="a",
                        index=False,
                        header=False,
                        encoding="utf-8-sig",
                    )

            except Exception as e:
                print("예외발생 : ", e)
            time.sleep(3)

        next_page_btn = driver.find_element(
            By.CSS_SELECTOR, "div.zRM9F a.eUTV2:last-child"
        )
        next_page_btn.click()
        time.sleep(2)

driver.quit()
