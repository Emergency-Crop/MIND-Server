"""
Weather Service Module

/travel/weather API 전용 서비스
- 기상청 초단기실황 API 호출
- GPS 좌표 → 격자 좌표 변환
- 행정구역 역지오코딩
- 원시/파생/표시 데이터 가공
"""

import datetime
import math
import httpx
import pandas as pd
from typing import Tuple, Dict, Optional, Any
from pathlib import Path

from src.api.v1.travel.weather_dto import (
    WeatherResponseDTO, WeatherDataDTO, WeatherSourceDTO, WeatherLocationDTO,
    WeatherAdminDTO, WeatherCurrentDTO, WeatherRawDTO, WeatherDerivedDTO
)
from src.core.logger import get_logger
from src.core.env import env
from src.config.status import ERR

_logger = get_logger(__name__)

# 기상청 초단기실황 API 설정
KMA_API_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
KMA_API_KEY = env.TOUR_API_KEY  # TourAPI 키를 기상청 API에 사용
KMA_TIMEOUT = httpx.Timeout(10.0)

# 행정구역 데이터 (서버 기동 시 로드)
_admin_data: Optional[pd.DataFrame] = None


class WeatherService:
    """날씨 API 전용 서비스"""
    
    @staticmethod
    async def get_weather(
        lat: float, 
        lng: float, 
        raw: bool = False, 
        detail: str = "full"
    ) -> WeatherResponseDTO:
        """
        GPS 좌표를 기반으로 현재 날씨 정보를 조회합니다.
        
        Args:
            lat: 위도 (33.0 ~ 39.0 권장)
            lng: 경도 (124.0 ~ 132.0 권장)
            raw: 원시 데이터 포함 여부
            detail: 파생/문자열 필드 포함 범위 (lite/full)
        """
        try:
            # 1. 좌표 유효성 검사
            if not (33.0 <= lat <= 39.0) or not (124.0 <= lng <= 132.0):
                raise ERR.BAD_REQUEST.to_exception(
                    detail={"error": "INVALID_COORDINATES", "message": "좌표가 한국 범위를 벗어났습니다"}
                )
            
            # 2. GPS → 격자 좌표 변환
            nx, ny = WeatherService._convert_to_grid(lat, lng)
            
            # 3. 기준 시각 결정
            base_date, base_time = WeatherService._get_base_time()
            
            # 4. 기상청 API 호출
            kma_data = await WeatherService._call_kma_api(nx, ny, base_date, base_time)
            
            # 5. 행정구역 역지오코딩
            admin_info = WeatherService._reverse_geocode(lat, lng, nx, ny)
            
            # 6. 데이터 가공
            current_weather = WeatherService._process_weather_data(kma_data)
            raw_data = WeatherService._process_raw_data(kma_data) if raw else None
            derived_data = WeatherService._process_derived_data(current_weather)
            
            # 7. 응답 구성
            response = WeatherResponseDTO(
                success=True,
                message="현재 날씨 조회가 완료되었습니다.",
                data=WeatherDataDTO(
                    source=WeatherSourceDTO(
                        baseDate=base_date,
                        baseTime=base_time,
                        nx=nx,
                        ny=ny,
                        served_at=datetime.datetime.now().isoformat() + "+09:00",
                        note="매 정시 생성, 정시+10분부터 제공"
                    ),
                    location=WeatherLocationDTO(
                        lat=lat,
                        lng=lng,
                        area_name=admin_info["area_name"],
                        admin=WeatherAdminDTO(**admin_info["admin"])
                    ),
                    current=current_weather,
                    raw=raw_data,
                    derived=derived_data,
                    updated_at=datetime.datetime.now().isoformat() + "+09:00"
                )
            )
            
            return response
            
        except Exception as e:
            _logger.error(f"Weather API error: {str(e)}")
            if hasattr(e, 'status_code'):
                raise e
            raise ERR.INTERNAL_ERROR.to_exception(detail="날씨 정보 조회 중 오류가 발생했습니다")

    @staticmethod
    def _convert_to_grid(lat: float, lng: float) -> Tuple[int, int]:
        """WGS84 GPS 좌표를 기상청 격자 좌표로 변환 (기상청 공식 정확 구현)"""
        try:
            # 기상청 공식 상수 (C언어 예제와 동일)
            RE = 6371.00877  # 지구 반경(km)
            GRID = 5.0       # 격자 간격(km)
            SLAT1 = 30.0     # 표준위도1(degree)
            SLAT2 = 60.0     # 표준위도2(degree)
            OLON = 126.0     # 기준점 경도(degree)
            OLAT = 38.0      # 기준점 위도(degree)
            XO = 210 / GRID  # 기준점 X좌표 (210/5 = 42)
            YO = 675 / GRID  # 기준점 Y좌표 (675/5 = 135)
            
            PI = math.pi
            DEGRAD = PI / 180.0
            
            re = RE / GRID
            slat1 = SLAT1 * DEGRAD
            slat2 = SLAT2 * DEGRAD
            olon = OLON * DEGRAD
            olat = OLAT * DEGRAD
            
            # Lambert Conformal Conic 투영 공식 (C언어 예제와 동일)
            sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
            sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
            sf = math.tan(PI * 0.25 + slat1 * 0.5)
            sf = math.pow(sf, sn) * math.cos(slat1) / sn
            ro = math.tan(PI * 0.25 + olat * 0.5)
            ro = re * sf / math.pow(ro, sn)
            
            ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
            ra = re * sf / math.pow(ra, sn)
            theta = lng * DEGRAD - olon
            if theta > PI:
                theta -= 2.0 * PI
            if theta < -PI:
                theta += 2.0 * PI
            theta *= sn
            
            x = ra * math.sin(theta) + XO
            y = ro - ra * math.cos(theta) + YO
            
            nx = int(x + 1.5)
            ny = int(y + 1.5)
            
            return nx, ny
            
        except Exception as e:
            _logger.error(f"Grid conversion error: {str(e)}")
            # 오류 발생 시 서울 기본 좌표 반환
            return 60, 127

    @staticmethod
    def _get_base_time() -> Tuple[str, str]:
        """기준 시각 결정 (정시+10분 전이면 직전 정시, 이후면 해당 정시) - 한국 시간 기준"""
        # UTC+9 (한국 시간) 적용
        utc_now = datetime.datetime.utcnow()
        kst_now = utc_now + datetime.timedelta(hours=9)
        
        
        # 정시+10분 체크
        if kst_now.minute < 10:
            # 직전 정시 사용
            if kst_now.hour == 0:
                base_date = (kst_now - datetime.timedelta(days=1)).strftime("%Y%m%d")
                base_time = "2300"
            else:
                base_date = kst_now.strftime("%Y%m%d")
                base_time = f"{(kst_now.hour - 1):02d}00"
        else:
            # 해당 정시 사용
            base_date = kst_now.strftime("%Y%m%d")
            base_time = f"{kst_now.hour:02d}00"
        
        return base_date, base_time

    @staticmethod
    async def _call_kma_api(nx: int, ny: int, base_date: str, base_time: str) -> Dict:
        """기상청 초단기실황 API 호출 (명세서 준수)"""
        endpoint = f"{KMA_API_BASE_URL}/getUltraSrtNcst"
        
        # 명세서에 따른 정확한 파라미터
        params = {
            "serviceKey": KMA_API_KEY,
            "pageNo": "1",
            "numOfRows": "1000", 
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": str(nx),
            "ny": str(ny)
        }
        
        
        async with httpx.AsyncClient(timeout=KMA_TIMEOUT) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            
            try:
                data = response.json()
            except Exception as json_error:
                _logger.error(f"JSON parsing error: {json_error}")
                raise ERR.BAD_GATEWAY.to_exception(
                    detail={"error": "JSON_PARSE_ERROR", "message": "기상청 API 응답 파싱 오류"}
                )
            
            # 응답 검증 (명세서 기반)
            header = data.get("response", {}).get("header", {})
            result_code = header.get("resultCode")
            result_msg = header.get("resultMsg", "Unknown error")
            
            
            if result_code != "00":
                _logger.error(f"KMA Weather error: {result_code} - {result_msg}")
                raise ERR.BAD_GATEWAY.to_exception(
                    detail={"error": "WEATHER_API_ERROR", "message": f"기상청 API 오류: {result_msg}"}
                )
            
            # 데이터 유무 확인
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not items:
                _logger.warning("No weather data available")
                raise ERR.BAD_GATEWAY.to_exception(
                    detail={"error": "NO_DATA", "message": "날씨 데이터가 없습니다"}
                )
            
            return data

    @staticmethod
    def _reverse_geocode(lat: float, lng: float, nx: int, ny: int) -> Dict:
        """행정구역 역지오코딩 (엑셀 데이터 활용)"""
        global _admin_data
        
        # 엑셀 데이터 로드 (최초 1회)
        if _admin_data is None:
            WeatherService._load_admin_data()
        
        try:
            # 1. grid-first: 동일 격자 후보 찾기
            grid_candidates = _admin_data[
                (_admin_data['nx'] == nx) & (_admin_data['ny'] == ny)
            ]
            
            if not grid_candidates.empty:
                # 2. nearest: 가장 가까운 중심점 선택
                best_match = WeatherService._find_nearest(grid_candidates, lat, lng)
                match_source = "grid+nearest"
            else:
                # 3. fallback: 전체에서 최근접
                best_match = WeatherService._find_nearest(_admin_data, lat, lng)
                match_source = "kd-nearest"
            
            # 거리 및 신뢰도 계산
            distance_m = WeatherService._calculate_distance(
                lat, lng, best_match['lat'], best_match['lng']
            )
            confidence = max(0, min(1, 1 - (distance_m / 500)))  # 0~500m 스케일
            
            return {
                "area_name": f"{best_match['level1']} {best_match['level2']} {best_match['level3']}",
                "admin": {
                    "level1": best_match['level1'],
                    "level2": best_match['level2'],
                    "level3": best_match['level3'],
                    "code": best_match['code'],
                    "nx": best_match['nx'],
                    "ny": best_match['ny'],
                    "match_source": match_source,
                    "distance_m": round(distance_m, 1),
                    "confidence": round(confidence, 2),
                    "updated_at": best_match['updated_at']
                }
            }
            
        except Exception as e:
            _logger.error(f"Reverse geocoding error: {str(e)}")
            # 기본값 반환
            return {
                "area_name": "한국",
                "admin": {
                    "level1": "한국",
                    "level2": "",
                    "level3": "",
                    "code": "0000000000",
                    "nx": nx,
                    "ny": ny,
                    "match_source": "fallback",
                    "distance_m": None,
                    "confidence": 0.0,
                    "updated_at": None
                }
            }

    @staticmethod
    def _load_admin_data():
        """행정구역 엑셀 데이터 로드"""
        global _admin_data
        try:
            excel_path = Path("/workspace/docs/gps_code.xlsx")
            if excel_path.exists():
                _admin_data = pd.read_excel(excel_path)
                
                # 격자 좌표 nx=97, ny=74 데이터 확인
                if '격자 X' in _admin_data.columns and '격자 Y' in _admin_data.columns:
                    target_data = _admin_data[(_admin_data['격자 X'] == 97) & (_admin_data['격자 Y'] == 74)]
                
                # 컬럼명 매핑 (실제 엑셀 파일 컬럼명에 맞게)
                column_mapping = {
                    '행정구역코드': 'code',
                    '1단계': 'level1', 
                    '2단계': 'level2',
                    '3단계': 'level3',
                    '격자 X': 'nx',
                    '격자 Y': 'ny',
                    '경도(초/100)': 'lng',
                    '위도(초/100)': 'lat',
                    '위치업데이트': 'updated_at'
                }
                
                # 컬럼명 변경
                for old_name, new_name in column_mapping.items():
                    if old_name in _admin_data.columns:
                        _admin_data = _admin_data.rename(columns={old_name: new_name})
                
                # 좌표 변환 처리
                if '경도(시)' in _admin_data.columns and '경도(분)' in _admin_data.columns and '경도(초)' in _admin_data.columns:
                    # 시/분/초를 도 단위로 변환
                    _admin_data['lng'] = (_admin_data['경도(시)'] + 
                                        _admin_data['경도(분)'] / 60.0 + 
                                        _admin_data['경도(초)'] / 3600.0)
                elif '경도(초/100)' in _admin_data.columns:
                    # 초/100을 도 단위로 변환
                    _admin_data['lng'] = _admin_data['경도(초/100)'] / 100.0
                
                if '위도(시)' in _admin_data.columns and '위도(분)' in _admin_data.columns and '위도(초)' in _admin_data.columns:
                    # 시/분/초를 도 단위로 변환
                    _admin_data['lat'] = (_admin_data['위도(시)'] + 
                                        _admin_data['위도(분)'] / 60.0 + 
                                        _admin_data['위도(초)'] / 3600.0)
                elif '위도(초/100)' in _admin_data.columns:
                    # 초/100을 도 단위로 변환
                    _admin_data['lat'] = _admin_data['위도(초/100)'] / 100.0
                    
                
                # 필수 컬럼 확인
                required_columns = ['level1', 'level2', 'level3', 'code', 'nx', 'ny', 'lng', 'lat']
                missing_columns = [col for col in required_columns if col not in _admin_data.columns]
                if missing_columns:
                    _logger.warning(f"Missing required columns: {missing_columns}")
                    _admin_data = pd.DataFrame()  # 빈 데이터프레임으로 리셋
            else:
                _logger.warning("Admin data file not found, using fallback")
                _admin_data = pd.DataFrame()
        except Exception as e:
            _logger.error(f"Failed to load admin data: {str(e)}")
            _admin_data = pd.DataFrame()

    @staticmethod
    def _find_nearest(candidates: pd.DataFrame, lat: float, lng: float) -> Dict:
        """가장 가까운 후보 찾기"""
        if candidates.empty:
            raise ValueError("No candidates found")
        
        min_distance = float('inf')
        best_match = None
        
        for _, row in candidates.iterrows():
            distance = WeatherService._calculate_distance(lat, lng, row['lat'], row['lng'])
            if distance < min_distance:
                min_distance = distance
                best_match = row.to_dict()
        
        return best_match

    @staticmethod
    def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """하버사인 거리 계산 (미터)"""
        R = 6371000  # 지구 반경 (미터)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    @staticmethod
    def _process_weather_data(kma_data: Dict) -> WeatherCurrentDTO:
        """기상청 데이터를 현재 날씨 정보로 가공"""
        items = kma_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        
        # 원시 데이터 파싱
        raw_values = {}
        for item in items:
            category = item.get("category")
            obsr_value = item.get("obsrValue")
            if category and obsr_value is not None:
                # 결측값 처리 (±900 이상은 결측)
                try:
                    value = float(obsr_value)
                    if abs(value) >= 900:
                        raw_values[category] = None
                    else:
                        raw_values[category] = value
                except (ValueError, TypeError):
                    raw_values[category] = None
        
        # 각 필드 처리
        temperature = raw_values.get("T1H", 20.0) or 20.0
        humidity = int(raw_values.get("REH", 50) or 50)
        precipitation = raw_values.get("RN1", 0.0) or 0.0
        wind_speed = raw_values.get("WSD", 2.0) or 2.0
        wind_direction = int(raw_values.get("VEC", 0) or 0)
        pty_code = int(raw_values.get("PTY", 0) or 0)
        
        # 표시 텍스트 생성
        temperature_text = f"{temperature:.1f}°C"
        humidity_text = f"{humidity}%"
        precipitation_text = WeatherService._format_precipitation(precipitation)
        wind_speed_text = f"{wind_speed:.1f} m/s"
        
        # 풍향 처리
        wind_direction_16, wind_direction_text = WeatherService._format_wind_direction(wind_direction)
        wind_strength_text = WeatherService._format_wind_strength(wind_speed)
        
        # 강수형태 처리
        pty_text = WeatherService._format_precipitation_type(pty_code)
        
        # 아이콘 결정
        icon = WeatherService._get_weather_icon(pty_code)
        
        return WeatherCurrentDTO(
            temperature=temperature,
            temperature_text=temperature_text,
            humidity=humidity,
            humidity_text=humidity_text,
            precipitation_1h=precipitation,
            precipitation_text=precipitation_text,
            wind_speed=wind_speed,
            wind_speed_text=wind_speed_text,
            wind_direction_deg=wind_direction,
            wind_direction_16=wind_direction_16,
            wind_direction_text=wind_direction_text,
            wind_strength_text=wind_strength_text,
            condition_pty_code=pty_code,
            condition_pty_text=pty_text,
            condition_sky_code=None,  # 초단기실황에는 SKY 없음
            condition_sky_text=None,
            icon=icon
        )

    @staticmethod
    def _process_raw_data(kma_data: Dict) -> WeatherRawDTO:
        """원시 데이터 처리"""
        items = kma_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        
        raw_values = {}
        for item in items:
            category = item.get("category")
            obsr_value = item.get("obsrValue")
            if category and obsr_value is not None:
                # 결측값 처리
                try:
                    value = float(obsr_value)
                    if abs(value) >= 900:
                        raw_values[category] = None
                    else:
                        raw_values[category] = str(obsr_value)
                except (ValueError, TypeError):
                    raw_values[category] = None
        
        return WeatherRawDTO(**raw_values)

    @staticmethod
    def _process_derived_data(current: WeatherCurrentDTO) -> WeatherDerivedDTO:
        """파생 데이터 처리 (여행 적합성 판단 및 조언)"""
        is_travel_friendly, travel_advice = WeatherService._judge_travel_friendliness(current)
        
        return WeatherDerivedDTO(
            is_travel_friendly=is_travel_friendly,
            travel_advice=travel_advice
        )

    @staticmethod
    def _format_precipitation(precipitation: float) -> str:
        """강수량 텍스트 포맷팅 (기상청 공식 준수)"""
        if precipitation == 0 or precipitation is None:
            return "강수없음"
        elif precipitation < 1.0:
            return "1mm 미만"
        elif precipitation < 30.0:
            return f"{precipitation:.1f}mm"
        elif precipitation < 50.0:
            return "30.0~50.0mm"
        else:
            return "50.0mm 이상"

    @staticmethod
    def _format_wind_direction(degrees: int) -> Tuple[str, str]:
        """풍향 16방위 변환 (기상청 공식 준수)"""
        directions = [
            "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
        ]
        korean_directions = [
            "북풍", "북북동풍", "북동풍", "동북동풍", "동풍", "동남동풍", "남동풍", "남남동풍",
            "남풍", "남남서풍", "남서풍", "서남서풍", "서풍", "서북서풍", "북서풍", "북북서풍"
        ]
        
        # 기상청 공식: (풍향값 + 22.5 * 0.5) / 22.5 = 변환값(소수점 이하 버림)
        index = int((degrees + 22.5 * 0.5) / 22.5) % 16
        return directions[index], korean_directions[index]

    @staticmethod
    def _format_wind_strength(speed: float) -> str:
        """풍속 강도 텍스트"""
        if speed < 4:
            return "약함"
        elif speed < 9:
            return "약간 강"
        elif speed < 14:
            return "강"
        else:
            return "매우 강"

    @staticmethod
    def _format_precipitation_type(pty_code: int) -> str:
        """강수형태 텍스트 (초단기실황 코드값)"""
        pty_map = {
            0: "강수없음",
            1: "비",
            2: "비/눈", 
            3: "눈",
            5: "빗방울",
            6: "빗방울/눈날림",
            7: "눈날림"
        }
        return pty_map.get(pty_code, "정보없음")

    @staticmethod
    def _get_weather_icon(pty_code: int) -> str:
        """날씨 아이콘 결정"""
        icon_map = {
            0: "⛅",  # 강수 없음 (기본값)
            1: "🌧",  # 비
            2: "🌨🌧", # 비/눈
            3: "❄️",  # 눈
            5: "🌦",  # 빗방울
            6: "🌨🌦", # 빗방울/눈날림
            7: "🌨"   # 눈날림
        }
        return icon_map.get(pty_code, "⛅")

    @staticmethod
    def _judge_travel_friendliness(current: WeatherCurrentDTO) -> Tuple[bool, str]:
        """여행 적합성 판단 및 조언 생성"""
        now = datetime.datetime.now()
        month = now.month
        
        # (1) 강수 관련
        if current.condition_pty_code == 1:  # 비
            if current.precipitation_1h < 5:
                return False, "가벼운 비가 내립니다. 우산을 챙기세요."
            else:
                return False, "비가 많이 내립니다. 야외 활동을 자제하세요."
        elif current.condition_pty_code in [2, 3, 7]:  # 눈 관련
            return False, "눈이나 비가 섞여 내립니다. 미끄럼과 시야 확보에 주의하세요."
        elif current.condition_pty_code == 5:  # 빗방울
            return False, "빗방울이 떨어집니다. 외출 시 우산이 있으면 좋아요."
        elif current.condition_pty_code == 6:  # 빗방울/눈날림
            return False, "비와 눈이 섞여 날립니다. 미끄럼에 각별히 주의하세요."
        
        # (2) 바람(강풍)
        if current.wind_speed >= 14:
            return False, "바람이 매우 강합니다. 야외 활동과 차량 운행에 주의하세요."
        
        # (3) 온도(한파/무더위)
        if current.temperature < 0:
            return False, "기온이 영하입니다. 따뜻하게 입고 외출하세요."
        elif current.temperature >= 30:
            return False, "무더운 날씨입니다. 수분 섭취와 그늘 휴식이 필요합니다."
        elif current.temperature < 10:
            return True, "쌀쌀합니다. 겉옷을 챙기면 좋겠어요."
        elif current.temperature >= 25:
            return True, "다소 더운 편입니다. 가벼운 옷차림과 수분 보충을 권장합니다."
        
        # (4) 맑은 날/계절 기본 멘트 (PTY=0 & WSD < 9)
        if current.condition_pty_code == 0 and current.wind_speed < 9:
            if month in [3, 4, 5, 9, 10, 11]:  # 봄/가을
                return True, "날씨가 맑고 선선합니다. 야외 활동하기 좋은 날씨예요."
            elif month in [6, 7, 8]:  # 여름
                return True, "하늘이 맑습니다. 햇볕이 강할 수 있어 모자와 선크림을 챙기세요."
            elif month in [12, 1, 2]:  # 겨울
                return True, "하늘이 맑지만 공기가 차갑습니다. 따뜻하게 입으세요."
        
        # (5) 기본값
        return True, "날씨 상황을 확인하고 활동을 계획하세요."
