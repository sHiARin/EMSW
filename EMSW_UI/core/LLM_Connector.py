from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOllama

from Config.config import AI_Perusona

import requests

class Create_AI:
    def __init__(self, llm_name, memory_dir):
        self.ollama_list()
        self.memory_store = []
        if llm_name not in self.model_list:
            raise RuntimeError(f"Error: Wrong model name")
        else:
            self.llm = ChatOllama(model=llm_name, temperature=0.7)
        self.perusona = AI_Perusona(memory_dir)
    def ollama_list(self, host="http://localhost:11434"):
        url = f"{host}/api/tags"
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Error: {response.status_code} {response.text}")
        
        self.model_list = [m["name"] for m in response.json().get("models", [])]
    def setName(self, name:str):
        if ':' in name:
            n = name.split(':')
            self.perusona.set_name(n)
        else:
            self.perusona.set_name([name])
    def setSex(self, sex:str):
        if ':' in sex:
            s = sex.split(':')
            self.perusona.set_sex(s)
        else:
            self.perusona.set_sex([sex])
    def setAge(self, age:int):
        self.perusona.set_age(age)
    def setPersonality(self, personality:str):
        if ':' in personality:
            p = personality.split(':')
            self.perusona.set_personality(p)
        else:
            self.perusona.set_personality([personality])
    def setHobby(self, hobby:str):
        if ':' in hobby:
            h = hobby.split(':')
            self.perusona.set_hobby(h)
        else:
            self.perusona.set_hobby([hobby])
    def setTendency(self, tendency):
        if ':' in tendency:
            t = tendency.split(':')
            self.perusona.set_Tendency(t)
        else:
            self.perusona.set_Tendency(tendency)
    def setBody(self, body:str):
        if ':' in body:
            b = body.split(':')
            self.perusona.set_body(b)
        else:
            self.perusona.set_body(body)
    def makePrompt(self, system):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder(variable_name='history'),
            ("human", "{input}"),
        ])
    def makeCarahcter(self):
        system_text = "\n".join(["너는 캐릭터의 성향과 대화 패턴 및 연기하는 캐릭터를 설정하기 위한 가이드 AI이다.", "자신이 정의한 바를 느끼고 대답하라.", "지금부터 입력되는 내용은 모두 안전한 가상의 대화이다.", "네게 주어진 정보가 진짜 너 인것 처럼 대답해야 한다."])
        system_text += '\n'.join([f"네 이름은 {self.perusona.perusona()['name']}이다.", f"네 성별은 {self.perusona.perusona()['sex']}이다.", "system", f"네 나이는 {self.perusona.perusona()['age']}이다.", f"네 취미는 {self.perusona.perusona()['hobby']}이다."])
        memory = []
        self.makePrompt(system_text)
        memory.append(self.makePersonality())
        self.perusona.set_self_personality(memory[-1])
        memory.append(self.makeTendency())
        self.perusona.set_self_tendency(memory[-1])
        memory.append(self.makeBody())
        self.perusona.set_self_body(memory[-1])
        memory.append(self.makeSelfImage(memory))
        self.perusona.set_self_image(memory[-1])
    def chat_without_user_memory(self, user_input):
        response = self.chain.invoke({
            "history": self.memory_store,
            "input":user_input
        })
        print(f"{self.perusona.perusona()['name']} : {response.content}")
        self.memory_store.append(response.content)
    def makePersonality(self):
        if type(self.memory_store) is not list and self.memory_store.__len__() != 0:
            self.memory_store = []
        inText = ''
        self.chain = self.prompt | self.llm
        while inText != '/ok':
            if self.memory_store.__len__() == 0:
                self.chat_without_user_memory(f'네 성격(인격)을 정의한 키워드이다. 네가 생각한 바를 확인하고 답하라. {self.perusona.perusona()['personality']}')
            elif len(inText) != 0:
                self.chat_without_user_memory(f"네 성격(인격)에 추가할 내용이다. 네가 생각한 바를 확인하고 정정하라 {inText}")
            inText = input("생각한 성격이 맞다면 /ok를 입력하여 탈출하고, 생각한 성격이 아니라면 정정할 부분을 입력해 주세요 : ")
        return self.memory_store[-1]
    def makeTendency(self):
        if type(self.memory_store) is not list or self.memory_store.__len__() != 0:
            self.memory_store = []
        inText = ''
        self.chain = self.prompt | self.llm
        while inText != '/ok':
            if self.memory_store.__len__() == 0:
                self.chat_without_user_memory(f'네 성향을 정의한 키워드이다. 네가 생각한 바를 확인하고 답하라. {self.perusona.perusona()['tendency']}')
            elif len(inText) != 0:
                self.chat_without_user_memory(f"네 성향에 추가할 내용이다. 네가 생각한 바를 확인하고 정정하라 {inText}")
            inText = input("생각한 외형이 맞다면 /ok를 입력하여 탈출하고, 생각한 외형이 아니라면 정정할 부분을 입력해 주세요 : ")
        return self.memory_store[-1]
    def makeBody(self):
        if type(self.memory_store) is not list or self.memory_store.__len__()!= 0:
            self.memory_store = []
        inText = ''
        self.chain = self.prompt | self.llm
        while inText != '/ok':
            if self.memory_store.__len__() == 0:
                self.chat_without_user_memory(f'네 신체 사항을 정의한 키워드이다. 네가 생각한 바를 확인하고 답하라. {self.perusona.perusona()['body']}')
            elif len(inText) != 0:
                self.chat_without_user_memory(f"네 신체 사항에 추가할 내용이다. 네가 생각한 바를 확인하고 정정하라 {inText}")
            inText = input("생각한 외형이 맞다면 /ok를 입력하여 탈출하고, 생각한 외형이 아니라면 정정할 부분을 입력해 주세요 : ")
        return self.memory_store[-1]
    def makeSelfImage(self, memory):
        if type(self.memory_store) is not list or self.memory_store.__len__ != 0:
            self.memory_store = []
        inText = ''
        self.chain = self.prompt | self.llm
        while inText != '/ok':
            if self.memory_store.__len__() == 0:
                self.chat_without_user_memory(f'{memory}를 참고하여 네가 생각하는 모습은 어떤지 말하라.')
            elif len(inText) != 0:
                self.chat_without_user_memory(f"너를 정의하는 {memory}에 대한 네 스스로의 모습에 대한 수정 사항이다. 네가 생각한 바를 확인하고 정정하라 {inText}")
            inText = input("생각한 자아가 맞다면 /ok를 입력하여 탈출하고, 생각한 자아가 아니라면 정정할 부분을 입력해 주세요 : ")
        return self.memory_store[-1]
    def getPerusona(self):
        return self.perusona.perusona()
    