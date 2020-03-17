# ff4ssemble/recruiter/client.py

"""
네이버 아이디로 로그인하여 모집글 게시한다.
"""


from urllib import parse, request
import json
import requests
import webbrowser
import random

class Client:
    """ 네이버 아이디 로그인&카페 글 포스팅하는 클라이언트 """
    def __init__(self, client_id, client_secret):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_uri = 'https://nid.naver.com/login/noauth/oauthCallback.nhn'
        self.__state = State()
        self.__authorization_code = None
        self.__token = None

    def parse_and_check_json(self, json_str):
        """ json 형식인 callback 메시지를 딕셔너리로 변환 """
        if not isinstance(json_str, str):
            json_str = json_str.decode('utf-8')
        j = json.loads(json_str)    # j dict
        if 'error' in j:
            print(f"Error!: {j['error']}, {j['error_description']}")
            return j
        else:
            return j

    def grant_oauth2_code(self):
        """ 네이버 아이디 로그인 창을 새로 띄워 인증? 코드를 발급 """ # TODO 무슨 코드? 용어 확인
        url = ("https://nid.naver.com/oauth2.0/authorize?"
            f"response_type=code&client_id={self.__client_id}"
            f"&redirect_uri={self.__redirect_uri}"
            f"&state={self.__state.get_state()}")
        response = request.urlopen(request.Request(url))
        res_code = response.getcode()

        if res_code == 200 :
            response_body = response.read()
            f = open('naver_login.html', 'w', -1, 'utf-8') # TODO 파일 출력 없이 바로 도큐먼트로 새 창 여는법?
            f.write(response_body.decode('utf-8'))
            f.close()

            # 웹브라우저를 통해 네이버 아이디 로그인 성공 후 code 를 입력
            webbrowser.open_new('naver_login.html')
            print("네이버 아이디로 로그인하여 리디렉트된 callback uri에서 code 값을 입력하시오")
            return input()
        else:
            print("Error Code: " + res_code)
            return None

    def grant_oauth2_token(self):
        """ 접근 토큰을 발급 """
        url = ("https://nid.naver.com/oauth2.0/token?"
            f"client_id={self.__client_id}"
            f"&client_secret={self.__client_secret}"
            f"&grant_type=authorization_code"
            f"&state={self.__state.get_state()}"
            f"&code={self.__authorization_code}")
        response = request.urlopen(request.Request(url))
        res_code = response.getcode()

        if res_code == 200 :
            response_body = response.read()
            print(response_body.decode('utf-8')) # TODO response_body json 형식인지확인
            self.__token = Oauth2_token(self.parse_and_check_json(response_body))
        else:
            print("Error Code: " + res_code)

    # def refresh_token(self):  # TODO 토큰 갱신 메서드 추가하기

    def login_oauth2_naver(self):
        """ 네이버 아이디로 로그인 메서드 """
        self.__authorization_code = self.grant_oauth2_code()
        if self.__authorization_code == '' or self.__authorization_code == None :
            print("code 입력에 실패했습니다. 처음부터 다시 시도하세요.")
            pass
        else:
            print("code 입력 완료!")

        self.__access_token = self.grant_oauth2_token()

    def formatting_alliance_info(self, alliance_info):
        """ loads_content 메서드에서 호출, 모집글 양식에 변수 부분 포매팅,
        변수값 지정은 테스트 코드에서 post_naver_cafe 매개변수로 직접 입력 """
        for dict_key in alliance_info.keys():
            alliance_info[dict_key] = format(alliance_info[dict_key], ',')
        return alliance_info

    def loads_content(self, sample_path_prefix, alliance_info, str):
        """ 모집글 샘플 파일 읽어와서 카페 API로 전송할 양식으로 변환 """
        content = str
        try:
            f = open(sample_path_prefix
                +'Recruiting_sample.txt', 'r', encoding='utf-8')
                # 샘플 파일 인코딩이 utf-8이 아니면 atom 에디터에서 한글 깨짐...
            while True:
                line = f.readline()
                if len(line) == 0:
                    break
                content += line +"<br>" # 개행 태그 삽입
                # TODO 따옴표를 만나면 이스케이프 문자(\) 넣기, 모집글 본문에 쌍따옴표 있으면?
            f.close()
        except FileNotFoundError:
            print("<!FileNotFoundError!>: 파일명 'Recruiting_sample.txt'를 찾을 수 없습니다.")
        return parse.quote(content.format(**self.formatting_alliance_info(alliance_info)))

    def post_naver_cafe(self, sample_path_prefix,
            alliance_info, clubid, menuid, subject):
        """ 네이버 카페 API로 모집글 포스트 """
        header = "Bearer " + self.__token._Oauth2_token__access_token
        url = ("https://openapi.naver.com/v1/cafe/"
            + clubid + "/menu/" + menuid + "/articles")
        subject = parse.quote(subject)
        content = "<img src='#0' /><br><br><br><br>"    # 이미지 첨부
        data = {'subject': subject, 'content': self.loads_content(sample_path_prefix, alliance_info, content)}
        files = [
            ('image',
                ('B2V_mk3.png',
                open(sample_path_prefix+'B2V_mk3.png','rb'),
                'image/png',
                {'Express': '0'}))]
        headers = {'Authorization': header}

        response = requests.post(url, headers=headers, data=data, files=files)
        res_code = response.status_code
        if res_code == 200:
            response_body = response.text
            webbrowser.open_new(self.parse_and_check_json(response_body)["message"]["result"]["articleUrl"])
        else:
            print(response_body)
            print("Error Code: " + str(res_code))



class State:
    """ 네이버 아이디 로그인 과정에서 매번 확인해야하는 상태 클래스 """
    def __init__(self):
        self.__state = self.generate_state()

    @staticmethod
    def generate_state():
        """ 상태 코드 생성 """
        return parse.quote(str(random.random()))

    def get_state(self):
        """ 클라이언트 클래스내 메서드에서 상태 코드를 요구 """
        return self.__state

    def validate_state(self, current_state):
        """ 클라이언트 메서드에서 네이버API 서버와 통신 할 때마다 상태 검증 """
        return self.__state == current_state

class Oauth2_token:
    """ 네이버 아이디 로그인 결과 취득하는 접근 토큰 클래스 """
    def __init__(self, j: dict):
        self.__access_token = j['access_token']
        self.__refresh_token = j['refresh_token']
        self.__token_type = j['token_type']
        self.__expires_in = j['expires_in']

if __name__ == "__main__":
    print("==== /recruiter/request_naver_login.py 테스트 ====")
    print("ff4ssemble/recruiter/client.py 테스트 완료!")
    pass
