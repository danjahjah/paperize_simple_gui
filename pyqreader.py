import cv2
from pyzbar.pyzbar import decode
import time
import numpy as np
import re


class QRscanner():
  # паттерн поиска текущего номера страницы и колическтва страниц
  regpattern = r"(?!---pprzv1:)(?P<cnt>\d{,3})/(?P<total>\d{,3})(?<!---)" 

  def __init__(self, camid, messenger):
    """
    camid: индекс видеокамеры в винде (0, 1...) или имя в линуксах (/dev/video0)
    messenger: функция вывода текста в главном окне 
    """
    # всего страниц в документе
    self.pages_cnt=0
    # текущая страница
    self.current_page=0

    self.filepath = None
    
    self.camid = camid
    # объект камеры
    self.cam = None
    # слоаврь с текстом из кода {ноиер страницы : данные}
    self.qrdata={}
    # флаг завершения сканирования документа 
    self.ready=False
    # текущий кадр - типа фрейм
    self.frame = None


  def printout(self, message):
    """print to main window"""
    print(message)


  def add_text(self, message):
    """add text to video frame"""
    if self.frame is None:
      print(message)
      return
    
    cv2.putText(self.frame, message, (50, 50) , cv2.FONT_HERSHEY_SIMPLEX ,  
               1, (0, 255, 0) , 2, cv2.LINE_AA)

    
  def init_camera(self):

    if self.camid == None:
      self.printout("Wrong videocamera ID == None")
      return None
    
    self.cam = cv2.VideoCapture(self.camid)
    self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    self.cam.set(cv2.CAP_PROP_FPS, 24)

    if not self.cam.isOpened():
      self.printout(f"Cannot open camera id={self.camid}")
      return None

 
  def check_page_count(self):
    """
    Проврка количества сосканированных страниц
    если все соканировано - ставил флаг ready 

    """    
    if len(self.qrdata) >= int(self.pages_cnt):      
      self.ready = True

  def capture_qr(self):

    self.init_camera()

    if self.cam is None:
      return

    detect = cv2.QRCodeDetector()
    cv2.startWindowThread()
    
    # цикл сканирования с окошком  
    while True:
      success, frame = self.cam.read()
      self.frame = frame

      if not success:
        self.printout("Can't receive frame (stream end?). Exiting ...")
        break

      # пытаемся распознать qr код    
      value, _, _ = detect.detectAndDecode(frame)

      if value: # нашли в кадре код
        self.procced_qrdata(value)
        self.check_page_count()
      
      else:
        self.add_text("No QR code")

      time.sleep(0.25)  
      cv2.imshow('QR Scaner', frame) 

      if cv2.waitKey(1) == ord('q'):
        print("Exit")
        break 

      # поставлен флаг ready - значит все сосканировали. Выходим  
      if self.ready == True:
        print("All pages scanned. Exit")
        break 


    self.cam.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    return

  def get_file_path(self, data):    

    path = data.split(':n:')[1].rstrip('---')
    self.filepath = path

  def procced_qrdata(self, data):
    """
    Сюда попадаем когда сосканирован и распознаан QR код
    он может не относиться к теме
    """
    print(data)
    match = re.search(QRscanner.regpattern, data)

    # если нашли строчку с номером страницы
    if match:

      total = match.groupdict().get('total')
      
      # если в отсканированном коде не совпадает количество страниц 
      if self.pages_cnt > 0 and self.pages_cnt != total:
        self.add_text("Suspicious data. Page not added")
        self.printout(f"Suspicious data: pages conut do no match {total} {self.pages_cnt}. Page not added")
        return



      self.pages_cnt=int(match.groupdict().get('total'))
      self.current_page=int(match.groupdict().get('cnt'))

      if self.current_page == 1 and self.filepath is None:
        self.get_file_path(data.splitlines()[0])


      print(match.groupdict())

      # проверяем что эта страница уже отсканирована
      if self.current_page in self.qrdata.keys():
        self.add_text('This page is already scanned')
        return 1

      self.qrdata[self.current_page] = data

    else: # если каклй-то левый qr код 
      self.add_text('Wrong QR code')
      return 0





cam = QRscanner(1, None)

cam.capture_qr()


exit()






def proceed_qrdata(data):

  proceed_qrdata.cnt += 1 

  print('---- NEW DATA ----')
  print(data)

  match = re.search(QRscanner.regpattern, data)
  if match:
    print(match.groupdict())

  if proceed_qrdata.cnt == 3:
    return 0, 3, 3

  return 1, proceed_qrdata.cnt, 3

proceed_qrdata.cnt =0

def add_text(frame, current_value, total_value):
   

    if current_value == 0 and total_value ==0:
      string_display = "QR not detected"
    else:
      string_display = f"{current_value}/{total_value}"

    return cv2.putText(frame, string_display, (50, 50) , cv2.FONT_HERSHEY_SIMPLEX ,  
                   1, (0, 255, 0) , 2, cv2.LINE_AA)




def capture_qr(deviceID, func):

  # blank_image = np.zeros((height,width,3), np.uint8)

  cam = cv2.VideoCapture(deviceID)
  cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  cam.set(cv2.CAP_PROP_FPS, 24)

  detect = cv2.QRCodeDetector()

  if not cam.isOpened():
   print("Cannot open camera")
   exit()

  cv2.startWindowThread()
  while True:
    success, frame = cam.read()

    ready = False # флаг что весь список кодов считан

    if not success:
     print("Can't receive frame (stream end?). Exiting ...")
     break

    
     
    current_value = 0
    total_value = 0

    # for i in decode(frame):  
    #   # сюда попадаем если поймали qr код       
    #   value, points, straight_qrcode = detect.detectAndDecode(frame)
    #   ret, current_value, total_value = func(value)      
    #   if ret == 0:
    #     ready = True
    #     break 

    value, points, straight_qrcode = detect.detectAndDecode(frame)

    if value:
      print(value)
      ret, current_value, total_value = func(value)
      if ret == 0:
        ready = True
        break 
    else:
      print("No qr code")  
    




 
    frame = add_text(frame, current_value, total_value)

    time.sleep(0.25)  
    cv2.imshow('QR Scaner', frame) 
    if cv2.waitKey(1) == ord('q') or ready == True:
      break
    

  cam.release()
  cv2.destroyAllWindows()
  cv2.waitKey(1)

capture_qr(1, proceed_qrdata)