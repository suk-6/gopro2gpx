import re
import json
import os
from glob import glob
import random
from datetime import datetime
from natsort import natsorted
import xml.etree.ElementTree as ET
import cv2
from dotenv import load_dotenv
import requests
import base64

load_dotenv(".env")

detectionURL = os.getenv("detectionURL")

if not os.path.exists("./tmp"):
    os.makedirs("./tmp")
else:
    os.system("rm -rf ./tmp/*")

if not os.path.exists("./export"):
    os.makedirs("./export")

if not os.path.exists("./export_frames"):
    os.makedirs("./export_frames")

# 출력 JSON 파일 경로
outputPath_json = f'./export/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
outputPath_images = "./export_frames/"

videosPath = "/Volumes/T7/Original-videos/wangsimni3/videos/"
videoFiles = natsorted(os.listdir(videosPath))
print(videoFiles)


def randomColor():
    color = "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )
    return color


def detectObjects(frame):
    # 이미지를 base64로 변환
    _, buffer = cv2.imencode(".jpg", frame)
    textImage = buffer.tobytes()
    base64Image = str(base64.b64encode(textImage), "utf-8")

    response = requests.post(detectionURL, data={"frame": base64Image})

    detection = response.json()

    print(detection)

    return detection


def saveFrame(point, kmlPath, pointCount):
    GPXPath = kmlPath.replace(".kml", ".gpx")

    root = ET.parse(os.path.join(GPXPath)).getroot()

    metaTime_str = (
        root.find(".//{http://www.topografix.com/GPX/1/1}metadata")
        .find("{http://www.topografix.com/GPX/1/1}time")
        .text
    )
    metaTime = datetime.strptime(metaTime_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    videoPath = videosPath + videoDict[kmlPath.split("/")[-1].replace(".kml", "")]

    # 영상 읽기
    cap = cv2.VideoCapture(videoPath)

    # trkseg 내의 모든 trkpt 태그 처리
    for trkpt in root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt"):
        lat = float(trkpt.attrib["lat"])
        lon = float(trkpt.attrib["lon"])

        if lat == point["y"] and lon == point["x"]:
            print(f"Found point: {lat}, {lon} - {point['y']}, {point['x']}")
            trkptTime_str = trkpt.find("{http://www.topografix.com/GPX/1/1}time").text
            trkptTime = datetime.strptime(trkptTime_str, "%Y-%m-%dT%H:%M:%S.%fZ")

            timeDifference = trkptTime - metaTime
            secondsDifference = timeDifference.total_seconds()

            # 해당 시간으로 영상 프레임 이동
            cap.set(cv2.CAP_PROP_POS_MSEC, secondsDifference * 1000)

            # 프레임 읽기
            ret, frame = cap.read()

            try:
                # 프레임 저장
                outputPath = f"./{outputPath_images}{pointCount}.jpg"
                cv2.imwrite(outputPath, frame)
                print(f"Frame saved to {pointCount}.jpg")

                # 프레임에 대한 객체 검출
                return detectObjects(frame)

            except Exception as e:
                print("Failed to read frame:", e)

                return None

    # 영상 읽기 종료
    cap.release()


def savePoint(point, kmlPath):
    pointCount = len(polylines["marker"])

    detection = saveFrame(point, kmlPath, pointCount)

    if detection is None:
        return None

    marker = {
        "type": "marker",
        "index": pointCount,
        "x": point["x"],
        "y": point["y"],
        "coordinate": "wgs84",
        "zIndex": 0,
        "content": "",
        "videoName": videoDict[kmlPath.split("/")[-1].replace(".kml", "")],
        "detection": detection,
    }

    return marker


def convert(kmlPath):
    # KML 파일 열기
    with open(kmlPath, "r") as kmlFile:
        kmlData = kmlFile.read()

    # <coordinates> 태그 안의 데이터 추출
    coordinatesData = re.findall(
        r"<coordinates>(.*?)</coordinates>", kmlData, re.DOTALL
    )

    # 데이터 추출 및 열 바꾸기
    points = []
    for coordinates in coordinatesData:
        lines = coordinates.strip().split("\n")  # 각 줄을 분리
        for i, line in enumerate(lines):
            longitude, latitude, _ = line.split(",")  # 세 번째 값은 무시
            result = {"x": float(longitude), "y": float(latitude)}
            points.append(result)

            if i % 300 == 0:
                polylines["marker"].append(savePoint(result, kmlPath))

    return points


polylines = {"marker": [], "polyline": []}

videoDict = {}

for video in videoFiles:
    os.system(f"gopro2gpx -s {videosPath + video} ./tmp/{video[:-4]}")
    videoDict[video[:-4]] = video

kmlFiles = glob("./tmp/*.kml")

for kmlPath in kmlFiles:
    points = convert(kmlPath)
    color = randomColor()

    polyline = {
        "type": "polyline",
        "points": points,
        "coordinate": "wgs84",
        "videoName": videoDict[kmlPath.split("/")[-1].replace(".kml", "")],
        "options": {
            "strokeColor": color,
            "strokeWeight": 5,
            "strokeStyle": "solid",
            "strokeOpacity": 1,
        },
    }

    polylines["polyline"].append(polyline)

with open(outputPath_json, "w") as jsonFile:
    json.dump(polylines, jsonFile, indent=4)

print(f"saved to {outputPath_json}.")
