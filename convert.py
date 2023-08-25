import re
import json
import os
from glob import glob
import random


# 출력 JSON 파일 경로
outputPath = 'data.json'

videosPath = '/Volumes/T7/Original-videos/wangsimni/videos/'
videoFiles = os.listdir(videosPath)
print(videoFiles)

def randomColor():
    color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color

def convert(kmlPath):
    # KML 파일 열기
    with open(kmlPath, 'r') as kmlFile:
        kmlData = kmlFile.read()

    # <coordinates> 태그 안의 데이터 추출
    coordinatesData = re.findall(r'<coordinates>(.*?)</coordinates>', kmlData, re.DOTALL)

    # 데이터 추출 및 열 바꾸기
    points = []
    for coordinates in coordinatesData:
        lines = coordinates.strip().split('\n')  # 각 줄을 분리
        for line in lines:
            longitude, latitude, _ = line.split(',')  # 세 번째 값은 무시
            points.append({"x": float(longitude), "y": float(latitude)})

    return points

polylines = {
        "polyline": []
    }

for video in videoFiles:
    os.system(f"gopro2gpx -s -vvv {videosPath + video} ./tmp/{video[:-4]}")

kmlFiles = glob('./tmp/*.kml')
print(kmlFiles)

for kmlFile in kmlFiles:
    points = (convert(kmlFile))
    color = randomColor()

    polyline = {
                "type": "polyline",
                "points": points,
                "coordinate": "wgs84",
                "options": {
                    "strokeColor": color,
                    "strokeWeight": 5,
                    "strokeStyle": "solid",
                    "strokeOpacity": 1
                }
            }
    
    polylines['polyline'].append(polyline)

with open(outputPath, 'w') as jsonFile:
    json.dump(polylines, jsonFile, indent=4)

print(f"saved to {outputPath}.")