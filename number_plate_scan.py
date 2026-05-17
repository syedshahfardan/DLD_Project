import cv2
import serial
import time
import base64
import requests
import os


MISTRAL_API_KEY = "m2iLcvTBtae0NngKi5DjrOz8VmL2WcSd"
URL = "https://api.mistral.ai/v1/chat/completions"

try:
    arduino = serial.Serial('COM7', 9600)
    time.sleep(2)
    print("Arduino Connected!")
except:
    arduino = None
    print("Arduino Not found.")

user_database = {
    "ABC123": "JAWAD",
    "KHI456": "EBAD",
    "LEA789": "Ali",
    "FAR123": "FARDAN"
}

camera = cv2.VideoCapture("http://192.168.100.5:8080/video")
frame_count = 0

print("System Active...")

while True:
    ret, frame = camera.read()
    if not ret: continue

    cv2.imshow("Smart Parking", frame)
    frame_count += 1

    if frame_count % 60 == 0:
        cv2.imwrite("scan.jpg", frame)
        
        try:
            with open("scan.jpg", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "model": "pixtral-12b-2409",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Read the vehicle number plate. Return ONLY the alphanumeric text. No extra words."},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}
                        ]
                    }
                ],
                "temperature": 0
            }

            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(URL, json=payload, headers=headers)
            data = response.json()

            if "choices" in data:
                plate = data["choices"][0]["message"]["content"].strip().upper().replace(" ", "")
                print(f"Detected: {plate}")
                
                # Dynamic Matching Logic
                found_user = None
                for auth_plate, name in user_database.items():
                    if auth_plate in plate:
                        found_user = name
                        break
                
                if found_user:
                    print(f"ACCESS GRANTED: Welcome {found_user}")
                    if arduino: 
                        message = f"W{found_user}\n"
                        arduino.write(message.encode())
                        print("Signal sent: Gate Opening...")
                        time.sleep(1.5)  
                else:
                    print("ACCESS DENIED")
                    if arduino: 
                        arduino.write(b"0\n")
                        print("Signal sent: Access Denied")
                        time.sleep(1.5)  
            else:
                print("API Error Response:", data)

        except Exception as e:
            print(f"System Error: {e}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
if arduino: arduino.close()
if os.path.exists("scan.jpg"): os.remove("scan.jpg")