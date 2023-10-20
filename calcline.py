import math
import random
from pprint import pprint
from labels import labels, weightofObject


class Calc:
    def __init__(self):
        self.jsonData = {}
        self.videoPoint = {}
        self.calcPoint = []
        self.polyline = []
        self.group = []
        self.colors = {
            "red": "#ff0000",
            "green": "#00ff00",
            "blue": "#0000ff",
            "grey": "#808080",
        }

    def getLine(self, videoName):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            if line["videoName"] != None:
                if line["videoName"] == videoName:
                    return line

        return None

    def randomColor(self):
        color = "#{:02x}{:02x}{:02x}".format(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

        return color

    def startLine(self, videoName):
        line = self.getLine(videoName)
        if line == None:
            return None

        points = line["points"]
        return points[0]

    def endLine(self, videoName):
        line = self.getLine(videoName)
        if line == None:
            return None

        points = line["points"]
        return points[-1]

    def calcDistance(self, point1, point2):
        x1, y1 = point1["x"], point1["y"]
        x2, y2 = point2["x"], point2["y"]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def isWithinRadius(self, point1, point2, radius=0.00018):
        distance = self.calcDistance(point1, point2)
        return distance <= radius

    def loadPoint(self):
        for video in self.jsonData["polyline"]:
            if video["videoName"] != None:
                self.videoPoint[video["videoName"]] = {}
                self.videoPoint[video["videoName"]]["start"] = self.startLine(
                    video["videoName"]
                )
                self.videoPoint[video["videoName"]]["end"] = self.endLine(
                    video["videoName"]
                )

    # def calcContinuousLine(self):
    #     for video in self.videoPoint.keys():
    #         end = self.videoPoint[video]["end"]
    #         self.calcPoint[video] = []
    #         for compareVideo in self.videoPoint.keys():
    #             if video == compareVideo:
    #                 continue
    #             compareStart = self.videoPoint[compareVideo]["start"]
    #             if self.isWithinRadius(end, compareStart):
    #                 self.calcPoint[video].append(compareVideo)

    #     print(self.calcPoint)
    #     return self.calcPoint

    def distanceVideos(self, videoName):
        distance = {}

        for video in self.videoPoint.keys():
            if video == videoName:
                continue
            distance[video] = self.calcDistance(
                self.videoPoint[videoName]["end"], self.videoPoint[video]["start"]
            )

        return sorted(distance.items(), key=lambda item: item[1])

    def findAllPaths(self, startVideo, currentPath=[], radius=0.00018):
        currentPath.append(startVideo)

        if startVideo not in self.videoPoint:
            return

        startVideo_end = self.videoPoint[startVideo]["end"]

        if startVideo in self.endVideos:
            self.calcPoint.append(currentPath.copy())

        for compareVideo in self.videoPoint.keys():
            if startVideo == compareVideo or compareVideo in currentPath:
                continue
            compareStart = self.videoPoint[compareVideo]["start"]
            if self.isWithinRadius(startVideo_end, compareStart):
                self.findAllPaths(compareVideo, currentPath.copy())

        if startVideo not in self.endVideos:  # 일정 오차범위 내에 있는 비디오가 없을 경우
            distanceVideos = self.distanceVideos(startVideo)  # 가까운 순서대로 정렬된 비디오 리스트
            if self.isWithinRadius(  # 가장 가까운 비디오가 오차범위 내에 있을 경우
                startVideo_end,
                self.videoPoint[distanceVideos[0][0]]["start"],
                radius,
            ):
                self.findAllPaths(distanceVideos[0][0], currentPath.copy(), radius)
            else:  # 가장 가까운 비디오가 오차범위 내에 없을 경우에는 오차범위를 조금씩 늘려가며 탐색
                for i in range(30):
                    radius += 0.00001
                    if self.isWithinRadius(
                        startVideo_end,
                        self.videoPoint[distanceVideos[0][0]]["start"],
                        radius,
                    ):
                        self.findAllPaths(
                            distanceVideos[0][0], currentPath.copy(), radius
                        )

    def colorLine(self, continuousVideos, color):
        polyline = self.jsonData["polyline"]

        for video in continuousVideos:
            for line in polyline:
                if line["videoName"] == video:
                    line["options"]["strokeColor"] = color

        self.jsonData["polyline"] = polyline

    def haversine(self, lat1, lon1, lat2, lon2):
        radius = 6371.0

        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = radius * c

        return distance

    def calcPoint2Point(self):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            points = line["points"]
            lineLength = 0
            for point in enumerate(points):
                if point[0] == len(points) - 1:
                    break
                lineLength += self.haversine(
                    point[1]["y"],
                    point[1]["x"],
                    points[point[0] + 1]["y"],
                    points[point[0] + 1]["x"],
                )

            line["lineLength"] = lineLength

        self.polyline = polyline

    def removeDuplicates(self):
        uniqueList = []
        for item in self.calcPoint:
            if item not in uniqueList:
                uniqueList.append(item)
        self.calcPoint = uniqueList

    def sumLength(self, videos):
        length = 0
        for video in videos:
            length += self.getLine(video)["lineLength"]

        return length

    def sumObjects(self, videos):
        objects = {}
        markers = self.jsonData["marker"]

        for video in videos:
            for marker in markers:
                if marker == None:
                    continue
                if marker["videoName"] == video:
                    for label in marker["detection"].keys():
                        if label not in objects:
                            objects[label] = 0
                        objects[label] += marker["detection"][label]

        return objects

    def groupLine(self):
        index = 0

        for continuousVideo in self.calcPoint:
            group = {}
            group["index"] = index
            group["videos"] = continuousVideo
            group["lineLength"] = self.sumLength(continuousVideo)
            group["objects"] = self.sumObjects(continuousVideo)
            group["congestion"] = self.calcCongestion(group["objects"])

            self.group.append(group)
            index += 1

    def shortestGroup(self):  # 최단 거리 그룹 찾기 (파란색으로 표시)
        shortestGroup = self.group[0]

        for group in self.group:
            if group["lineLength"] < shortestGroup["lineLength"]:
                shortestGroup = group

        self.colorLine(shortestGroup["videos"], self.colors["blue"])

    def longestGroup(self):  # 최장 거리 그룹 찾기 (빨간색으로 표시)
        longestGroup = self.group[0]

        for group in self.group:
            if group["lineLength"] > longestGroup["lineLength"]:
                longestGroup = group

        self.colorLine(longestGroup["videos"], self.colors["red"])

    def calcCongestion(self, objects):  # 혼잡도 계산 (백분율 반환)
        congestion = 0

        for object in objects.keys():
            try:
                weight = weightofObject[labels[int(object)]]
            except:
                weight = 0.1

            congestion += objects[object] * weight

        # return round(((congestion**2) / 10e2), 1)
        return round(congestion, 1)

    def lowCongestionGroup(self):  # 혼잡도가 가장 낮은 그룹 찾기 (초록색으로 표시)
        lowCongestionGroup = self.group[0]

        for group in self.group:
            if group["congestion"] < lowCongestionGroup["congestion"]:
                lowCongestionGroup = group

        self.colorLine(lowCongestionGroup["videos"], self.colors["green"])

    def lastMarker(self):
        originMarkers = self.jsonData["marker"]
        usedVideos = []
        markers = []

        for group in self.group:
            midVideo = group["videos"][len(group["videos"]) // 2]

            if midVideo in usedVideos:
                for i in range(len(group["videos"])):
                    if group["videos"][i] not in usedVideos:
                        midVideo = group["videos"][i]
                        break

            for marker in originMarkers:
                if marker == None:
                    continue
                if marker["videoName"] == midVideo:
                    marker["index"] = group["index"]
                    marker["detection"] = group["objects"]
                    marker["videos"] = group["videos"]
                    marker["congestion"] = group["congestion"]
                    marker["lineLength"] = group["lineLength"]

                    markers.append(marker)

            usedVideos += group["videos"]

        return markers

    def run(self, jsonData, startVideo, endVideos=[]):
        self.jsonData = jsonData
        self.endVideos = endVideos

        self.loadPoint()
        self.findAllPaths(startVideo)
        self.removeDuplicates()
        self.calcPoint2Point()
        self.groupLine()
        pprint(self.group)

        self.shortestGroup()
        self.longestGroup()
        self.lowCongestionGroup()

        self.jsonData["polyline"] = self.polyline
        self.jsonData["group"] = self.group
        self.jsonData["marker"] = self.lastMarker()

        return self.jsonData
