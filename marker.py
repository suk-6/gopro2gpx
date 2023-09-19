import json
import os


class Marker:
    def __init__(self):
        self.jsonFolder = "./export"
        self.markers = []
        self.jsonData = {}
        self.count = {}

    def addVideoName(self):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            if line["videoName"] != None:
                self.count[line["videoName"]] = {}

    def saveSum(self, jsonData):
        self.jsonData = jsonData
        self.addVideoName()
        markers = self.jsonData["marker"]

        for marker in markers:
            if marker == None:
                continue
            countObject = self.count[marker["videoName"]]
            for detection in marker["detection"]:
                print(detection)
                label = detection["label"]
                if label not in countObject:
                    countObject[label] = 0
                countObject[label] += 1
        return self.count

    # def saveMarker(self):
    #     polyline = self.jsonData["polyline"]

    #     for line in polyline:
    #         if line["videoName"] != None:
    #             points = line["points"]
    #             detection = self.count[line["videoName"]]
    #             midIndex = int(len(points) / 2)
    #             midPoint = points[midIndex]
    #             pointCount = len(self.markers)

    #             marker = {
    #                 "type": "marker",
    #                 "index": pointCount,
    #                 "x": midPoint["x"],
    #                 "y": midPoint["y"],
    #                 "coordinate": "wgs84",
    #                 "zIndex": 0,
    #                 "content": "",
    #                 "videoName": line["videoName"],
    #                 "detection": detection,
    #             }

    #             self.markers.append(marker)

    #     return self.markers

    def saveMarker(self):
        markers = self.jsonData["marker"]
        videoNames = self.count.keys()

        for videoName in videoNames:
            indexList = []
            for marker in markers:
                if marker == None:
                    continue
                if marker["videoName"] == videoName:
                    indexList.append(marker["index"])
            if indexList == []:
                continue
            midIndex = indexList[int(len(indexList) / 2)]

            for marker in markers:
                if marker == None:
                    continue
                if marker["index"] == midIndex:
                    marker["detection"] = self.count[videoName]
                    self.markers.append(marker)
                    break

        return self.markers
