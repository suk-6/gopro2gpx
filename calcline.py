from utiljson import Utiljson
import math

utiljson = Utiljson()


class Calc:
    def __init__(self):
        self.jsonData = utiljson.getJSON()
        self.videoPoint = {}
        self.calcPoint = {}
        self.loadPoint()

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

    def calcLine(self):
        for video in self.videoPoint.keys():
            end = self.videoPoint[video]["end"]
            self.calcPoint[video] = []
            for compareVideo in self.videoPoint.keys():
                if video == compareVideo:
                    continue
                compareStart = self.videoPoint[compareVideo]["start"]
                if self.isWithinRadius(end, compareStart):
                    self.calcPoint[video].append(compareVideo)

        return self.calcPoint


calc = Calc()

print(calc.calcLine())
