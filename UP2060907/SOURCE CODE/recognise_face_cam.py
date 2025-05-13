import paho.mqtt.client as mqtt
import face_recognition
import pickle
import cv2
import os
import time


def face(uid):
    people = {"83398834": "Jason", "33e633f7": "person"}

    try:
        target = people[uid]
    except:
        print("no uid given")
        return False

    if not target:
        print("No target found")
        return False

    print("target: ", target)

    cascPathface = (
        os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    )
    faceCascade = cv2.CascadeClassifier(cascPathface)
    data = pickle.loads(open("face_enc", "rb").read())

    start_time = time.time()
    video_capture = cv2.VideoCapture(0)
    try:
        while True:
            if time.time() - start_time > 10:
                print("Have not found the match in 10 seconds")
                return False
            
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            names = []
            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)

                    if name == target:
                        print("found: ", name)
                        return True
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("ending video")
                break
    finally:
        video_capture.release()
        cv2.destroyAllWindows()


def connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT")
        client.subscribe(topic)
    else:
        print(f"Connection failed: {rc}")


def message(client, userdata, msg):
    uid = msg.payload.decode()
    print(f"UID: {uid}")

    result = face(uid)
    if result:
        print("Match found")
        msg = "success"
        client.publish(topic_pub, msg)
        return
    else:
        print("No match found")
        msg = "fail"
        client.publish(topic_pub, msg)
        return


def publish(client, userdata, mid):
    print("Message Published!")


# MQTT connection initialisation
broker_ip = "" # Replace with broker IP. This is just a placeholder
broker_port = 1883
topic = "attendance/request"
topic_pub = "attendance/response"

client = mqtt.Client()
client.on_connect = connect
client.on_message = message
client.on_publish = publish
client.connect(broker_ip, broker_port, 60)

client.loop_forever()
