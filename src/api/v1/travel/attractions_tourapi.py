"""
Attractions TourAPI Module

한국관광공사 TourAPI와의 연동을 담당하는 모듈
- TourAPI locationBasedList2 호출
- API 파라미터 변환 및 에러 처리
- 명세서 기반 정확한 API 연동
"""

import httpx
from typing import Dict, Any
from src.api.v1.travel.attractions_dto import AttractionsCategoryEnum, AttractionsSortEnum

from src.core.logger import get_logger
from src.core.env import env
from src.config.status import ERR

_logger = get_logger(__name__)

# TourAPI 설정
TOUR_API_BASE_URL = "http://apis.data.go.kr/B551011/KorService2"
TOUR_API_KEY = env.TOUR_API_KEY
TOUR_TIMEOUT = httpx.Timeout(10.0)


class AttractionsTourAPI:
    """한국관광공사 TourAPI 연동 클래스"""

    @staticmethod
    async def fetch_location_based_list(
        lat: float,
        lng: float,
        radius: int,
        category: AttractionsCategoryEnum,
        sort: AttractionsSortEnum,
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """
        TourAPI locationBasedList2 호출
        
        Args:
            lat: 위도
            lng: 경도
            radius: 반경 (km)
            category: 카테고리
            sort: 정렬 방식
            limit: 결과 수 제한
            offset: 시작 위치
            
        Returns:
            Dict: TourAPI 응답 데이터
            
        Raises:
            HTTPException: API 호출 실패
        """
        try:
            endpoint = f"{TOUR_API_BASE_URL}/locationBasedList2"
            
            params = {
                "serviceKey": TOUR_API_KEY,
                "numOfRows": str(limit),
                "pageNo": str((offset // limit) + 1),
                "MobileOS": "ETC",
                "MobileApp": "TravelApp",
                "_type": "json",
                "mapX": str(lng),
                "mapY": str(lat),
                "radius": str(radius * 1000),  # km를 m로 변환
                "arrange": AttractionsTourAPI._get_tour_api_sort(sort),
                "contentTypeId": AttractionsTourAPI._get_content_type_id(category)
            }
            
            async with httpx.AsyncClient(timeout=TOUR_TIMEOUT) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # 응답 검증 - TourAPI 응답 구조에 따라 수정
                if "resultCode" in data:
                    # 직접 resultCode가 있는 경우
                    result_code = data.get("resultCode", "Unknown")
                    result_msg = data.get("resultMsg", "Unknown error")
                else:
                    # response.header 구조인 경우
                    result_code = data.get("response", {}).get("header", {}).get("resultCode", "Unknown")
                    result_msg = data.get("response", {}).get("header", {}).get("resultMsg", "Unknown error")
                
                if result_code != "0000":
                    _logger.error(f"TourAPI 오류: {result_code} - {result_msg}")
                    raise ERR.BAD_GATEWAY.to_exception(
                        detail={"error": "TOUR_API_ERROR", "message": f"TourAPI 오류: {result_msg}"}
                    )
                
                # 데이터 추출 - TourAPI 응답 구조에 따라 수정
                if "response" in data and "body" in data["response"]:
                    # 표준 TourAPI 응답 구조
                    body = data["response"]["body"]
                    items = body.get("items", {}).get("item", [])
                    total_count = int(body.get("totalCount", 0))
                elif "items" in data:
                    # 직접 items가 있는 경우
                    items = data.get("items", {}).get("item", [])
                    total_count = int(data.get("totalCount", 0))
                else:
                    # 기타 구조
                    items = []
                    total_count = 0
                
                _logger.info(f"TourAPI 응답: {len(items)}개 아이템")
                
                return {
                    "items": items if isinstance(items, list) else [items] if items else [],
                    "totalCount": total_count,
                    "pageNo": int(data.get("response", {}).get("body", {}).get("pageNo", 1)),
                    "numOfRows": int(data.get("response", {}).get("body", {}).get("numOfRows", limit))
                }
                
        except httpx.HTTPError as e:
            _logger.error(f"TourAPI HTTP 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_HTTP_ERROR", "message": "TourAPI 연결 오류"}
            )
        except Exception as e:
            _logger.error(f"TourAPI 호출 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_CALL_ERROR", "message": "TourAPI 호출 중 오류가 발생했습니다"}
            )

    @staticmethod
    def _get_content_type_id(category: AttractionsCategoryEnum) -> str:
        """카테고리 Enum을 TourAPI contenttypeid로 변환"""
        category_mapping = {
            AttractionsCategoryEnum.ALL: "",
            AttractionsCategoryEnum.TOURIST: "12",
            AttractionsCategoryEnum.CULTURE: "14",
            AttractionsCategoryEnum.FESTIVAL: "15",
            AttractionsCategoryEnum.COURSE: "25",
            AttractionsCategoryEnum.LEISURE: "28",
            AttractionsCategoryEnum.ACCOMMODATION: "32",
            AttractionsCategoryEnum.SHOPPING: "38",
            AttractionsCategoryEnum.RESTAURANT: "39"
        }
        return category_mapping.get(category, "")

    @staticmethod
    def _get_tour_api_sort(sort: AttractionsSortEnum) -> str:
        """정렬 방식 Enum을 TourAPI arrange 파라미터로 변환"""
        sort_mapping = {
            AttractionsSortEnum.DISTANCE: "A",  # 거리순
            AttractionsSortEnum.NAME: "B",      # 제목순
            AttractionsSortEnum.RATING: "C"     # 평점순 (TourAPI에서는 인기도순)
        }
        return sort_mapping.get(sort, "A")

    @staticmethod
    async def fetch_detail_common(content_id: str) -> Dict[str, Any]:
        """
        TourAPI detailCommon2 호출 (공통정보 조회)
        
        Args:
            content_id: 관광지 콘텐츠 ID
            
        Returns:
            Dict: TourAPI 공통정보 응답 데이터
        """
        try:
            endpoint = f"{TOUR_API_BASE_URL}/detailCommon2"
            
            params = {
                "serviceKey": TOUR_API_KEY,
                "numOfRows": "1",
                "pageNo": "1",
                "MobileOS": "ETC",
                "MobileApp": "TravelApp",
                "_type": "json",
                "contentId": content_id
            }
            
            async with httpx.AsyncClient(timeout=TOUR_TIMEOUT) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # 응답 검증 - TourAPI 응답 구조 확인
                if "response" in data and "header" in data["response"]:
                    result_code = data["response"]["header"].get("resultCode", "Unknown")
                    result_msg = data["response"]["header"].get("resultMsg", "Unknown error")
                else:
                    result_code = data.get("resultCode", "Unknown")
                    result_msg = data.get("resultMsg", "Unknown error")
                
                if result_code != "0000":
                    _logger.error(f"TourAPI 오류: {result_code} - {result_msg}")
                    raise ERR.BAD_GATEWAY.to_exception(
                        detail={"error": "TOUR_API_ERROR", "message": f"TourAPI 오류: {result_msg}"}
                    )
                
                # 데이터 추출 - TourAPI 응답 구조에 맞게 수정
                if "response" in data and "body" in data["response"]:
                    body = data["response"]["body"]
                    items = body.get("items", {})
                    if isinstance(items, str) and items == "":
                        items = []
                    elif isinstance(items, dict):
                        items = items.get("item", [])
                    else:
                        items = []
                else:
                    items = data.get("items", {}).get("item", [])
                
                if isinstance(items, dict):
                    items = [items]
                
                
                return {
                    "items": items,
                    "totalCount": len(items)
                }
                
        except httpx.HTTPError as e:
            _logger.error(f"TourAPI HTTP 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_HTTP_ERROR", "message": "TourAPI 연결 오류"}
            )
        except Exception as e:
            _logger.error(f"TourAPI 호출 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_CALL_ERROR", "message": "TourAPI 호출 중 오류가 발생했습니다"}
            )

    @staticmethod
    async def fetch_detail_intro(content_id: str, content_type_id: str) -> Dict[str, Any]:
        """
        TourAPI detailIntro2 호출 (소개정보 조회)
        
        Args:
            content_id: 관광지 콘텐츠 ID
            content_type_id: 관광지 타입 ID
            
        Returns:
            Dict: TourAPI 소개정보 응답 데이터
        """
        try:
            endpoint = f"{TOUR_API_BASE_URL}/detailIntro2"
            
            params = {
                "serviceKey": TOUR_API_KEY,
                "numOfRows": "1",
                "pageNo": "1",
                "MobileOS": "ETC",
                "MobileApp": "TravelApp",
                "_type": "json",
                "contentId": content_id,
                "contentTypeId": content_type_id
            }
            
            async with httpx.AsyncClient(timeout=TOUR_TIMEOUT) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # 응답 검증 - TourAPI 응답 구조 확인
                if "response" in data and "header" in data["response"]:
                    result_code = data["response"]["header"].get("resultCode", "Unknown")
                    result_msg = data["response"]["header"].get("resultMsg", "Unknown error")
                else:
                    result_code = data.get("resultCode", "Unknown")
                    result_msg = data.get("resultMsg", "Unknown error")
                
                if result_code != "0000":
                    _logger.error(f"TourAPI 오류: {result_code} - {result_msg}")
                    raise ERR.BAD_GATEWAY.to_exception(
                        detail={"error": "TOUR_API_ERROR", "message": f"TourAPI 오류: {result_msg}"}
                    )
                
                # 데이터 추출 - TourAPI 응답 구조에 맞게 수정
                if "response" in data and "body" in data["response"]:
                    body = data["response"]["body"]
                    items = body.get("items", {})
                    if isinstance(items, str) and items == "":
                        items = []
                    elif isinstance(items, dict):
                        items = items.get("item", [])
                    else:
                        items = []
                else:
                    items = data.get("items", {}).get("item", [])
                
                if isinstance(items, dict):
                    items = [items]
                
                
                return {
                    "items": items,
                    "totalCount": len(items)
                }
                
        except httpx.HTTPError as e:
            _logger.error(f"TourAPI HTTP 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_HTTP_ERROR", "message": "TourAPI 연결 오류"}
            )
        except Exception as e:
            _logger.error(f"TourAPI 호출 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_CALL_ERROR", "message": "TourAPI 호출 중 오류가 발생했습니다"}
            )

    @staticmethod
    async def fetch_detail_images(content_id: str) -> Dict[str, Any]:
        """
        TourAPI detailImage2 호출 (이미지정보 조회)
        
        Args:
            content_id: 관광지 콘텐츠 ID
            
        Returns:
            Dict: TourAPI 이미지정보 응답 데이터
        """
        try:
            endpoint = f"{TOUR_API_BASE_URL}/detailImage2"
            
            params = {
                "serviceKey": TOUR_API_KEY,
                "numOfRows": "10",
                "pageNo": "1",
                "MobileOS": "ETC",
                "MobileApp": "TravelApp",
                "_type": "json",
                "contentId": content_id,
                "imageYN": "Y"
            }
            
            async with httpx.AsyncClient(timeout=TOUR_TIMEOUT) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # 응답 검증 - TourAPI 응답 구조 확인
                if "response" in data and "header" in data["response"]:
                    result_code = data["response"]["header"].get("resultCode", "Unknown")
                    result_msg = data["response"]["header"].get("resultMsg", "Unknown error")
                else:
                    result_code = data.get("resultCode", "Unknown")
                    result_msg = data.get("resultMsg", "Unknown error")
                
                if result_code != "0000":
                    _logger.error(f"TourAPI 오류: {result_code} - {result_msg}")
                    raise ERR.BAD_GATEWAY.to_exception(
                        detail={"error": "TOUR_API_ERROR", "message": f"TourAPI 오류: {result_msg}"}
                    )
                
                # 데이터 추출 - TourAPI 응답 구조에 맞게 수정
                if "response" in data and "body" in data["response"]:
                    body = data["response"]["body"]
                    items = body.get("items", {})
                    if isinstance(items, str) and items == "":
                        items = []
                    elif isinstance(items, dict):
                        items = items.get("item", [])
                    else:
                        items = []
                else:
                    items = data.get("items", {}).get("item", [])
                
                if isinstance(items, dict):
                    items = [items]
                
                _logger.info(f"📊 TourAPI 이미지정보 결과: {len(items)}개 아이템")
                
                return {
                    "items": items,
                    "totalCount": len(items)
                }
                
        except httpx.HTTPError as e:
            _logger.error(f"TourAPI HTTP 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_HTTP_ERROR", "message": "TourAPI 연결 오류"}
            )
        except Exception as e:
            _logger.error(f"TourAPI 호출 오류: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(
                detail={"error": "TOUR_API_CALL_ERROR", "message": "TourAPI 호출 중 오류가 발생했습니다"}
            )


# TourAPI 인스턴스 생성
attractions_tourapi = AttractionsTourAPI()