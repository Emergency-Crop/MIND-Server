"""
Feed Service Module

사용자 아키타입 기반 피드 조회 비즈니스 로직
"""

import httpx
import base64
import json
from typing import List, Optional, Tuple, Dict
from uuid import UUID
from src.api.v1.feed.feed_dto import (
    FeedRequestDTO, FeedResponseDTO, TravelLogItemDTO,
    UserProfileDTO, FeedMetaDTO
)
from src.core.env import env
from src.core.logger import get_logger
from src.config.status import ERR

_logger = get_logger(__name__)


class FeedService:
    def __init__(self):
        self.supabase_url = env.SUPABASE_URL
        self.supabase_key = env.SUPABASE_ANON_KEY
        self.timeout = httpx.Timeout(10.0)
        
    async def test_supabase_connection(self) -> Dict:
        """
        Supabase 연결 상태를 테스트합니다.
        """
        try:
            # 1. 환경 변수 확인
            config_info = {
                "supabase_url": self.supabase_url,
                "supabase_key_length": len(self.supabase_key) if self.supabase_key else 0,
                "timeout": str(self.timeout)
            }
            
            # 2. 간단한 API 호출 테스트 (profiles 테이블 조회)
            url = f"{self.supabase_url}/rest/v1/profiles"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            params = {
                "select": "id",
                "limit": "1"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                return {
                    "status": "success",
                    "message": "Supabase 연결 성공",
                    "config": config_info,
                    "test_query": {
                        "url": url,
                        "status_code": response.status_code,
                        "response_count": len(data) if isinstance(data, list) else 0,
                        "headers": dict(response.headers)
                    }
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"HTTP 오류: {e.response.status_code}",
                "config": config_info,
                "error": str(e),
                "response_text": e.response.text if hasattr(e.response, 'text') else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"연결 오류: {str(e)}",
                "config": config_info,
                "error": str(e)
            }

    async def get_feed(self, dto: FeedRequestDTO) -> FeedResponseDTO:
        """
        사용자 아키타입 기반 피드를 조회합니다.
        """
        try:
            # 1. 사용자 프로필 조회 (아키타입 포함)
            user_profile = await self._get_user_profile(dto.user_id)
            if not user_profile:
                raise ERR.NOT_FOUND.to_exception(detail={"user_id": str(dto.user_id)})
            
            # 2. 같은 아키타입을 가진 여행 로그 조회
            try:
                travel_logs, total_count, next_cursor = await self._get_travel_logs_by_archetype(
                    user_profile.archetype, dto.limit, dto.cursor
                )
            except Exception as e:
                _logger.warning(f"Failed to get travel logs for archetype {user_profile.archetype}: {str(e)}")
                # travel_logs 조회 실패 시 빈 결과 반환
                travel_logs, total_count, next_cursor = [], 0, None
            
            # 3. 페이지네이션 정보 생성
            has_more = next_cursor is not None
            
            # 4. 메타 정보 생성
            meta = FeedMetaDTO(
                user_profile=user_profile,
                total_count=total_count,
                current_count=len(travel_logs),
                limit=dto.limit,
                has_more=has_more,
                next_cursor=next_cursor
            )
            
            # 5. 응답 생성
            return FeedResponseDTO(
                meta=meta,
                items=travel_logs
            )
            
        except Exception as e:
            if hasattr(e, 'status_code'):
                # 이미 처리된 에러는 그대로 전달
                raise e
            
            _logger.error(f"Unexpected error in feed service: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="피드 조회 중 오류가 발생했습니다")

    async def _get_user_profile(self, user_id: UUID) -> Optional[UserProfileDTO]:
        """
        사용자 프로필을 조회합니다.
        """
        try:
            # Supabase REST API를 사용하여 profiles 테이블 조회
            url = f"{self.supabase_url}/rest/v1/profiles"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            params = {
                "id": f"eq.{user_id}",
                "select": "id,archetype,display_name,profile_image_url,bio"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    _logger.warning(f"User profile not found for user_id: {user_id}")
                    return None
                
                profile_data = data[0]
                
                return UserProfileDTO(
                    id=UUID(profile_data["id"]),
                    archetype=profile_data["archetype"],
                    display_name=profile_data["display_name"],
                    profile_image_url=profile_data.get("profile_image_url"),
                    bio=profile_data.get("bio")
                )
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                _logger.warning(f"User profile not found for user_id: {user_id}")
                return None
            _logger.error(f"HTTP error in get_user_profile: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(detail="데이터베이스 연결 오류")
        except Exception as e:
            _logger.error(f"Error in get_user_profile: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="사용자 프로필 조회 중 오류가 발생했습니다")

    async def _get_travel_logs_by_archetype(
        self, archetype: str, limit: int, cursor: Optional[str] = None
    ) -> Tuple[List[TravelLogItemDTO], int, Optional[str]]:
        """
        아키타입을 기반으로 여행 로그를 조회합니다.
        """
        try:
            # Supabase REST API를 사용하여 travel_logs 테이블 조회
            url = f"{self.supabase_url}/rest/v1/travel_logs"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # 2. 커서 기반 쿼리 구성
            params = {
                "archetype": f"eq.{archetype}",
                "is_public": "eq.true",  # 공개된 로그만
                "select": "id,created_at",
                "order": "created_at.desc,id.desc",  # 최신순 정렬 (커서 안정성을 위해 id도 포함)
                "limit": str(limit + 1)  # 다음 페이지 확인을 위해 1개 더 요청
            }
            
            # 커서가 있으면 필터 추가
            if cursor:
                try:
                    # URL 디코딩 먼저 수행
                    import urllib.parse
                    decoded_cursor = urllib.parse.unquote(cursor)
                    _logger.info(f"URL decoded cursor: {decoded_cursor}")
                    
                    # Base64 디코딩
                    cursor_bytes = base64.b64decode(decoded_cursor)
                    cursor_str = cursor_bytes.decode('utf-8')
                    _logger.info(f"Decoded cursor: {cursor_str}")
                    
                    cursor_data = json.loads(cursor_str)
                    created_at = cursor_data.get('created_at')
                    last_id = cursor_data.get('id')
                    
                    if created_at and last_id:
                        # 커서 기반 필터: created_at이 같으면 id로, 다르면 created_at으로
                        params["or"] = f"(created_at.lt.{created_at}),(and(created_at.eq.{created_at},id.lt.{last_id}))"
                        _logger.info(f"Applied cursor filter: created_at={created_at}, id={last_id}")
                    else:
                        _logger.warning(f"Missing cursor data: created_at={created_at}, id={last_id}")
                        
                except Exception as e:
                    _logger.warning(f"Invalid cursor format: {str(e)}")
                    _logger.warning(f"Original cursor: {cursor}")
                    # 잘못된 커서는 무시하고 처음부터 조회
            
            # 쿼리 실행
            return await self._execute_query(url, headers, params, limit, archetype)
                
        except httpx.HTTPStatusError as e:
            _logger.error(f"HTTP error in get_travel_logs_by_archetype: {str(e)}")
            _logger.error(f"Response text: {e.response.text}")
            _logger.error(f"Response headers: {dict(e.response.headers)}")
            # 테이블이 없거나 접근 권한이 없는 경우 빈 결과 반환
            return [], 0, None
        except Exception as e:
            _logger.error(f"Error in get_travel_logs_by_archetype: {str(e)}")
            # 예상치 못한 오류의 경우 빈 결과 반환
            return [], 0, None

    async def _get_total_count_by_archetype(self, archetype: str) -> int:
        """
        특정 아키타입의 전체 여행 로그 개수를 조회합니다.
        """
        try:
            # Supabase REST API를 사용하여 개수 조회
            url = f"{self.supabase_url}/rest/v1/travel_logs"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "count=exact"  # 정확한 개수 요청
            }
            params = {
                "archetype": f"eq.{archetype}",
                "is_public": "eq.true",
                "select": "id"  # 개수만 필요하므로 id만 선택
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                # Content-Range 헤더에서 전체 개수 추출
                content_range = response.headers.get("content-range", "")
                if content_range:
                    # "0-19/100" 형태에서 마지막 숫자 추출
                    total_count = int(content_range.split("/")[-1])
                    return total_count
                
                # Content-Range가 없는 경우 응답 데이터 길이 반환
                return len(response.json())
                
        except Exception as e:
            _logger.error(f"Error in get_total_count_by_archetype: {str(e)}")
            return 0

    async def _execute_query(self, url: str, headers: dict, params: dict, limit: int, archetype: str) -> Tuple[List[TravelLogItemDTO], int, Optional[str]]:
         """
         실제 쿼리를 실행하고 결과를 처리합니다.
         """
         # 실제 쿼리 URL 로깅
         query_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
         _logger.info(f"Actual query URL: {query_url}")
         _logger.info(f"Query params: {params}")
         
         async with httpx.AsyncClient(timeout=self.timeout) as client:
             response = await client.get(url, headers=headers, params=params)
             _logger.info(f"Response status: {response.status_code}")
             _logger.info(f"Response headers: {dict(response.headers)}")
             _logger.info(f"Response data: {response.text}")
             
             response.raise_for_status()
             
             data = response.json()
             
             # TravelLogItemDTO로 변환 및 다음 커서 생성
             travel_logs = []
             next_cursor = None
             
             # limit + 1개를 요청했으므로, 마지막 항목으로 다음 커서 생성
             actual_data = data[:limit]  # 실제 반환할 데이터
             has_more = len(data) > limit  # 다음 페이지 존재 여부
             
             for item in actual_data:
                 travel_log = TravelLogItemDTO(
                     id=UUID(item["id"]),
                     created_at=item["created_at"]
                 )
                 travel_logs.append(travel_log)
             
             # 다음 커서 생성 (마지막 항목 기준)
             if has_more and travel_logs:
                 last_item = data[limit - 1]  # 마지막 항목
                 cursor_data = {
                     "created_at": last_item["created_at"],
                     "id": str(last_item["id"])
                 }
                 next_cursor = base64.b64encode(json.dumps(cursor_data).encode('utf-8')).decode('utf-8')
             
             # 전체 개수 조회 (페이지네이션용)
             total_count = await self._get_total_count_by_archetype(archetype)
             
             return travel_logs, total_count, next_cursor


# 서비스 인스턴스 생성
feed_service = FeedService()
