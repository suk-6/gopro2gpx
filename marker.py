import json
import os
from utiljson import Utiljson

utiljson = Utiljson()


class Marker:
    def __init__(self):
        self.jsonFolder = "./export"
        self.markers = []
        self.jsonData = utiljson.getJSON()
        self.count = {}
        self.addVideoName()
        self.saveAvg()

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
            sumDetect = self.count[videoName]
            for label in marker["detection"].keys():
                labelCount = marker["detection"][label]
                if label not in sumDetect:
                    sumDetect[label] = 0
                sumDetect[label] += labelCount

    def saveMarker(self):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            if line["videoName"] != None:
                points = line["points"]
                detection = self.count[line["videoName"]]
                midIndex = int(len(points) / 2)
                midPoint = points[midIndex]
                pointCount = len(self.markers)

                marker = {
                    "type": "marker",
                    "index": pointCount,
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
