<h1>EMSW(Echo Mind Sub Writer)</h1>

<h2>프로잭트 개요</h2>

이 프로젝트는 문서 작업을 지원하기 위하여 Local AI를 다루는 방법을 체계적으로 보완한 프로젝트로서, 다음과 같은 역할을 한다.

<h3>창작자 또는 기획자 등의 저작권자</h3>

IP를 가지고 개발하는 저작자들에게는 가장 중요한 것이 바로 이 저작물을 AI가 외부에서 학습하느냐 하지 않느냐에 대한 중요한 문제일 것이다. 이것이 중요한 문제인 이유는 다음과 같다.

1. 저작권자로서 자신의 IP가 도둑맞을 수 있다는 약간의 공포심.
2. 실제 계약자간의 법적 논쟁의 필요성.
3. 자신의 자식과도 같은 IP가 도둑맞을지도 모른다는 점에 대한 문제.

또한, 일부 신체상의 이유로 불편함을 겪는 사람들의 '문제'를 해결하기 위한 방법을 지원하기 위한 역할을 만들었다.
첫번째로 기억력에 문제가 있어 자주 기억력이 끊기는 형태의 문제를 가진 사람.
두번째로 기타의 문제로 작업 변경이 능동적이지 않는 경우.
세번째로 자신이 계획을 세우고, 세운 계획을 주기적으로 Responsive를 통해 일정 관리와 일상 관리를 같이 하고 싶은 경우.

<hr>

상세 기획은 [기획서](./ProjectProposal.md) 참고하시오.

<hr>
<hr>

<h2> How To Use </h2>

전제 조건 : Ollama를 인스톨해야 합니다.
수정 필요 : 테스트 컴퓨터에서는 gpt-oss:20b로 실행하였으며, 필요시 EMSW_MainUI.py의 ChatController 클래스에서 generate의 끝에 model_name="바꿀 model name"을 추가해주면 됩니다.
<br>
<br>
```
git clone https://github.com/sHiARin/EMSW.git
cd ./EMSW
pip install -r requirements.txt
```
<br>
<br>
<br>

```
./EMSW/Scripts/activate
python ./main.py
```
<br>
<br>
requirements.txt로 필요한 패키지를 설치해아 합니다.<br>
hwp-helper와 pyside6, langchain과 ollama를 사용했습니다.<br>
ollama 로컬 LLM 서버는 별도로 설치해주시기 바랍니다.<br>
<br>
<br>
<hr>
이후 사용법은 여기를 참고해 주세요.<br>
<hr>
[AI 설정법](./HowToUsePrograme/HowToUse_AIEditting.md)
<br>
<br>
[문서 편집 방법](./HowToUsePrograme/HowToEditingDocument.md)
<hr>
<br>
<br>
<br>
<br>
<br>
<br>
개발 과정 내용을 보려면 TODO(./todo)를 참고하세요<br>
<br>
<br>
+++ 기존의 기획서와는 이후 개발 중 예기치 못한 오류가 발생하여 사실상 대부분의 개발은 하지 못한 상황.<br>
+++ ... 예측 실패! 와아아... (웃음)<br>
+++ 기말고사 끝난 뒤에 계속 업데이트 해야 겠습니다.<br>
