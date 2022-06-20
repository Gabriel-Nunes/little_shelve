import cv2
from pyzbar import pyzbar
import re


class BarcodeReader:
	REGEX = re.compile(r'\d{9}')
	code = ''

	def read_barcodes(self, frame, camera):
		barcodes = pyzbar.decode(frame)
		for barcode in barcodes:
			x, y , w, h = barcode.rect
			#1 Recognizing and decoding the barcode/QR code that we will be showing to the camera.
			barcode_info = barcode.data.decode('utf-8')
			if re.match(self.REGEX, barcode_info):
				self.code = barcode_info
				print()
				print(barcode_info)
				
			cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
			
			#2 Adding the stored information as a text on the recognized barcode/QR code.
			font = cv2.FONT_HERSHEY_DUPLEX
			cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)
			#3 exporting the stored information as a text document.
			with open("barcode_result.txt", mode ='w') as file:
				file.write("Recognized Barcode:" + barcode_info)
		return frame

	def run(self):
		#1 turning on the camera of the computer using OpenCV. 
		# If you have an external camera, you have to change the value 0 to 1 depending on the device.
		camera = cv2.VideoCapture(0)
		ret, frame = camera.read()
		#2 run a while loop to keep running the decoding function until the “Esc” key is pressed.
		while ret:
			ret, frame = camera.read()
			frame = self.read_barcodes(frame, camera)
			
			if re.match(self.REGEX, self.code):
				break
			cv2.imshow('Barcode/QR code reader', frame)
			if cv2.waitKey(1) & 0xFF == 27:
				break

		#3 releasing the camera that we turned on in the first step.
		# And then we are closing the application window.
		camera.release()
		cv2.destroyAllWindows()

# reader = BarcodeReader()
# reader.main()