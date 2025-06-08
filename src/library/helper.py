"""
상태 코드와 설명을 기반으로 FastAPI 문서 응답을 자동 생성하는 유틸리티
"""
from typing import Union
from src.config.status import ERR, SUC

class Status:
    @staticmethod
    def docs(*modes: list[Union[ERR, SUC]]):
        """
        FastAPI 라우터에서 responses 파라미터 자동 생성

        예시:
        @app.get("/users", responses=Status.docs(ERR.NOT_FOUND, SUC.OK))
        """
        rv = {}
        for mode in modes:
            rv[mode.code] = {"description": mode.desc}
        return dict(sorted(rv.items()))