import cv2
import serial
import time
import base64
import requests # Sirf ye library chahiye, jo har system pe hoti hai
import os

# ---------- CONFIGURATION ----------
# Aapki Mistral API Key
MISTRAL_API_KEY = "m2iLcvTBtae0NngKi5DjrOz8VmL2WcSd"
URL = "https://api.mistral.ai/v1/chat/completions"

# ---------- ARDUINO SETUP ----------
try:
    # Port COM3 check kar lena (Agar Arduino connected hai)
    arduino = serial.Serial('COM3', 9600)
    time.sleep(2)
    print("Arduino Connected!")
except:
    arduino = None
    print("Arduino Not found.")

# ---------- DATABASE ----------
authorized_plates = ["ABC123", "KHI456", "LEA789", "FAR123"]

# ---------- CAMERA SETUP ----------
# IP Webcam URL
camera = cv2.VideoCapture("http://192.168.100.5:8080/video")
frame_count = 0

print("System Active...")

while True:
    ret, frame = camera.read()
    if not ret: continue

    cv2.imshow("Smart Parking", frame)
    frame_count += 1

    # Har 60 frames baad scan
    if frame_count % 60 == 0:
        cv2.imwrite("scan.jpg", frame)
        
        try:
            with open("scan.jpg", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")

            # Direct API Payload (Mistral Standard)
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
                "temperature": 0 # Accuracy ke liye 0 rakha hai
            }

            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }

            # Seedha server se baat karega, kisi library ki help ke bagair
            response = requests.post(URL, json=payload, headers=headers)
            data = response.json()

            if "choices" in data:
                plate = data["choices"][0]["message"]["content"].strip().upper().replace(" ", "")
                print(f"Detected: {plate}")
                
                # Check Authorization
                if any(auth in plate for auth in authorized_plates):
                    print("ACCESS GRANTED")
                    if arduino: arduino.write(b'1')
                else:
                    print("ACCESS DENIED")
                    if arduino: arduino.write(b'0')
            else:
                print("API Error Response:", data)

        except Exception as e:
            print(f"System Error: {e}")

    # 'q' dabane se stop hoga
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
if arduino: arduino.close()
if os.path.exists("scan.jpg"): os.remove("scan.jpg")