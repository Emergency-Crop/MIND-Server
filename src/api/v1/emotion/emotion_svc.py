"""
감정 태그 추출 서비스 모듈
"""
import json
import httpx
from typing import List, Dict, Any
from src.api.v1.emotion.emotion_dto import (
    EmotionTagRequestDTO, EmotionSentenceDTO, EmotionSentenceResultDTO, EmotionAnalysisResponseDTO
)
from src.core.logger import get_logger
from src.core.env import env

_logger = get_logger(__name__)

class EmotionTagService:
    """감정 태그 추출 서비스"""
    
    def __init__(self):
        self.openai_api_key = env.OPENAI_API_KEY
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # 감정 태그 목록
        self.emotion_tags = [
            "설렘", "고요함", "그리움", "행복", "쓸쓸함", "위로", "따뜻함", "벅참", "해방감", "집중",
            "햇살", "노을", "파도소리", "안개", "쨍한날", "밤하늘", "달빛", "비오는날", "청명함", "은은함",
            "해변", "산책로", "한옥마을", "골목길", "전통시장", "전망대", "공원", "숲속", "섬", "호수",
            "봄꽃", "여름밤", "가을단풍", "겨울바다", "새벽산책", "이른아침", "한낮", "해질녘", "밤산책", "첫눈",
            "혼자여행", "커플여행", "가족여행", "아이들과함께", "부모님과함께", "친구들과", "단체여행",
            "힐링여행", "맛집투어", "사진여행", "도보여행", "자연치유", "성지순례", "체험여행", "역사탐방", "쉼여행",
            "산책", "카페탐방", "맛집탐방", "수영", "등산", "시장구경", "자전거", "일몰감상", "명상", "책읽기",
            "필름감성", "따뜻한톤", "차분한톤", "레트로", "몽환적", "빈티지풍", "미니멀", "컬러풀", "로컬감성", "네이처무드",
            "1일1기록", "사진중심", "텍스트중심", "스냅기록", "타임라인형", "앨범형",
            "첫여행", "재방문", "기념일여행", "즉흥여행", "휴식필요", "기획여행"
        ]
        
        # 아키타입 테이블
        self.ARCHETYPE_TABLE = {
            "고요한 회복러": [
                "고요함", "위로", "따뜻함", "숲속", "혼자여행", "쉼여행", "힐링여행", "명상",
                "자연속에서", "차분한톤", "청명함", "이른아침", "비오는날", "무계획", "첫눈", "치유"
            ],
            "감성 수집가": [
                "설렘", "그리움", "행복", "노을", "햇살", "골목길", "카페탐방", "필름감성",
                "레트로", "로컬감성", "사진중심", "텍스트중심", "잔잔함", "혼자여행", "감성기록", "1일1기록"
            ],
            "탐험형 활동러": [
                "신남", "트레킹", "즉흥여행", "시장구경", "산책", "전망대", "도보여행",
                "한옥마을", "성지순례", "여름밤", "계획없음", "핵심스팟", "새로운장소", "에너지"
            ],
            "가족 중심 케어러": [
                "가족여행", "아이들과함께", "부모님과함께", "공원", "편안한코스", "전통시장",
                "사진여행", "계획여행", "쉼여행", "느긋함", "맛집탐방", "테마파크", "기획여행"
            ],
            "풍경 마스터": [
                "자연치유", "전망대", "청명함", "노을", "파도소리", "달빛", "해변", "겨울바다",
                "가을단풍", "봄꽃", "하늘", "풍경중심", "사진중심", "따뜻한톤", "첫눈", "비오는날"
            ],
            "소셜 공감러": [
                "공유일기", "좋아요많음", "댓글많음", "친구들과", "커플여행", "가족여행",
                "감성공유", "여행공감", "포토기록", "소통", "같이걷기", "여행일기", "1일1기록"
            ],
            "목적 집중형": [
                "사진여행", "맛집투어", "성지순례", "테마파크", "기획여행", "계획여행",
                "맛집중심", "핵심스팟", "전통시장", "산책루트", "문화유산", "자전거", "핫플투어"
            ],
            "느린여행자": [
                "쉼여행", "무계획", "자연속에서", "산책", "혼자여행", "이른아침",
                "한낮의산책", "느긋함", "비오는날", "조용한장소", "따뜻한톤", "고요함", "차분한톤"
            ]
        }
    
    async def analyze_emotion_sentences(self, request_dto: EmotionTagRequestDTO) -> EmotionAnalysisResponseDTO:
        """여러 문장의 감정 분석 및 아키타입 추출"""
        try:
            sentence_results = []
            all_tags = []
            
            # 각 문장별로 태그 추출
            for sentence in request_dto.sentences:
                tags = await self._extract_tags_for_sentence(sentence.feel)
                sentence_results.append(EmotionSentenceResultDTO(
                    index=sentence.index,
                    feel=sentence.feel,
                    tags=tags
                ))
                all_tags.extend(tags)
            
            # 전체 아키타입 추출
            overall_archetype = self._determine_archetype(all_tags)
            
            return EmotionAnalysisResponseDTO(
                sentences=sentence_results,
                overall_archetype=overall_archetype
            )
            
        except Exception as e:
            _logger.error(f"감정 분석 중 오류 발생: {str(e)}")
            # 기본 응답 반환
            return EmotionAnalysisResponseDTO(
                sentences=[],
                overall_archetype="고요한 회복러"
            )
    
    async def _extract_tags_for_sentence(self, text: str) -> List[str]:
        """단일 문장에서 태그 추출"""
        try:
            response = await self._call_openai_api(text)
            tags = self._parse_openai_response(response)
            
            # 유효한 태그만 필터링
            valid_tags = [tag for tag in tags if tag in self.emotion_tags]
            
            # 유효한 태그가 없으면 빈 배열 반환
            if not valid_tags:
                _logger.warning(f"유효한 태그가 없음. 원본 태그: {tags}")
                return []
            
            return valid_tags
        except Exception as e:
            _logger.warning(f"문장 태그 추출 실패: {str(e)}")
            return []
    
    def _determine_archetype(self, all_tags: List[str]) -> str:
        """전체 태그를 기반으로 아키타입 결정"""
        archetype_scores = {}
        
        # 각 아키타입별 점수 계산
        for archetype, archetype_tags in self.ARCHETYPE_TABLE.items():
            score = 0
            for tag in all_tags:
                if tag in archetype_tags:
                    score += 1
            archetype_scores[archetype] = score
        
        # 가장 높은 점수의 아키타입 반환
        if archetype_scores:
            best_archetype = max(archetype_scores, key=archetype_scores.get)
            if archetype_scores[best_archetype] > 0:
                return best_archetype
        
        # 기본값 반환
        return "고요한 회복러"
    
    async def _call_openai_api(self, text: str) -> str:
        """OpenAI API 호출"""
        prompt = f"""
당신은 여행 감정 분석 전문가입니다. 주어진 문장을 분석하여 가장 정확한 태그를 추출해주세요.

**분석할 문장:**
"{text}"

**사용 가능한 태그 목록:**
{', '.join(self.emotion_tags)}

**분석 지침:**
1. 문장에서 직접적으로 느껴지는 감정과 분위기를 파악하세요
2. 여행 상황(장소, 활동, 시간대, 동반자 등)을 고려하세요
3. 문장의 톤과 어조를 분석하세요
4. 가장 핵심적인 요소들만 선택하세요 (개수보다 정확성이 중요)

**태그 선택 기준:**
- 감정: 설렘, 고요함, 그리움, 행복, 쓸쓸함, 위로, 따뜻함, 벅참, 해방감 등
- 분위기: 햇살, 노을, 파도소리, 안개, 쨍한날, 밤하늘, 달빛, 비오는날 등
- 장소: 해변, 산책로, 한옥마을, 골목길, 전통시장, 전망대, 공원, 숲속 등
- 활동: 산책, 카페탐방, 맛집탐방, 수영, 등산, 시장구경, 자전거 등
- 동반자: 혼자여행, 커플여행, 가족여행, 친구들과 등
- 여행 스타일: 힐링여행, 맛집투어, 사진여행, 즉흥여행, 기획여행 등

**응답 형식:**
{{
  "tags": ["가장_적절한_태그1", "적절한_태그2", "적절한_태그3"]
}}

정확하고 의미있는 태그만 선택해주세요. 개수는 2-5개 사이로 선택하되, 정확성이 최우선입니다. 최소 2개의 태그를 선택해주세요.
"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.openai_url,
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "당신은 여행 감정 분석 전문가입니다. 문장의 뉘앙스, 감정, 상황을 정확히 파악하여 가장 적합한 태그를 추출하는 것이 당신의 역할입니다. 개수보다는 정확성과 의미를 우선시하세요."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API 오류: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _parse_openai_response(self, response: str) -> List[str]:
        """OpenAI 응답 파싱"""
        try:
            # JSON 추출
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("JSON 형식을 찾을 수 없습니다")
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            tags = data.get("tags", [])
            return tags
            
        except Exception as e:
            _logger.warning(f"OpenAI 응답 파싱 실패: {str(e)}")
            return []
    


# 서비스 인스턴스
emotion_service = EmotionTagService()
