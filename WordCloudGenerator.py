from collections import Counter
import os
import sys
import jieba
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
from wordcloud import STOPWORDS, ImageColorGenerator, WordCloud
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QPushButton, QTextEdit
from PyQt5.QtGui import QPixmap


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("词云图")
        self.setFixedSize(800, 545)

        self.select_file_button = QPushButton(
            "Select text", self, clicked=self.select_text)
        self.select_file_button.move(20, 20)
        self.select_file_button.setFixedSize(114, 45)

        self.select_image_button = QPushButton(
            "Select image", self, clicked=self.select_image)
        self.select_image_button.move(146, 20)
        self.select_image_button.setFixedSize(114, 45)

        # 创建一个QLabel控件
        self.Label = QLabel("剔除字：", self)
        self.Label.move(20, 70)
        self.Label.setFixedSize(120, 45)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(20, 120, 240, 345)

        self.generate_word_cloud_button = QPushButton(
            "Generate", self, clicked=self.generate_word_cloud)
        self.generate_word_cloud_button.move(65, 475)
        self.generate_word_cloud_button.setFixedSize(150, 45)

        self.image_label = QLabel(self)
        self.image_label.move(280, 20)
        self.image_label.setFixedSize(500, 500)
        self.image_label.setStyleSheet("background-color: white")

        self.enlarge_button = QPushButton(
            "🔍", self, clicked=self.clicked_image)
        self.enlarge_button.move(745, 20)
        self.enlarge_button.setFixedSize(35, 35)
        self.enlarge_button.hide()

    def select_text(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "Text files (*.txt);;All files (*)", options=options)
        if filename:
            self.filename = filename

    def select_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        imagefilename, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "", "Image files (*.png *.jpg *.bmp *.gif *.webp);;All files (*)", options=options)
        if imagefilename:
            self.image = imagefilename

    def pushButton(self):
        self.enlarge_button.show()

    def clicked_image(self):
        plt.imshow(self.wc)  # 显示词云
        plt.axis('off')  # 关闭x,y轴
        plt.show()  # 显示

    def generate_word_cloud(self):
        # 判断文本文件路径是否正确
        if not hasattr(self, 'filename'):
            QMessageBox.information(
                self, "错误", "请先选择一个文件!")
            return
        # 判断自定义背景图片路径是否正确
        if not hasattr(self, 'image'):
            reply = QMessageBox.question(self, '提示',
                                         "背景文件不存在。您想使用默认值吗？", QMessageBox.Ok, QMessageBox.No)
            if reply == QMessageBox.Ok:
                width=700
                height=1100
                img = Image.new('RGB', (width, height))
                for x in range(width):
                    for y in range(height):
                        r = int(255 * x / (width - 1))
                        g = int(255 * y / (height - 1))
                        b = 255 - r - g
                        img.putpixel((x, y), (r, g, b))
                # 保存图片
                img.save("temp.png")

                backgroud = np.array(Image.open("temp.png"))
            else:
                return
        else:
            backgroud = np.array(Image.open(self.image))
        
        # 内置的屏蔽词,并添加自己设置的词语
        if not self.text_edit.toPlainText().strip() == '':
            stopwords_list = self.text_edit.toPlainText().split(" ")
            for s in stopwords_list:
                STOPWORDS.add(s)
        
        with open(self.filename, 'r', encoding='utf-8') as f:
            textfile = f.read()

        with open('all_stopwords.txt', 'r', encoding='utf-8') as f:
            stopwords_list = [line.strip() for line in f.readlines()]
        
        
        c = Counter()  # python一种数据集合，用来存储字典
        wordlist = jieba.lcut(textfile)
        for x in wordlist:
            if len(x) > 1 and x != '\r\n':  # 不是单个字 并且不是特殊符号
                try:
                    c[x] += 1  # 这个单词的次数加一
                except:
                    continue
        for (k, v) in c.most_common():  # 过滤掉次数小于5的单词
            if v < 5 or k in stopwords_list:
                c.pop(k)
                continue
        print(len(c),c)
        x = []
        y = []
        for k, v in c.most_common(500):  # 在前300个常用词语中
            x.append(k)
            y.append(v)
        wordlist = x[0:300]  # 截取前150个
        
        space_list = ' '.join(wordlist)
        # print(space_list)

        wc = WordCloud(
            width=1400, height=2200,
            background_color='white',
            mode='RGB',
            mask=backgroud,
            max_words=500,
            stopwords=STOPWORDS,
            font_path='C:\Windows\Fonts\SIMLI.TTF',
            max_font_size=150,
            relative_scaling=0.4,
            random_state=50,
            scale=2
        ).generate(space_list)

        image_color = ImageColorGenerator(backgroud)
        self.wc = wc.recolor(color_func=image_color)

        img = wc.to_image()
        img.save("temp222.png")

        # 获取原始图像的宽度和高度
        width, height = img.size

        # 计算宽高比
        aspect_ratio = width / height

        if aspect_ratio > 1:
            # 设置调整后的宽度和高度
            new_width = 500  # 替换为所需的新宽度
            new_height = int(new_width / aspect_ratio)

            # 调整图像大小
            img = img.resize((new_width, new_height),
                             resample=Image.Resampling.LANCZOS)
        else:
            # 设置调整后的宽度和高度
            new_height = 500  # 替换为所需的新宽度
            new_width = int(new_height * aspect_ratio)

            # 调整图像大小
            img = img.resize((new_width, new_height),
                             resample=Image.Resampling.LANCZOS)

        img.save("temp.png")
        pixmap = QPixmap("temp.png")
        # print(img.tobytes())
        # pixmap = QPixmap.fromImage(QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB666))
        self.image_label.setPixmap(pixmap)
        # self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.pushButton()

    def closeEvent(self, event):
        os.remove("temp.png")


def main():
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
