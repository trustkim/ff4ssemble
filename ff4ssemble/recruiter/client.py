# ff4ssemble/recruiter/client.py

from urllib import parse, request
import json
import requests
import webbrowser
import random

class Client:
    def __init__(self, client_id, client_secret):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_uri = 'https://nid.naver.com/login/noauth/oauthCallback.nhn'
        self.__state = State()
        self.__authorization_code = None
        self.__token = None

    def parse_and_check_json(self, json_str):
        if not isinstance(json_str, str):
            json_str = json_str.decode('utf-8')
        j = json.loads(json_str)    # j dict
        if 'error' in j:
            print(f"Error!: {j['error']}, {j['error_description']}")
            return j
        else:
            return j

    def grant_oauth2_code(self):
        url = f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={self.__client_id}&redirect_uri={self.__redirect_uri}&state={self.__state.get_state()}"
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
        url = f"https://nid.naver.com/oauth2.0/token?client_id={self.__client_id}&client_secret={self.__client_secret}&grant_type=authorization_code&state={self.__state.get_state()}&code={self.__authorization_code}"
        response = request.urlopen(request.Request(url))
        res_code = response.getcode()

        if res_code == 200 :
            response_body = response.read()
            print(response_body.decode('utf-8')) # TODO response_body json 형식인지확인
            self.__token = Oauth2_token(self.parse_and_check_json(response_body))
        else:
            print("Error Code: " + res_code)

    def login_oauth2_naver(self):
        self.__authorization_code = self.grant_oauth2_code()
        if self.__authorization_code == '' or self.__authorization_code == None :
            print("code 입력에 실패했습니다. 처음부터 다시 시도하세요.")
            pass
        else:
            print("code 입력 완료!")

        self.__access_token = self.grant_oauth2_token()

    def formatting_alliance_info(self, alliance_info):
        for dict_key in alliance_info.keys():
            alliance_info[dict_key] = format(alliance_info[dict_key], ',')
        return alliance_info

    def loads_content(self, sample_path_prefix, alliance_info, str):
        content = str
        try:
            f = open(sample_path_prefix+'Recruiting_sample.txt', 'r', encoding='utf-8')
            while True:
                line = f.readline()
                if len(line) == 0:
                    break
                content += line +"<br>"
            f.close()
        except FileNotFoundError:
            print("<!FileNotFoundError!>: 파일명 'Recruiting_sample.txt'를 찾을 수 없습니다.")
        return parse.quote(content.format(**self.formatting_alliance_info(alliance_info)))

    def post_naver_cafe(self, sample_path_prefix, alliance_info, clubid, menuid, subject):
        header = "Bearer " + self.__token._Oauth2_token__access_token
        url = "https://openapi.naver.com/v1/cafe/" + clubid + "/menu/" + menuid + "/articles"
        subject = parse.quote(subject)
        content = "<img src='#0' /><br><br><br><br>"    # 이미지 첨부
        data = {'subject': subject, 'content': self.loads_content(sample_path_prefix, alliance_info, content)}
        files = [
            ('image', ('B2V_mk3.png', open(sample_path_prefix+'B2V_mk3.png','rb'), 'image/png', {'Express': '0'}))
        ]
        headers = {'Authorization': header}

        response = requests.post(url, headers=headers, data=data, files=files)
        res_code = response.status_code
        if res_code == 200:
            response_body = response.text
            print(response_body) # TODO response_body json 형식인지확인
            webbrowser.open_new(self.parse_and_check_json(response_body)["message"]["result"]["articleUrl"])
        else:
            print("Error Code: " + str(res_code))



class State:
    def __init__(self):
        self.__state = self.generate_state()

    @staticmethod
    def generate_state():
        return parse.quote(str(random.random()))

    def get_state(self):
        return self.__state

    def validate_state(self, current_state):
        return self.__state == current_state

class Oauth2_token:
    def __init__(self, j: dict):
        self.__access_token = j['access_token']
        self.__refresh_token = j['refresh_token']
        self.__token_type = j['token_type']
        self.__expires_in = j['expires_in']

if __name__ == "__main__":
    print("==== /recruiter/request_naver_login.py 테스트 ====")
    print("ff4ssemble/recruiter/client.py 테스트 완료!")
    pass
