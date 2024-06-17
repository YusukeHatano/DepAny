import cv2
import numpy as np
import os
import torch
import torch.nn.functional as F
from torchvision.transforms import Compose
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime
from depth_anything.dpt import DepthAnything
from depth_anything.util.transform import Resize, NormalizeImage, PrepareForNet
import argparse

class Negi():
    def main(self):
        self.Capture(2)
        self.DepAny()

    def __init__(self):
        self.filenames = None
        self.time = None 
        self.frame = None # raw image
        self.cropped_frame = None # cropped image
        # picture_pixel
        self.y_min = 90
        self.y_max = 270
        self.x_min = 150
        self.x_max = 300
        # calculate_pixel
        self.yc_min = None
        self.yc_max = None
        self.xc_min = None
        self.xc_max = None
        # for distance to define DEPTH range
        self.Cam_to_Top = 0.475
        self.Top_to_Plate = 0.120
        self.indir = None # raw image　dirctory
        self.outdir = None # output depth image dirctory
        self.depth = None # depth Tensor
        self.depth_abs = None # meter distance from camera
        self.depth_calc = None # only Negi
        self.DEPTH = None # for move
        # xy position
        self.max_Pos = None
        self.min_Pos = None

    def Loading(self,dir):
        if os.path.isfile(dir):
            if dir.endswith('txt'):
                with open(dir, 'r') as f:
                    self.filenames = f.read().splitlines()
            else:
                self.filenames = [dir]
        else:
            self.filenames = os.listdir(dir)
            self.filenames = [os.path.join(dir, filename) for filename in self.filenames if not filename.startswith('.')]
            self.filenames.sort()

    def Trimming(self,y1,y2,x1,x2,subject):
        h = y2 - y1
        w = x2 - x1
        return subject[y1:y1+h, x1:x1+w]

    def TimeDir(self):
        ext = ".jpg"
        file_name = str(self.time.strftime("%H%M%S")) + ext

        self.indir = os.getcwd()
        self.outdir = os.getcwd()
        self.indir =  self.indir + "\\Test\\"
        self.outdir = self.outdir + "\\Tested\\"
        self.indir = self.indir + str(self.time.strftime("%Y")) + "\\" + str(self.time.strftime("%m"))  + \
                "\\" + str(self.time.strftime("%m%d"))  + "\\" + str(self.time.strftime("%H%M%S")) 
        self.outdir = self.outdir + str(self.time.strftime("%Y")) + "\\" + str(self.time.strftime("%m"))  + \
                "\\" + str(self.time.strftime("%m%d"))  + "\\" + str(self.time.strftime("%H%M%S")) 

        os.makedirs(self.indir, exist_ok=True)
        os.makedirs(self.outdir, exist_ok=True)
        save_path = os.path.join(self.indir, file_name)
        cv2.imwrite(save_path, self.cropped_frame)
        print("Image captured and saved successfully at:", save_path)

    def Capture(self,number):
        cap = cv2.VideoCapture(number)
        self.time = datetime.now()
        print(datetime.now())

        if not cap.isOpened():
            print("カメラが見つかりません。")
            exit()

        ret, self.frame = cap.read()
        # Trimming
        self.cropped_frame = self.Trimming(self.y_min, self.y_max, self.x_min, self.y_max, self.frame)
        if ret:
            self.TimeDir()
            print("success")
        else:
            print("Failed to capture image.")

        cap.release()

    def Edge(self):
        # Loading Image
        self.Loading(self.outdir)

        for filename in tqdm(self.filenames,disable = True):
            # エッジ検出
            frame = cv2.imread(filename)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            coords = np.column_stack(np.where(edges > 0))
            self.yc_min, self.xc_min = coords.min(axis=0) - (10,10)
            self.yc_max, self.xc_max = coords.max(axis=0) + (10,10)
            print("\nyrange = ", self.yc_min, "to", self.yc_max)
            print("xrange = ", self.xc_min, "to", self.xc_max)

            #グラフプロット  
            plt.plot(figsize=(edges.shape[1] / 100, edges.shape[0] / 100), dpi=100)
            plt.imshow(edges, cmap='gray')
            plt.axis('off')  
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            path = os.path.join(self.outdir,"edge.png")
            plt.savefig(path)
            print("\nedge success")

    def DepAny(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--encoder', type=str, default='vitl', choices=['vits', 'vitb', 'vitl'])
        args = parser.parse_args()    
        DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(DEVICE)
    
        depth_anything = DepthAnything.from_pretrained('LiheYoung/depth_anything_{}14'.format(args.encoder)).to(DEVICE).eval()
    
        transform = Compose([
            Resize(
                width=518,
                height=518,
                resize_target = False,
                keep_aspect_ratio = True,
                ensure_multiple_of = 14,
                resize_method='lower_bound',
                image_interpolation_method = cv2.INTER_CUBIC,
            ),
            NormalizeImage(mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]),
            PrepareForNet(),
        ])

        # reading file
        self.Loading(self.indir)

        for filename in tqdm(self.filenames,disable = True):
            raw_image = cv2.imread(filename)
            image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB) / 255.0
            h, w = image.shape[:2]
            image = transform({'image': image})['image']
            image = torch.from_numpy(image).unsqueeze(0).to(DEVICE)
        
            with torch.no_grad():
                depth = depth_anything(image)
                depth = F.interpolate(depth[None], (h, w), mode='bilinear', align_corners=False)[0, 0]
                self.depth = depth
                self.Analyse_Tensor(self.depth)

            #tranform depth data 
            depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
            depth = depth.cpu().numpy().astype(np.uint8)
            depth = cv2.applyColorMap(depth, cv2.COLORMAP_INFERNO)
            #readed filename 
            filename = os.path.basename(filename)
            cv2.imwrite(os.path.join(self.outdir, filename[:filename.rfind('.')] + '_depth.png'), depth)

            #エッジ検出
            self.Edge()
            
            # meter depth tensor
            self.depth_abs = torch.full(self.depth.size(), (self.Cam_to_Top + self.Top_to_Plate)) - \
                             (self.depth - self.depth.min()) / (self.depth.max() - self.depth.min()) *self.Top_to_Plate
            self.Analyse_Tensor(self.depth_abs)
            # Trimming
            self.depth_calc = self.Trimming(self.yc_min,self.yc_max,self.xc_min,self.xc_max,self.depth_abs)
            self.Analyse_Tensor(self.depth_calc)
            self.DEPTH = self.depth_calc.mean().item()

            max_index = self.depth_calc.argmax() 
            self.max_position = np.unravel_index(max_index.cpu().numpy(), self.depth_calc.shape)
            min_index = self.depth_calc.argmin() 
            self.min_position = np.unravel_index(min_index.cpu().numpy(), self.depth_calc.shape)
            print("\nmin_calc_pos =",self.min_position,"\nmax_calc_pos =", self.max_position)
            # 実際にツールを降下させる距離の選定に使うデータ
            print("\nDEPTH =",self.DEPTH)
            print(datetime.now())

    def Analyse_Tensor(self,subject):
        max = subject.max().item()
        min = subject.min().item()
        mean =subject.mean().item()
        print("\nmax =", max,"\nmin = ", min,"\nmean =", mean)

run = Negi()
run.main()
