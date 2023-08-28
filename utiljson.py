import json
import os


class Utiljson:
    def __init__(self):
        self.jsonFolder = "./export"

    def getJSON(self):
        # JSON 파일들의 타임스탬프를 기준으로 정렬
        jsonFiles = [f for f in os.listdir(self.jsonFolder) if f.endswith(".json")]
        jsonFiles.sort(
            key=lambda x: os.path.getmtime(os.path.join(self.jsonFolder, x)),
            reverse=True,
        )

        if jsonFiles:
            latestJson = os.path.join(self.jsonFolder, jsonFiles[0])

            # JSON 파일 내용 읽어오기
            with open(latestJson, "r") as jsonFile:
                jsonData = json.load(jsonFile)

            return jsonData
        else:
            return None
