#!/usr/bin/env python3
"""
기상청 API 테스트 스크립트
"""
import asyncio
import httpx
from datetime import datetime

async def test_weather_api():
    """기상청 API 직접 테스트"""
    
    # API 설정
    WEATHER_API_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
    WEATHER_API_KEY = "mXJbdNHuEcndfpnsLEjkEbPEDHuVvWMT//cPkivmhiH691na921i4JZ+8kTIKzJcPyvqHKfJlP86zeNi8RmOkQ=="
    
    # 테스트 좌표 (서울)
    nx, ny = 59, 1391
    
    # 현재 시간 기준으로 base_date, base_time 설정
    now = datetime.now()
    print(f"현재 시간: {now}")
    
    # 새벽 시간대(0-6시)에는 전날 23시 데이터 사용
    if now.hour < 6:
        base_date = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")
        base_time = "2300"
    else:
        base_date = now.strftime("%Y%m%d")
        if now.minute < 30:
            hour = (now.hour - 1) % 24
        else:
            hour = now.hour
        base_time = f"{hour:02d}00"
    
    print(f"API 호출 파라미터: base_date={base_date}, base_time={base_time}")
    
    # API 호출
    endpoint = f"{WEATHER_API_BASE_URL}/getUltraSrtNcst"
    params = {
        "serviceKey": WEATHER_API_KEY,
        "pageNo": "1",
        "numOfRows": "1000",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": str(nx),
        "ny": str(ny)
    }
    
    print(f"API URL: {endpoint}")
    print(f"파라미터: {params}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(endpoint, params=params)
            print(f"HTTP 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"API 응답: {data}")
                
                # 결과 코드 확인
                header = data.get("response", {}).get("header", {})
                result_code = header.get("resultCode")
                result_msg = header.get("resultMsg")
                
                print(f"결과 코드: {result_code}")
                print(f"결과 메시지: {result_msg}")
                
                if result_code == "00":
                    print("✅ API 호출 성공!")
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    print(f"데이터 항목 수: {len(items)}")
                    
                    # 날씨 데이터 출력
                    for item in items[:5]:  # 처음 5개만 출력
                        print(f"  {item.get('category')}: {item.get('obsrValue')}")
                else:
                    print(f"❌ API 오류: {result_msg}")
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                print(f"응답 내용: {response.text}")
                
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_weather_api())

