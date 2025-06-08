"""
API 응답에 사용할 에러 코드와 성공 코드를 Enum 기반으로 정의한 모듈

- ERR: ErrorMode를 상속한 에러 상태 집합 (HTTP status code + 설명 포함)
- SUC: SuccessMode를 상속한 성공 상태 집합 (HTTP status code + 설명 포함)

사용 예:
    raise ERR.USER_NOT_FOUND.to_exception()
    return SUC.OK.to_response(data)
"""
from src.library.exception import ErrorMode, SuccessMode

class ERR(ErrorMode):
    """
    API 예외 응답용 에러 코드 정의
    - 상태 코드 + 메시지 쌍을 Enum처럼 선언
    - to_exception(detail) 메서드로 FastAPI 예외로 변환 가능
    """
    BAD_REQUEST = (400, "요청 형식이 잘못되었습니다.")
    UNAUTHORIZED = (401, "인증이 필요합니다.")
    FORBIDDEN = (403, "해당 요청에 대한 권한이 없습니다.")
    NOT_FOUND = (404, "요청한 리소스를 찾을 수 없습니다.")
    METHOD_NOT_ALLOWED = (405, "허용되지 않은 메서드입니다.")
    DUPLICATE_RECORD = (409, '입력 키 값이 중복되어 오류 발생되었습니다.')
    GONE = (410, "해당 리소스는 더 이상 유효하지 않습니다.")
    UNPROCESSABLE_ENTITY = (422, "입력값 유효성 검증에 실패했습니다.")
    TOO_MANY_REQUESTS = (429, "요청 횟수가 너무 많습니다. 잠시 후 다시 시도하세요.")
    INTERNAL_SERVER_ERROR = (500, "서버 내부 오류가 발생했습니다.")
    SERVICE_UNAVAILABLE = (503, "현재 서비스를 이용할 수 없습니다. 잠시 후 다시 시도하세요.")

class SUC(SuccessMode):
    """
    API 성공 응답 코드 정의
    - 상태 코드 + 메시지 쌍을 Enum처럼 선언
    - to_response(data) 메서드로 공통 응답 객체 반환
    """
    OK = (200, "요청이 성공적으로 처리되었습니다.")
    CREATED = (201, "요청 리소스가 성공적으로 생성되었습니다.")
    ACCEPTED = (202, "요청이 수락되었으며, 처리는 비동기로 진행됩니다.")
    NO_CONTENT = (204, "요청이 성공적으로 처리되었으나 응답 본문은 없습니다.")
    PARTIAL_CONTENT = (206, "요청이 부분적으로 처리되었습니다.")
    ALREADY_REPORTED = (208, "해당 리소스는 이미 처리되었습니다.")