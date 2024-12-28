# RASA
**Naver Boostcamp AI Tech 7기 - 창업 스터디 팀**
안녕하세요! 이번 프로젝트(Recommend Application for Study Room, RASA)를 위해 repo.를 만들었습니다! 
작업할 때 다음과 같은 규칙에 유의하여 진행해주시길 부탁드립니다.

## Branch naming rule
- main branch 수정은 README.md만 가능합니다.
- 사용할 수 있는 브렌치 명은 다음 4개로 제안합니다.  'develop' / 'exp' / 'feat' / 'fix'
- 모든 작업은 develop을 기준으로 최종 병합됩니다. 따라서 develop에 바로 코드를 작성하지 않습니다.
- 필요한 기능은 feat / 본격적인 개발은 exp를 앞에 붙여 명명해주시면 됩니다.
- fix 는 버그 수정에 사용하며, 사용 후 가급적 제거해주세요!
- MVP 구현 단계에 따라 develop -> version으로 올려, 배포 버전을 관리합니다.

## 우선적으로 규칙을 정하다보니, 협업 규칙에 있어 수정이 필요하면 함께 토의 부탁드립니다!

이 외 모든 사항에 대해서는 자유롭게 작업하면서, 간단한 예시를 남기겠습니다.
ex) 
- 브랜치 이름 - 'exp/data_crawling' : 데이터 크롤링 코드 작성
- 브랜치 이름 - 'exp/sync_slack2backend' : 슬랙과 백엔드 연결 코드 작성


## 구현 목표
* 공부할 때 어디서 모일지 매번 고민했던 경험
* 사용자 위치 기반으로, 모임 위치를 추천해주는 Slack bot 개발
* 추천된 위치의 스터디 카페 등 학습 공간, 근처 식당을 추천하는 기능 개발
