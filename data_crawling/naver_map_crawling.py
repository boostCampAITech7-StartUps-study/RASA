from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import random
rd = random.uniform(1,2)

def scroll_down(driver):
    """스크롤을 끝까지 내리면서 새로운 항목을 로드하는 함수"""
    scrollable_element = driver.find_element(By.CLASS_NAME, "Ryr1F")
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
    no_change_count = 0  # 높이 변화 없음을 카운트
    max_retries = 3  # 최대 재시도 횟수
    
    while no_change_count < max_retries:
        # 현재 스크롤 위치 확인
        # current_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_element)
        total_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
        
        # 요소 내에서 아래로 스크롤
        driver.execute_script("arguments[0].scrollTop += 600;", scrollable_element)
        time.sleep(rd)  # 동적 콘텐츠 로드 시간에 따라 조절
        
        # 새 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
        new_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_element)
        
        # 스크롤이 바닥에 도달했는지 확인
        if new_height == last_height and new_scroll + scrollable_element.rect['height'] >= total_height:
            no_change_count += 1
            # print(f"스크롤 변화 없음: {no_change_count}/{max_retries}")
        else:
            no_change_count = 0  # 변화가 있으면 카운트 리셋
            
        last_height = new_height
        
    #     # 현재 진행상황 출력
    #     progress = (new_scroll / total_height) * 100 if total_height > 0 else 0
    #     print(f"스크롤 진행률: {progress:.1f}%")

    # print("스크롤 완료")

def crawl_detail(soup):
    try:
        name = soup.select_one('span.GHAhO')
        name = name.text if name else '이름정보 없음'

        address = soup.select_one('span.LDgIH')
        address = address.text if address else '주소정보 없음'
        
        subway = soup.select_one('div.nZapA')
        subway = subway.get_text(separator=' ', strip=True) if subway else '역정보 없음'
        
        call = soup.select_one('span.xlx7Q')
        call = call.text if call else '가격정보 없음'

        price = soup.select_one('ul.Jp8E6.a0hWz')
        price = price.text if price else '가격정보 없음'

        url = soup.select_one('div.jO09N')
        url = url.text if url else 'URL정보 없음'
        
        note = soup.select_one('div.xPvPE')
        note = note.text if note else '비고 없음'
        
        reviews = soup.select('div.dAsGb')
        # 방문자 리뷰 추출
        visitor_review = next(
            (item.text.strip() for item in reviews if '방문자 리뷰' in item.text), 
            '방문자 리뷰 없음'
        )

        # 블로그 리뷰 추출
        blog_review = next(
            (item.text.strip() for item in reviews if '블로그 리뷰' in item.text), 
            '블로그 리뷰 없음'
        )
        
        # grade = soup.select_one('ul.K4J9r')
        # grade = grade.text if grade else '평가정보 없음'
        
        return {
            'name': name,
            'address': address,
            'subway': subway,
            'call': call,
            'price': price,
            'url': url,
            'note': note,
            'visitor_review': visitor_review,
            'blog_review': blog_review,
            # 'grade': grade,
        }
    except Exception as e:
        print(f"상세정보 추출 중 오류: {e}")
        return None

def save_to_csv(results, query):
    """결과를 CSV 파일로 저장하는 함수"""
    if not results:
        print("저장할 데이터가 없습니다.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{query}_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"데이터가 {filename}에 저장되었습니다.")

def search_and_scrape(query):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    try:
        driver.get(f"https://map.naver.com/v5/search/{query}")
        time.sleep(3)
        
        # 검색 결과 iframe으로 전환
        search_frame = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe")))
        driver.switch_to.frame(search_frame)
        
        # 스크롤 끝까지 내리기
        scroll_down(driver)
        
        # 모든 장소 elements 가져오기
        places = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.qbGlu")))
        total_places = len(places)
        print(f"총 {total_places}개의 장소를 찾았습니다.")
        
        results = []
        for idx, place in enumerate(places, 1):
            try:
                # StaleElementReferenceException 처리를 위한 재시도 로직
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        place.find_element(By.CSS_SELECTOR, ".place_bluelink").click()
                        break
                    except StaleElementReferenceException:
                        if retry == max_retries - 1:
                            raise
                        driver.switch_to.default_content()
                        driver.switch_to.frame(search_frame)
                        places = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.qbGlu")))
                        place = places[idx-1]
                
                time.sleep(2)
                
                driver.switch_to.default_content()
                entry_frame = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#entryIframe")))
                driver.switch_to.frame(entry_frame)
                
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                details = crawl_detail(soup)
                
                if details:
                    results.append(details)
                
                driver.switch_to.default_content()
                driver.switch_to.frame(search_frame)
                
            except Exception as e:
                print(f"항목 처리 중 오류 발생: {e}")
                # iframe 재설정
                driver.switch_to.default_content()
                driver.switch_to.frame(search_frame)
                continue
                
        return results
        
    finally:
        driver.quit()

def main():
    # 검색할 역 이름 목록
    stations = [
        # "홍대", "합정", "상수", "연남" 
        # "신촌", "이대", "아현", "연희"
        # "명동역", "을지로", "동대문역" 
        # "영등포", "여의도", "당산", "문래" 
        # "송파", "잠실", "관악", "신림", "서울대입구" 
    ]
    
    # 전체 결과 저장할 리스트
    # all_results = []
    for station in stations:
        query = f"{station} 스터디룸"
        print(f"\n--- '{query}' 검색 시작 ---")
        
        # 크롤링 실행
        results = search_and_scrape(query)
        
        # 결과 출력
        print(f"\n총 {len(results)}개의 장소 정보를 추출했습니다.")
        
        # 개별 CSV 저장
        save_to_csv(results, query)

        # 결과 통합 저장
        # all_results.extend(results)
        
        # 속도 조절 (각 역 검색 사이에 대기 시간 추가)
        wait_time = random.uniform(10, 20)  # 10~20초 사이 랜덤 대기
        print(f"다음 검색을 위해 {wait_time:.1f}초 대기 중...")
        time.sleep(wait_time)
    
    # if all_results:
    #     # 딕셔너리 중복 제거
    #     unique_results = list({frozenset(item.items()): item for item in all_results}.values())
    #     # 통합된 결과를 저장
    #     station_name = "⋅".join(stations)
    #     save_to_csv(unique_results, station_name)

if __name__ == "__main__":
    main()