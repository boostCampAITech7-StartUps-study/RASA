import pandas as pd
from geopy.geocoders import Nominatim
from sklearn.cluster import KMeans
import math

class StudyroomRecommender:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="studyroom_recommender")

    def get_lat_lon(self, address):
        try:
            location = self.geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                print(f"주소를 찾을 수 없습니다: {address}")
                return None, None
        except Exception as e:
            print(f"Error 처리 중: {address}, 에러: {e}")
            return None, None

    def find_optimal_center(self, coordinates, k=1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(coordinates)
        center_lat, center_lon = kmeans.cluster_centers_[0]
        return center_lat, center_lon

    def haversine(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        r = 6371.0
        return r * c

    def get_nearest_subways(self, user_addresses, subway_file):
        # 유저 주소를 기반으로 위도와 경도 변환
        user_data = pd.DataFrame(user_addresses, columns=['address'])
        user_data[['latitude', 'longitude']] = user_data['address'].apply(
            lambda x: pd.Series(self.get_lat_lon(x))
        )

        # 유효하지 않은 데이터 출력
        invalid_data = user_data[user_data['latitude'].isna()]
        if not invalid_data.empty:
            print("위도와 경도를 찾을 수 없는 주소 목록:")
            print(invalid_data['address'])

        # 유효한 위도/경도 데이터만 추출
        valid_data = user_data.dropna(subset=['latitude', 'longitude'])
        coordinates = valid_data[['latitude', 'longitude']].to_numpy()

        if coordinates.size > 0:
            # 최적 중심 좌표 계산
            center_lat, center_lon = self.find_optimal_center(coordinates, k=1)

            # 지하철역 데이터 읽기
            subway_data = pd.read_csv(subway_file)

            # 중심 좌표와 각 지하철역 간 거리 계산
            subway_data['distance'] = subway_data.apply(
                lambda row: self.haversine(center_lat, center_lon, row['latitude'], row['longitude']), axis=1
            )

            # 최소 거리 상위 5개의 지하철역 반환
            top_5_subways = subway_data.nsmallest(5, 'distance')['subway_station']
            return top_5_subways.tolist()
        else:
            print("유효한 좌표가 없어 중심 좌표를 계산할 수 없습니다.")
            return []

    def recommend_studyroom(self, df, target_stations, wifi=True, group=True):
        # 지정된 역 근처의 스터디룸만 필터링
        df = df[df['subway'].isin(target_stations)].copy()
        
        # 무선 인터넷이 되는 스터디룸만 필터링
        if wifi:
            df = df[df['note'].str.contains('무선 인터넷', na=False)]
        
        # 단체 이용이 되는 스터디룸만 필터링
        if group:
            df = df[df['note'].str.contains('단체 이용 가능', na=False)]
        
        # 전체 리뷰 수 계산 (방문자 리뷰 + 블로그 리뷰)
        df['visitor_review'] = df['visitor_review'].str.extract('(\d+)').astype(float).fillna(0)
        df['blog_review'] = df['blog_review'].str.extract('(\d+)').astype(float).fillna(0)
        df['total_reviews'] = df['visitor_review'] + df['blog_review']
        
        # 점수 계산을 위한 정규화 함수
        def normalize_score(series):
            if series.max() == series.min():
                return series.apply(lambda x: 1 if x > 0 else 0)
            return (series - series.min()) / (series.max() - series.min())
        
        # 역세권 점수 계산 (40%)
        df['distance'] = df['subway_distance'].str.extract(r'(\d+)(?=m)').astype(float).fillna(0)
        df['distance_score'] = normalize_score(1 - df['distance']) * 0.4

        # 리뷰 점수 계산 (30%)
        df['review_score'] = normalize_score(df['total_reviews']) * 0.3

        # 가격 점수 계산 (30%)
        df['price_score'] = df['orginized_price'].apply(lambda x: 0 if x == '가격정보 없음' else 1) * 0.3
        
        # 총점 계산
        df['total_score'] = df['review_score'] + df['distance_score'] + df['price_score']
        
        # 상위 5개 스터디룸 추천
        top_5 = df.nlargest(5, 'total_score')[['name', 'address', 'subway_distance', 'total_reviews', 'orginized_price']]
        top_5['total_reviews'] = top_5['total_reviews'].apply(lambda x: f'리뷰 수 {int(x)}개')

        return top_5

if __name__ == "__main__":
    recommender = StudyroomRecommender()
    user_addresses = [
        "서울특별시 강남구 역삼동",
        "서울특별시 마포구 서교동",
        "서울특별시 송파구 잠실동"
    ]
    df = pd.read_csv('studyroom_df_result.csv')
    target_stations = recommender.get_nearest_subways(user_addresses, 'subway_station_with_lat_lon.csv')
    recommendations = recommender.recommend_studyroom(df, target_stations)
    print(recommendations)
