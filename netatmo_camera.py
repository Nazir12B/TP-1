import aiohttp
import asyncio
import os
from dotenv import load_dotenv
import cv2

 
face_detector= cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')

c= 50
async def fetch_netatmo_data():
    load_dotenv()
    variable = os.getenv('API_KEY')
    if not variable:
        print("La clé n'existe pas .")
        return
    
    url = "https://api.netatmo.com/api/gethomesdata"
 
    headers = {
        'Authorization': f'Bearer {variable}'
    }
 
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                homes = data.get('body', {}).get('homes', [])
                for home in homes:
                    cam = home.get('cameras', [])
                    for macam in cam:
                        vpn = macam.get('vpn_url')
                        vpn=vpn+"/live/index.m3u8"

                        capture = cv2.VideoCapture(vpn)
                        
                        while True:
 
                            ret, frame= capture.read()
                            gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                            face= face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(c,c))

                            for x, y, w, h in face:
                                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0), 2)

                            if ret:
                                    cv2.imshow('Camera Feed', frame)

                                    if cv2.waitKey(1) & 0xFF == ord('q'):
                                        break
                            else:
                                print("Camera eteinte flux de video inacessible")
                                break
                        capture.release()
                        key= cv2.waitKey(1)&0xFF
                        if key==ord('q'):
                            break
                        cv2.destroyAllWindows()
            else:
                print("Erreur:", response.status)
                return None
 
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(fetch_netatmo_data())