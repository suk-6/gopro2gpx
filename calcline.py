import math


class Calc:
    def __init__(self):
        self.jsonData = {}
        self.videoPoint = {}
        self.calcPoint = {}

    def getLine(self, videoName):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            if line["videoName"] != None:
                if line["videoName"] == videoName:
                    return line

        return None

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

    def isWithinRadius(self, point1, point2, radius=0.001):
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

    def calcContinuousLine(self):
        for video in self.videoPoint.keys():
            end = self.videoPoint[video]["end"]
            self.calcPoint[video] = []
            for compareVideo in self.videoPoint.keys():
                if video == compareVideo:
                    continue
                compareStart = self.videoPoint[compareVideo]["start"]
                if self.isWithinRadius(end, compareStart):
                    self.calcPoint[video].append(compareVideo)

        # print(self.calcPoint)
        return self.calcPoint

    def colorLine(self):
        polyline = self.jsonData["polyline"]

        for line in polyline:
            afterVideos = self.calcPoint[line["videoName"]]
            if len(afterVideos) == 0:
                continue
            for afterVideo in afterVideos:
                for afterLine in polyline:
                    if afterLine["videoName"] == afterVideo:
                        afterLine["options"]["strokeColor"] = line["options"][
                            "strokeColor"
                        ]

        return polyline

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

    def calcPoint2Point(self, jsonData):
        self.jsonData = jsonData
        self.loadPoint()
        self.calcContinuousLine()
        polyline = self.colorLine()

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
            print(line["videoName"], lineLength)

        return polyline
