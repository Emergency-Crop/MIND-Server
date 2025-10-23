"""
Feed Service Module

사용자 아키타입 기반 피드 조회 비즈니스 로직
"""

import httpx
import base64
import json
import asyncio
from functools import lru_cache
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
    # 가중치 상수
    WEIGHT_PROFILE_ONLY = 100  # 신규 사용자 프로필 가중치
    WEIGHT_PROFILE_PRIORITY = 80  # 초보 사용자 프로필 가중치
    WEIGHT_OTHER_ARCHETYPES = 30  # 초보 사용자 다른 아키타입 가중치
    WEIGHT_PROFILE_HYBRID = 60  # 성장 사용자 프로필 가중치
    WEIGHT_MIN = 10  # 최소 가중치
    WEIGHT_MAX = 100  # 최대 가중치
    WEIGHT_DEFAULT = 10  # 기본 가중치
    
    # 시간 점수 상수
    TIME_SCORE_BASE = 100  # 시간 점수 기준값
    TIME_SCORE_DECAY = 5  # 하루당 감소 점수
    
    # 사용자 단계 상수
    BEGINNER_THRESHOLD = 3  # 초보 사용자 임계값
    GROWING_THRESHOLD = 10  # 성장 사용자 임계값
    
    # 가중치 혼합 비율
    BEHAVIOR_RATIO = 0.7  # 행동 패턴 비율
    
    # 기본 아키타입 리스트 (fallback용)
    DEFAULT_ARCHETYPES = ["adventurer", "감성 수집가", "교감러", "향수러", "고요한 회복러", "힐링러"]
    
    def __init__(self):
        self.supabase_url = env.SUPABASE_URL
        self.supabase_key = env.SUPABASE_ANON_KEY
        self.timeout = httpx.Timeout(10.0)
        # 사용자 가중치 캐시 (5분간 유효)
        self._user_weights_cache = {}
        self._cache_ttl = 300  # 5분
        
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
                "select": "id,created_at,archetype",
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
                     created_at=item["created_at"],
                     archetype=item["archetype"]
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


    async def get_personalized_feed(self, dto: FeedRequestDTO) -> FeedResponseDTO:
        """
        사용자의 과거 여행 로그 패턴을 분석하여 개인화된 피드를 조회합니다.
        병렬 처리를 통해 성능을 최적화합니다.
        """
        try:
            # 1. 사용자 프로필 조회와 아키타입 선호도 분석을 병렬로 실행
            user_profile_task = self._get_user_profile(dto.user_id)
            user_archetype_weights_task = self._analyze_user_archetype_preferences(dto.user_id)
            
            # 병렬 실행
            user_profile, user_archetype_weights = await asyncio.gather(
                user_profile_task,
                user_archetype_weights_task,
                return_exceptions=True
            )
            
            # 예외 처리
            if isinstance(user_profile, Exception):
                raise user_profile
            if isinstance(user_archetype_weights, Exception):
                raise user_archetype_weights
                
            if not user_profile:
                raise ERR.NOT_FOUND.to_exception(detail={"user_id": str(dto.user_id)})
            
            # 3. 개인화된 여행 로그 조회
            try:
                travel_logs, total_count, next_cursor = await self._get_personalized_travel_logs(
                    dto.user_id, user_archetype_weights, dto.limit, dto.cursor
                )
            except Exception as e:
                _logger.warning(f"Failed to get personalized travel logs: {str(e)}")
                # 개인화된 조회 실패 시 빈 결과 반환
                travel_logs, total_count, next_cursor = [], 0, None
            
            # 4. 페이지네이션 정보 생성
            has_more = next_cursor is not None
            
            # 5. 메타 정보 생성
            meta = FeedMetaDTO(
                user_profile=user_profile,
                total_count=total_count,
                current_count=len(travel_logs),
                limit=dto.limit,
                has_more=has_more,
                next_cursor=next_cursor
            )
            
            # 6. 응답 생성
            return FeedResponseDTO(
                meta=meta,
                items=travel_logs
            )
            
        except Exception as e:
            if hasattr(e, 'status_code'):
                # 이미 처리된 에러는 그대로 전달
                raise e
            
            _logger.error(f"Unexpected error in personalized feed service: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="개인화된 피드 조회 중 오류가 발생했습니다")

    async def _analyze_user_archetype_preferences(self, user_id: UUID) -> Dict[str, int]:
        """
        사용자의 여행 로그 개수에 따라 적응형 가중치를 계산합니다.
        캐싱을 통해 성능을 최적화합니다.
        """
        import time
        
        # 캐시 확인
        cache_key = str(user_id)
        current_time = time.time()
        
        if cache_key in self._user_weights_cache:
            cached_data, cache_time = self._user_weights_cache[cache_key]
            if current_time - cache_time < self._cache_ttl:
                _logger.info(f"Using cached weights for user {user_id}")
                return cached_data
            else:
                # 캐시 만료
                del self._user_weights_cache[cache_key]
        
        try:
            # 1. 사용자 프로필 조회 (아키타입 정보 필요)
            user_profile = await self._get_user_profile(user_id)
            if not user_profile:
                _logger.warning(f"User profile not found for user_id: {user_id}")
                return {}
            
            # 2. 사용자의 여행 로그 개수 확인
            user_logs_count = await self._get_user_travel_logs_count(user_id)
            
            if user_logs_count == 0:
                # 신규 사용자: 프로필 아키타입 우선
                _logger.info(f"New user {user_id}: Using profile archetype {user_profile.archetype}")
                weights = {user_profile.archetype: self.WEIGHT_PROFILE_ONLY}
                # 캐시 저장
                self._user_weights_cache[cache_key] = (weights, current_time)
                return weights
            
            elif user_logs_count <= self.BEGINNER_THRESHOLD:
                # 초보 사용자: 프로필 우선 + 다양성
                _logger.info(f"Beginner user {user_id}: Profile + diversity strategy")
                weights = {user_profile.archetype: self.WEIGHT_PROFILE_PRIORITY}
                # 다른 아키타입들도 적당한 가중치 부여 (동적으로 가져오기)
                other_archetypes = await self._get_all_archetypes()
                for archetype in other_archetypes:
                    if archetype != user_profile.archetype:
                        weights[archetype] = self.WEIGHT_OTHER_ARCHETYPES
                # 캐시 저장
                self._user_weights_cache[cache_key] = (weights, current_time)
                return weights
            
            elif user_logs_count <= self.GROWING_THRESHOLD:
                # 성장 사용자: 행동 패턴 + 프로필 혼합
                _logger.info(f"Growing user {user_id}: Behavior + profile hybrid")
                behavior_weights = await self._calculate_behavior_weights(user_id)
                profile_weight = {user_profile.archetype: self.WEIGHT_PROFILE_HYBRID}
                weights = self._merge_weights(behavior_weights, profile_weight, ratio=self.BEHAVIOR_RATIO)
                # 캐시 저장
                self._user_weights_cache[cache_key] = (weights, current_time)
                return weights
            
            else:
                # 숙련 사용자: 완전 행동 패턴 기반
                _logger.info(f"Expert user {user_id}: Full behavior-based")
                weights = await self._calculate_behavior_weights(user_id)
                # 캐시 저장
                self._user_weights_cache[cache_key] = (weights, current_time)
                return weights
                
        except Exception as e:
            _logger.error(f"Error analyzing user archetype preferences: {str(e)}")
            # 오류 시 기본 가중치 반환
            return {}

    async def _get_user_travel_logs_count(self, user_id: UUID) -> int:
        """
        사용자의 여행 로그 개수를 조회합니다.
        """
        try:
            url = f"{self.supabase_url}/rest/v1/travel_logs"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            params = {
                "user_id": f"eq.{user_id}",
                "select": "id"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return len(response.json())
                
        except Exception as e:
            _logger.error(f"Error getting user travel logs count: {str(e)}")
            return 0

    async def _calculate_behavior_weights(self, user_id: UUID) -> Dict[str, int]:
        """
        사용자의 행동 패턴을 기반으로 아키타입 가중치를 계산합니다.
        """
        try:
            # 사용자의 travel_logs 조회
            url = f"{self.supabase_url}/rest/v1/travel_logs"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            params = {
                "user_id": f"eq.{user_id}",
                "select": "archetype"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # 아키타입별 빈도 계산
                archetype_counts = {}
                for item in data:
                    archetype = item.get("archetype")
                    if archetype:
                        archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
                
                # 빈도를 가중치로 변환 (최소 10, 최대 100)
                archetype_weights = {}
                if archetype_counts:
                    max_count = max(archetype_counts.values())
                    for archetype, count in archetype_counts.items():
                        # 정규화: WEIGHT_MIN-WEIGHT_MAX 범위로 변환
                        weight = int(self.WEIGHT_MIN + (count / max_count) * (self.WEIGHT_MAX - self.WEIGHT_MIN))
                        archetype_weights[archetype] = weight
                
                return archetype_weights
                
        except Exception as e:
            _logger.error(f"Error calculating behavior weights: {str(e)}")
            return {}

    async def _get_all_archetypes(self) -> List[str]:
        """
        데이터베이스에서 실제로 사용되는 모든 아키타입을 조회합니다.
        """
        try:
            url = f"{self.supabase_url}/rest/v1/travel_logs"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            params = {
                "select": "archetype",
                "archetype": "not.is.null"  # null이 아닌 아키타입만
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                # 중복 제거하여 고유한 아키타입만 반환
                unique_archetypes = list(set(item.get("archetype") for item in data if item.get("archetype")))
                _logger.info(f"Found {len(unique_archetypes)} unique archetypes: {unique_archetypes}")
                return unique_archetypes
                
        except Exception as e:
            _logger.error(f"Error getting all archetypes: {str(e)}")
            # 오류 시 기본 아키타입 반환
            return self.DEFAULT_ARCHETYPES

    def _merge_weights(self, behavior_weights: Dict[str, int], profile_weights: Dict[str, int], ratio: float = 0.7) -> Dict[str, int]:
        """
        행동 패턴 가중치와 프로필 가중치를 비율에 따라 혼합합니다.
        """
        merged_weights = {}
        
        # 행동 패턴 가중치 적용
        for archetype, weight in behavior_weights.items():
            merged_weights[archetype] = int(weight * ratio)
        
        # 프로필 가중치 적용
        for archetype, weight in profile_weights.items():
            if archetype in merged_weights:
                merged_weights[archetype] += int(weight * (1 - ratio))
            else:
                merged_weights[archetype] = int(weight * (1 - ratio))
        
        return merged_weights

    def _create_cursor(self, post: dict) -> str:
        """
        게시물 정보로부터 커서를 생성합니다.
        """
        cursor_data = {
            "score": post["score"],
            "id": post["id"]
        }
        cursor_str = json.dumps(cursor_data)
        return base64.b64encode(cursor_str.encode()).decode()

    async def _get_personalized_travel_logs(
        self, user_id: UUID, archetype_weights: Dict[str, int], limit: Optional[int], cursor: Optional[str] = None
    ) -> Tuple[List[TravelLogItemDTO], int, Optional[str]]:
        """
        개인화된 가중치를 적용하여 여행 로그를 조회합니다.
        """
        try:
            # 1. 데이터베이스 레벨에서 자기 게시물 제외 및 필요한 만큼만 조회
            url = f"{self.supabase_url}/rest/v1/travel_logs"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # 최적화: 필요한 데이터만 조회 (자기 게시물 포함, limit 적용)
            effective_limit = limit if limit is not None else 1000  # 기본 최대 1000개
            params = {
                "is_public": "eq.true",  # 공개 게시물만
                "select": "id,created_at,archetype",  # 필요한 필드만
                "order": "created_at.desc,id.desc",
                "limit": str(effective_limit + 1)  # 다음 페이지 확인을 위해 +1
            }
            
            _logger.info(f"Optimized personalized feed query params: {params}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                all_data = response.json()
                _logger.info(f"Retrieved {len(all_data)} posts from database (including self-posts)")
                
                # 자기 게시물도 포함하여 모든 공개 게시물 사용
                filtered_data = all_data
                
                # 3. 각 게시물에 점수 계산
                scored_posts = []
                for item in filtered_data:
                    # 시간 점수 계산 (최신일수록 높음)
                    created_at = item["created_at"]
                    days_ago = self._calculate_days_ago(created_at)
                    time_score = max(0, self.TIME_SCORE_BASE - days_ago * self.TIME_SCORE_DECAY)  # 하루마다 감소
                    
                    # 아키타입 가중치 적용
                    archetype = item.get("archetype", "")
                    archetype_weight = archetype_weights.get(archetype, self.WEIGHT_DEFAULT)  # 기본값
                    
                    # 최종 점수
                    final_score = time_score + archetype_weight
                    
                    # 디버깅을 위한 로그 (처음 5개만)
                    if len(scored_posts) < 5:
                        _logger.info(f"Post scoring: id={item['id'][:8]}..., archetype={archetype}, days_ago={days_ago}, time_score={time_score}, archetype_weight={archetype_weight}, final_score={final_score}")
                    
                    scored_posts.append({
                        "id": item["id"],
                        "created_at": item["created_at"],
                        "archetype": archetype,
                        "score": final_score
                    })
                
                # 3. 점수순으로 정렬
                scored_posts.sort(key=lambda x: x["score"], reverse=True)
                
                # 4. 커서 기반 페이지네이션 적용
                if cursor:
                    try:
                        import urllib.parse
                        decoded_cursor = urllib.parse.unquote(cursor)
                        cursor_bytes = base64.b64decode(decoded_cursor)
                        cursor_str = cursor_bytes.decode('utf-8')
                        cursor_data = json.loads(cursor_str)
                        
                        cursor_score = cursor_data.get("score", 0)
                        cursor_id = cursor_data.get("id")
                        
                        _logger.info(f"Cursor filter: score={cursor_score}, id={cursor_id}")
                        
                        # 커서보다 낮은 점수 또는 같은 점수에서 ID가 작은 것들 필터링
                        filtered_posts = []
                        for post in scored_posts:
                            post_score = post["score"]
                            post_id = post["id"]
                            
                            # 점수가 낮거나, 같은 점수에서 ID가 작은 경우 포함 (다음 페이지)
                            if post_score < cursor_score or (post_score == cursor_score and post_id < cursor_id):
                                filtered_posts.append(post)
                                _logger.debug(f"Including post: score={post_score}, id={post_id}")
                            else:
                                _logger.debug(f"Excluding post: score={post_score}, id={post_id}")
                        
                        _logger.info(f"Filtered posts count: {len(filtered_posts)} (from {len(scored_posts)})")
                        scored_posts = filtered_posts
                        
                    except Exception as e:
                        _logger.warning(f"Invalid cursor format: {str(e)}")
                
                # 5. limit 처리 최적화 (최대 1000개로 제한)
                max_results = min(len(scored_posts), 1000)
                if limit is None:
                    # 모든 결과 반환 (최대 1000개)
                    actual_posts = scored_posts[:max_results]
                    has_more = len(scored_posts) > 1000
                else:
                    # limit + 1개까지 가져와서 다음 커서 확인
                    effective_limit = min(limit, 1000)  # 최대 1000개로 제한
                    result_posts = scored_posts[:effective_limit + 1]
                    has_more = len(result_posts) > effective_limit
                    actual_posts = result_posts[:effective_limit]
                
                # 6. TravelLogItemDTO로 변환
                travel_logs = []
                for post in actual_posts:
                    travel_log = TravelLogItemDTO(
                        id=UUID(post["id"]),
                        created_at=post["created_at"],
                        archetype=post["archetype"]
                    )
                    travel_logs.append(travel_log)
                
                # 7. 다음 커서 생성 (최적화)
                next_cursor = None
                if has_more and actual_posts:
                    next_cursor = self._create_cursor(actual_posts[-1])
                
                # 8. 전체 개수 (필터링된 결과의 총 개수)
                total_count = len(scored_posts)
                
                return travel_logs, total_count, next_cursor
                
        except Exception as e:
            _logger.error(f"Error in get_personalized_travel_logs: {str(e)}")
            return [], 0, None

    def _calculate_days_ago(self, created_at_str: str) -> int:
        """
        생성 시간으로부터 경과된 일수를 계산합니다.
        """
        try:
            from datetime import datetime, timezone
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            delta = now - created_at
            return delta.days
        except Exception as e:
            _logger.warning(f"Error calculating days ago: {str(e)}")
            return 0


# 서비스 인스턴스 생성
feed_service = FeedService()
