import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from keras.models import load_model

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '이미지 분류기'
        self.initUI()

        # 모델 로드
        self.model = load_model("model/keras_Model.h5", compile=False)

        # 레이블 로드
        self.class_names = open("model/labels.txt", "r", encoding='utf-8').readlines()

    def initUI(self):
        self.setWindowTitle(self.title)

        # 이미지 표시 레이블
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # 클래스 및 정확도 표시 레이블
        self.resultLabel = QLabel(self)
        self.resultLabel.setAlignment(Qt.AlignCenter)

        # 업로드 버튼
        self.btnUpload = QPushButton('이미지 업로드', self)
        self.btnUpload.clicked.connect(self.openFileDialog)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.resultLabel)
        layout.addWidget(self.btnUpload)
        self.setLayout(layout)

        self.setGeometry(100, 100, 640, 480)

    def openFileDialog(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "이미지를 선택하세요", "", "Image files (*.jpg *.png *.jpeg *.bmp)")
        if filePath:
            self.processImage(filePath)

    def processImage(self, filePath):
        frame = cv2.imread(filePath)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))
        h, w, ch = frame.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.label.setPixmap(QPixmap.fromImage(p))

        # 이미지 분류
        image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Keras 모델에 적합한 이미지 형식으로 변환
        image = (image / 255.0).astype(np.float32)
        image = np.expand_dims(image, axis=0)
        prediction = self.model.predict(image)
        index = np.argmax(prediction)
        class_name = self.class_names[index]
        confidence_score = prediction[0][index]
        result_text = f"클래스: {class_name.strip()}, 정확도: {str(np.round(confidence_score * 100))[:-2]}%"
        self.resultLabel.setText(result_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
