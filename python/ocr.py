import base64
import os
import re
import subprocess
import uuid

import requests
from PIL import Image


def ocr_tesseract(pic, file="", lang="eng", accuracy="high"):
    if accuracy == "high":
        image = Image.open(pic).convert("L")
        pic = "{}.{}".format(uuid.uuid5(uuid.NAMESPACE_DNS,
                                        pic.split(".")[0]),
                             pic.split(".")[-1])
        image.save(pic)
    try:
        file = file.replace(".txt", "")
        cmd = "tesseract {} {} -l {}".format(pic, file or "stdout", lang)
        result = subprocess.Popen(cmd,
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).stdout.read()
        result = result.decode("utf-8").split("\r")[0].replace("\x0c", "")
    finally:
        if accuracy:
            os.remove(pic)
    return file + ".txt" if file else result


def ocr_baidu(pic, file="", lang="eng", accuracy="high"):
    accuracy = {"high": "accurate", "low": "general"}[accuracy]
    base_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/{}_basic".format(
        accuracy)
    f = open(pic, 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img, "language_type": lang.upper()}
    access_token = "24.66455d872e6117a6a5c08b3e56ce191b.2592000.1596684535.282335-19446321"
    request_url = base_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    while response:
        result = response.json()
        if "error_code" in result and 100 <= result["error_code"] <= 111:
            API_KEY = "uKxDDZrBwEZqeAs5wI1fq7hy"
            SECRET_KEY = "chOfpAmaKqikmg2rvQDT07CsPbbw4TDW"
            url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}".format(
                API_KEY, SECRET_KEY)
            response = requests.get(url)
            access_token = response.json()["access_token"]
            with open(__file__, "r") as f:
                src = f.read()
            with open(__file__, "w") as f:
                try:
                    dst = re.sub("access_token\s*=\s*\"\S+\"",
                                 "access_token = \"{}\"".format(access_token),
                                 src)
                    f.write(dst)
                except Exception:
                    f.write(src)
            request_url = base_url + "?access_token=" + access_token
            response = requests.post(request_url, data=params, headers=headers)
            continue
        elif "log_id" in result:
            words = "\n".join([
                word["words"] for word in result["words_result"]
            ]).replace(" ", "")
            if not file:
                return words
            else:
                file = file if file.endswith(".txt") else file + ".txt"
                with open(file, "w") as f:
                    f.write(words)
                return file
        else:
            return ""


def ocr(pic, mode="tesseract", file="", lang="eng", accuracy="high"):
    """
    :param pic: the path of the picture
    :param mode: the method
    :param file: the file to save the result
    :param lang: the language, the default is English
    :param accuracy: recognition accuracy,
                     'high' stand for high-precision, 'low' stand for low-precision
    :return: recognition result or the file path
    """
    return eval(
        "ocr_{}(pic, file=file, lang=lang, accuracy=accuracy)".format(mode))


if __name__ == "__main__":

    def test(pic, correct_answers):
        tesseract = ocr(pic, mode="tesseract")
        baidu = ocr(pic, mode="baidu")
        return {
            "tesseract": tesseract,
            "baidu": baidu,
            "correct_answers": correct_answers
        }

    result1 = test(r"test_ocr\test01.jpg", "7364")
    result2 = test(r"test_ocr\test02.jpg", "46168")
    result3 = test(r"test_ocr\test03.jpg", "KDQU")
    print(result1, result2, result3, sep="\n")
