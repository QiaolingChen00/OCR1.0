import cv2
from math import *
from PIL import Image
import numpy as np
from detect.ctpn_predict import get_det_boxes
from recognize.crnn_recognizer import PytorchOcr
recognizer = PytorchOcr()
import pdb
import os
import time

result_dir = './test_result'
class OCR:

    def ocr(self, image_file):
        # pdb.set_trace()
        # 预处理
        image = np.array(Image.open(image_file).convert('RGB'))
        # detect
        text_recs, img_framed, image = get_det_boxes(image)
        text_recs = self.sort_box(text_recs)
        #recognize
        result = self.charRec(image, text_recs)
        # 放入temp里./test_result/t1.png
        print(image_file.split('/')[-1])
        image_file=image_file.split('/')[-1]
        output_file = os.path.join(result_dir, image_file.split('\\')[-1])
        print('output'+output_file)
        # # 结果放入txt
        # txt_file = os.path.join(result_dir, image_file.split('/')[-1].split('.')[0]+'.txt')
        # print(txt_file)
        # txt_f = open(txt_file, 'w')
        Image.fromarray(img_framed).save(output_file)
        # print("\nRecognition Result:\n")
        # for key in result:
        #     print(result[key][1])
        #     txt_f.write(result[key][1]+'\n')
        # txt_f.close()
        return result,output_file

    def dis(self, image):
        cv2.imshow('image', image)
        cv2.waitKey(0)

    def sort_box(self, box):
        """
        对box进行排序
        """
        box = sorted(box, key=lambda x: sum([x[1], x[3], x[5], x[7]]))
        return box

    def dumpRotateImage(self,img, degree, pt1, pt2, pt3, pt4):
        height, width = img.shape[:2]
        heightNew = int(width * fabs(sin(radians(degree))) + height * fabs(cos(radians(degree))))
        widthNew = int(height * fabs(sin(radians(degree))) + width * fabs(cos(radians(degree))))
        matRotation = cv2.getRotationMatrix2D((width // 2, height // 2), degree, 1)
        matRotation[0, 2] += (widthNew - width) // 2
        matRotation[1, 2] += (heightNew - height) // 2
        imgRotation = cv2.warpAffine(img, matRotation, (widthNew, heightNew), borderValue=(255, 255, 255))
        pt1 = list(pt1)
        pt3 = list(pt3)

        [[pt1[0]], [pt1[1]]] = np.dot(matRotation, np.array([[pt1[0]], [pt1[1]], [1]]))
        [[pt3[0]], [pt3[1]]] = np.dot(matRotation, np.array([[pt3[0]], [pt3[1]], [1]]))
        ydim, xdim = imgRotation.shape[:2]
        imgOut = imgRotation[max(1, int(pt1[1])): min(ydim - 1, int(pt3[1])),
                    max(1, int(pt1[0])): min(xdim - 1, int(pt3[0]))]

        return imgOut


    def charRec(self, img, text_recs, adjust=False):
        """
        加载OCR模型，进行字符识别
        """
        results = {}
        xDim, yDim = img.shape[1], img.shape[0]

        for index, rec in enumerate(text_recs):
            xlength = int((rec[6] - rec[0]) * 0.1)
            ylength = int((rec[7] - rec[1]) * 0.2)
            if adjust:
                pt1 = (max(1, rec[0] - xlength), max(1, rec[1] - ylength))
                pt2 = (rec[2], rec[3])
                pt3 = (min(rec[6] + xlength, xDim - 2), min(yDim - 2, rec[7] + ylength))
                pt4 = (rec[4], rec[5])
            else:
                pt1 = (max(1, rec[0]), max(1, rec[1]))
                pt2 = (rec[2], rec[3])
                pt3 = (min(rec[6], xDim - 2), min(yDim - 2, rec[7]))
                pt4 = (rec[4], rec[5])

            degree = degrees(atan2(pt2[1] - pt1[1], pt2[0] - pt1[0]))  # 图像倾斜角度

            partImg = self.dumpRotateImage(img, degree, pt1, pt2, pt3, pt4)
            # dis(partImg)
            if partImg.shape[0] < 1 or partImg.shape[1] < 1 or partImg.shape[0] > partImg.shape[1]:  # 过滤异常图片
                continue
            text = recognizer.recognize(partImg)
            if len(text) > 0:
                results[index] = [rec]
                results[index].append(text)  # 识别文字

        return results

if __name__ == "__main__":
    result_dir = './test_result'
    model = OCR()
    image_file = "./test_images/t1.png"
    result, image_framed = model.ocr(image_file)
    pdb.set_trace()
    print(result)