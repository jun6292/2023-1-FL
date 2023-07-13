# 2023-1 형식언어 A+
### Scanner 구현 과제
Scanner 구현과제

- 4장 슬라이드에 소개된 MiniC 언어를 위한 Scanner 실습 및 구현하는 것이 목적임. (슬라이드 19~21 페이지 참고)

 1. Github의 Scanner 코드 중 C 버전과 Java 버전의 코드 실행 및 비교 분석

 2. MiniC Examples 폴더내의 MiniC 코드를 입력으로 Scanner 실습 후 결과 분석

 3. MiniC Scanner 확장 (C 버전과 Java 버전 택일 또는 다른 프로그래밍언어 가능)



- 확장 내용

 1. 추가 키워드: char, double, for, do, goto, switch, case, break, default

 2. 추가 연산자: ':'

 3. 추가 인식 리터럴

   1) character literal

   2) string literal

   3) double literal (  .123,   123. 과 같은 숏폼 인식)

 4. 문서화 주석

   1) documented(/** ~ */) comments

   2) single line documented(///) comments

 5. 추가 토큰 속성값 출력: file name, line number, column number



* 각 리터럴은 4장 슬라이드의 오토마타를 기준으로 인식할 것.

* 예제 코드 실험시, 구현한 스캐너가 인식할 수 있는 토큰 구조에 해당하지 않는 경우에는 에러 메시지 출력 후 다음 토큰 인식 시도.



* 출력 형식은 다음과 같음.

Token -----> int (token number, token value, file name, line number, column number)

Token -----> main (token number, token value, file name, line number, column number)

...

Documented Comments ------> comment contents

...



토큰 정보를 기본적으로 출력하되, 문서화 주석인 경우 그 내용을 출력 


- 요구 조건 전부 구현 (+ 정수형 8진수, 10진수, 16진수 추가 구현) <br><br>


### RE to Reduced DFA 구현과제
구현 조건

1. 입력: 정규표현

- 정규표현을 위한 알파벳은 a~z, A~Z, 0~9 총 62개로 제한

- 정규표현을 위한 연산자는  +, •, * 로 구성

- •의 경우는 축약 표현이 가능함. 예) a•b  ---> ab

- 우선 순위를 위해 () 사용이 가능함





2. 출력: 단계별로 FA(유한 오토마타) 정보가 기록된 파일

- ε-NFA

- DFA

- reduced DFA



3. 유한 오토마타 정보는 아래와 같은 포맷을 반드시 준수하기 바람.

- 유한 오토마타의 내용은 아래 5가지 항목이 순서대로 나와야 함.

- 각 항목은 아래와 같은 StateSet, TerminalSet, DeltaFunctions, StartState, FinalStateSet 의 키워드로 구분되며, 원소를 표현하기 위한 구분자는 {}를 이용

- 상태는 q로 시작하고 숫자 3자리로 구성됨

- 터미널 심볼은 a~z, A~Z, 0~9 로 제한 함

- 입실론 심볼은 ε를 사용 

- 상태전이함수는 아래 예시와 같이 (상태, 터미널) = { 출력상태1, 출력상태2 } 와 같이 구성됨

- 시작 상태와 종결 상태는 아래와 같이 임의의 상태, 상태 집합으로 정의함



예시)

StateSet = { q000, q001, q002 }

TerminalSet = { a, b, c, d }

DeltaFunctions = {

	(q000, a) = {q000, q001, ...}

	(q000, b) = {q000, q002, ...}

	(q001, a) = {q000, q005, ...}

	(q001, ε) = {q000, q001, ...}

}

StartState = q000

FinalStateSet = { q100, q220 }





4. 아래 예제를 포함하여 교재의 다양한 예시를 이용, 10개의 정규표현을 대상으로 실험 및 검증하시오.

(a+b)*abb

(b+a(aa*b)*b)*

(b+aa+ac+aaa+aac)*

(1+01)*00(0+1)*

(0+1)*011  



5. 과제 구현 코드는 별도 파일로 압축해서 제출
6. 중요 코드는 발췌해서 설명 필수
7. 사용 언어는 자유
8. 구현 소감 필수

* 힌트

정규 표현을 ε-NFA 로 변환하기 위해서는 정규 표현을 우선순위를 반영한 트리형태로 변환하고,

트리를 bottom-up(DFS)으로 분석하면서 ε-NFA를 구성하기 바람.

- Delta function 출력 형식 부분 미완
