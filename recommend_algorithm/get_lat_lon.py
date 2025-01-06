import pandas as pd
from geopy.geocoders import Nominatim

def get_lat_lon(address):
    try:
        # Nominatim geolocator 객체 생성
        geolocator = Nominatim(user_agent="my_geocoder")
        # 주소를 기반으로 위치 정보 가져오기
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# CSV 파일 읽기
input_file = "subway_station.csv"  # 입력 파일 경로
output_file = "subway_station_with_lat_lon.csv"  # 출력 파일 경로

# CSV 파일 로드
df = pd.read_csv(input_file)

# 위도와 경도 값 추가
df['latitude'], df['longitude'] = zip(*df['address'].apply(get_lat_lon))

# 결과를 CSV로 저장
df.to_csv(output_file, index=False, encoding="utf-8-sig")
