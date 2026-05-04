import requests, time, hashlib, base64, json, os, zipfile, getpass, shutil

debugMode:bool = True

def MakeSign(content:str, pid:str = "grlx", timestamp:int = int(time.time())) -> str:
    md5 = hashlib.md5()
    encodeSign:bytes = (pid + str(timestamp) + content + "555ffbe95ccf4e9535a110170b445ab8").encode("utf-8")
    md5.update(encodeSign)
    return md5.hexdigest()

def Login(phone:str, password:str, device_code:str = "DA6FDF42C0849761|0C072A134F008B9F", device_name:str = "LEITIANSHUO", system:str = "4", sign_response:int = 1, version:str = "3", global_client_version:str = "", sn:str = "test") -> str:
    body:list = [
        {
            "r":"user/login",
            "params":{
                "sn":sn,
                "phone":phone,
                "password":password,
                "device_code":device_code,
                "device_name":device_name,
                "version":version,
                "local_ip":"192.168.1.3",
                "system":system,
                "global_client_version":global_client_version,
                "sign_response":sign_response,
            }
        }
    ]
    bodyjson:str = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
    bodyb64:str = base64.b64encode(bodyjson.encode("utf-8")).decode("utf-8")
    timestamp = time.time()
    head:dict = {
        "version":"1.0",
        "sign":MakeSign(content = bodyb64, timestamp = int(timestamp)),
        "pid":"grlx", 
        "time":int(timestamp),
    }
    payload:dict = {
        "body":bodyb64,
        "head":head
    }
    headers:dict = {
        "Host": "api.ets100.com",
        "User-Agent": "libcurl-agent/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept":"*/*"
    }
    payload:str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    response = requests.post(url = "https://api.ets100.com/user/login", data = payload, headers = headers)
    return response.text

def GetPAI(token:str, system:str = "4", sign_response:int = 1, version:str = "2", global_client_version:str = "", sn:str = "test") -> str:
    body:list = [
        {
            "r":"m/ecard/list",
            "params":{
                "sn":sn,
                "token":token,
                "version":version,
                "system":system,
                "global_client_version":global_client_version,
                "sign_response":sign_response,
            }
        }
    ]
    bodyjson:str = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
    bodyb64:str = base64.b64encode(bodyjson.encode("utf-8")).decode("utf-8")
    timestamp = time.time()
    head:dict = {
        "version":"1.0",
        "sign":MakeSign(content = bodyb64, timestamp = int(timestamp)),
        "pid":"grlx", 
        "time":int(timestamp),
    }
    payload:dict = {
        "body":bodyb64,
        "head":head
    }
    headers:dict = {
        "Host": "api.ets100.com",
        "User-Agent": "libcurl-agent/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept":"*/*"
    }
    payload:str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    response = requests.post(url = "https://api.ets100.com/m/ecard/list", data = payload, headers = headers)
    return response.text

def GetHomeworkList(parent_account_id:str, token:str, limit:str = "10", system:str = "4", sign_response:int = 1, version:str = "2", global_client_version:str = "5.4.5", sn:str = "test") -> str:
    body:list = [
        {
            "r":"g/homework/list",
            "params":{
                "sn":sn,
                "token":token,
                "parent_account_id":parent_account_id,
                "limit":limit,
                "status":"1",
                "offset":"0",
                "max_end_time":"",
                "max_homework_id":"",
                "min_end_time":"",
                "min_homework_id":"",
                "get_to_do_count":"1",
                "show_old_homework":"1",
                "parent_homework_id":"",
                "get_all_count":1,
                "check_pass":1,
                "get_to_overtime_count":1,
                "version":version,
                "system":system,
                "global_client_version":global_client_version,
                "sign_response":sign_response
            }
        }
    ]
    bodyjson:str = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
    bodyb64:str = base64.b64encode(bodyjson.encode("utf-8")).decode("utf-8")
    timestamp = time.time()
    head:dict = {
        "version":"1.0",
        "sign":MakeSign(content = bodyb64, timestamp = int(timestamp)),
        "pid":"grlx", 
        "time":int(timestamp),
    }
    payload:dict = {
        "body":bodyb64,
        "head":head
    }
    headers:dict = {
        "Host": "api.ets100.com",
        "User-Agent": "libcurl-agent/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept":"*/*"
    }
    payload:str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    response = requests.post(url = "https://api.ets100.com/g/homework/list", data = payload, headers = headers)
    # print(response.text)
    return response.text

def GetHomeworkURL(PAI:str, token:str) -> list:
    homeworkLists = json.loads(GetHomeworkList(parent_account_id = PAI, token = token))[0]["body"]
    baseURL:str = homeworkLists["base_url"]
    datas = homeworkLists["data"]
    homework:list = []
    for data in datas:
        # {"name": "aaa", "contents": {"aaa": [url1, url2, url3], "bbb": [url1, url2, url3]}}
        zipInfo = data["struct"]["contents"]
        item:list = []   
        for info in zipInfo:
            group_name:str = info["group_name"]
            url:str = info["url"]
            item.append((group_name, baseURL + url))
        result_dict:dict = {}
        for key, value in item:
            if key in result_dict:
                result_dict[key].append(value)
            else:
                result_dict[key] = [value]
        homeworkList = {"name": data["name"], "contents": result_dict}
        homework.append(homeworkList)
    return homework

def calculate_md5(data):
    """计算二进制数据的MD5哈希值"""
    md5 = hashlib.md5()
    md5.update(data)
    return md5.digest()

def bytes_to_hex_string(data):
    """将二进制数据转换为大写十六进制字符串"""
    return data.hex().upper()

def generate_zip_password(tail_data):
    """生成压缩包密码"""
    FOOTER_SIZE = 336
    if len(tail_data) < FOOTER_SIZE:
        raise ValueError("Tail data too small")

    # 提取尾部336字节
    footer = tail_data[-FOOTER_SIZE:]

    # 验证签名 (MSTCHINA 或 EPLAT)
    valid_signature = (
        footer[:8] == b'MSTCHINA' or 
        footer[144:149] == b'EPLAT'
    )
    
    if not valid_signature:
        raise ValueError("Invalid file signature")

    # 提取128字节种子数据 (偏移16-143)
    seed = footer[16:144]

    # 第一重MD5: 计算种子数据的MD5
    first_md5 = calculate_md5(seed)
    first_hex = bytes_to_hex_string(first_md5)

    # 第二重MD5: 计算第一重结果的十六进制字符串的MD5
    second_md5 = calculate_md5(first_hex.encode('ascii'))
    second_hex = bytes_to_hex_string(second_md5)

    # 拼接最终密码 (64字符)
    return first_hex + second_hex

#需要优化代码和添加错误检测
def main():
    print("欢迎使用作业答案生成器v1.0(Beta)")
    print("ets.exe cracked by leitianshuo1337")
    print("This program -> Copyright(©) 2025 leitianshuo1337, All Rights Reserved")
    print("ets.exe -> Copyright(©) 2019 ETS100, All Rights Reserved")
    # if os.path.exists("pwd.json"):
    #     print("查询到之前保存的密码，正在登录...")
    phone:str = 13264003599 # input("请输入手机号:")
    password:str = 20101201 # getpass.getpass("请输入密码:")
    # savePwd:bool = input("是否保存密码以便下次使用(y/n):").lower() == 'y'
    # if savePwd:
    #     with open("pwd.json", "w", encoding="utf-8") as f:
    #         f.write(phone + "\n")
    #         f.write(password)
    print("正在登录...")
    token:str = json.loads(Login(phone = phone, password = password))[0]["body"]["token"]
    PAI:str = json.loads(GetPAI(token = token))[0]["body"]["0"]["parent_id"]
    print("登录成功")
    print("作业列表:")
    homeworkList:list = GetHomeworkURL(token = token, PAI = PAI)
    number:int = 1
    for homework in homeworkList:
        print(str(number) + "." + homework["name"])
        number += 1
    choice:int = int(input("请选择作业编号（0则为全部获取）:"))
    print("正在生成答案...")
    headers:dict = {
        "Host": "cdn.subject.ets100.com",
        "User-Agent": "libcurl-agent/1.0",
        "Accept":"*/*"
    }
    try:
        os.mkdir("./temp")
    except:
        pass
    # 操他妈的我自己写的代码自己都不认识，O(∞)
    if choice != 0:
        with open(homeworkList[choice - 1]["name"] + "_answer" + ".txt", "w", encoding="utf-8") as f:
            # num = 1
            for group in homeworkList[choice - 1]["contents"]:
                f.write(group + ":\n")
                for url in homeworkList[choice - 1]["contents"][group]:
                    response = requests.get(url, headers=headers)
                    with open("./temp/" + url.split("/")[4], "wb") as file:
                        file.write(response.content)
                    with zipfile.ZipFile("./temp/" + url.split("/")[4], 'r') as zip_ref:
                        zip_ref.extractall("./temp/" + url.split("/")[4].split(".")[0], pwd = generate_zip_password(response.content).encode("utf-8"))
                    if group.replace(" ", "") == "听后选择":
                        with open("./temp/" + url.split("/")[4].split(".")[0] + "/info.json", "r", encoding="utf-8") as answer_file:
                            for item in json.loads(json.loads(answer_file.read())[1]["code_json_array"]):
                                f.write(item["answer"])
                            f.write("\n")
                    elif group.replace(" ", "") == "听后回答":
                        with open("./temp/" + url.split("/")[4].split(".")[0] + "/content.json", "r", encoding="utf-8") as answer_file:
                            for item in json.loads(answer_file.read())["info"]["question"]:
                                f.write("第一答案:" + item["std"][0]["value"].replace("</br>", "") + " " + "第二答案:" + item["std"][1]["value"].replace("</br>", "") + " " + "第三答案:" + item["std"][2]["value"].replace("</br>", "") + " " + "关键词:" + item["keywords"] + "\n")
                    elif group.replace(" ", "") == "听后转述":
                        with open("./temp/" + url.split("/")[4].split(".")[0] + "/content.json", "r", encoding="utf-8") as answer_file:
                            item = json.loads(answer_file.read())["info"]
                            try:
                                f.write("第一答案:" + item["std"][0]["value"].replace("<i>", "").replace("</i>", "") + "\n" + "第二答案:" + item["std"][1]["value"].replace("<i>", "").replace("</i>", "") + "\n" + "第三答案:" + item["std"][2]["value"].replace("<i>", "").replace("</i>", "") + "\n")
                            except:
                                f.write("第一答案:" + item["std"][0]["value"].replace("<i>", "").replace("</i>", "") + "\n")
                            # f.write("第一答案:" + item["std"][0]["value"].replace("<i>", "").replace("</i>", "") + "\n" + "第二答案:" + item["std"][1]["value"].replace("<i>", "").replace("</i>", "") + "\n" + "第三答案:" + item["std"][2]["value"].replace("<i>", "").replace("</i>", "") + "\n")
                    elif group.replace(" ", "") == "短文朗读":
                        with open("./temp/" + url.split("/")[4].split(".")[0] + "/content.json", "r", encoding="utf-8") as answer_file:
                            f.write(json.loads(answer_file.read())["info"]["value"].replace("<p>", "").replace("</p>", ""))
                f.write("\n")
                # num += 1
    else:
        for homework in homeworkList:
            with open(homework["name"] + "_answer" + ".txt", "w", encoding="utf-8") as f:
                # num = 1
                for group in homework["contents"]:
                    f.write(group + ":\n")
                    for url in homework["contents"][group]:
                        response = requests.get(url, headers=headers)
                        with open("./temp/" + url.split("/")[4], "wb") as file:
                            file.write(response.content)
                        with zipfile.ZipFile("./temp/" + url.split("/")[4], 'r') as zip_ref:
                            zip_ref.extractall("./temp/" + url.split("/")[4].split(".")[0], pwd = generate_zip_password(response.content).encode("utf-8"))
                        if group.replace(" ", "") == "听后选择":
                            with open("./temp/" + url.split("/")[4].split(".")[0] + "/info.json", "r", encoding="utf-8") as answer_file:
                                for item in json.loads(json.loads(answer_file.read())[1]["code_json_array"]):
                                    f.write(item["answer"])
                                f.write("\n")
                        elif group.replace(" ", "") == "听后回答":
                            with open("./temp/" + url.split("/")[4].split(".")[0] + "/content.json", "r", encoding="utf-8") as answer_file:
                                for item in json.loads(answer_file.read())["info"]["question"]:
                                    f.write("第一答案:" + item["std"][0]["value"].replace("</br>", "") + " " + "第二答案:" + item["std"][1]["value"].replace("</br>", "") + " " + "第三答案:" + item["std"][2]["value"].replace("</br>", "") + " " + "关键词:" + item["keywords"] + "\n")
                        elif group.replace(" ", "") == "听后转述":
                            with open("./temp/" + url.split("/")[4].split(".")[0] + "/content.json", "r", encoding="utf-8") as answer_file:
                                item = json.loads(answer_file.read())["info"]
                                try:
                                    f.write("第一答案:" + item["std"][0]["value"].replace("<i>", "").replace("</i>", "") + "\n" + "第二答案:" + item["std"][1]["value"].replace("<i>", "").replace("</i>", "") + "\n" + "第三答案:" + item["std"][2]["value"].replace("<i>", "").replace("</i>", "") + "\n")
                                except:
                                    f.write("第一答案:" + item["std"][0]["value"].replace("<i>", "").replace("</i>", "") + "\n")
                        elif group.replace(" ", "") == "短文朗读":
                            with open("./temp/" + url.split("/")[4].split(".")[0] + "/content.json", "r", encoding="utf-8") as answer_file:
                                f.write(json.loads(answer_file.read())["info"]["value"].replace("<p>", "").replace("</p>", ""))
                    f.write("\n")
                    # num += 1
    print("答案生成完毕,请查看当前目录下的txt文件")
    if not debugMode:
        shutil.rmtree("./temp")

if __name__ == "__main__":
    main()