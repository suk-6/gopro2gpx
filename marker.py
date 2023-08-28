import json
import os


class Marker:
    def __init__(self):
        self.jsonFolder = "./export"
        self.markers = []
        self.jsonData = self.getJSON()
        self.count = {}
        self.addVideoName()
        self.saveAvg()

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

    def addVideoName(self):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            if line["videoName"] != None:
                self.count[line["videoName"]] = {}

    def saveAvg(self):
        markers = self.jsonData["marker"]

        for marker in markers:
            if marker == None:
                continue
            videoName = marker["videoName"]
            for data in marker["detection"]:
                self.count[videoName][data["label"]] = (
                    self.count[videoName].get(data["label"], 0) + 1
                )

    def saveMarker(self):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            if line["videoName"] != None:
                points = line["points"]
                detection = self.count[line["videoName"]]
                midIndex = int(len(points) / 2)
                midPoint = points[midIndex]

                marker = {
                    "type": "marker",
                    "x": midPoint["x"],
                    "y": midPoint["y"],
                    "coordinate": "wgs84",
                    "zIndex": 0,
                    "content": "",
                    "videoName": line["videoName"],
                    "detection": detection,
                }

                self.markers.append(marker)

        return self.markers
