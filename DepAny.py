import argparse
import cv2
import numpy as np
import os
import torch
import torch.nn.functional as F
from torchvision.transforms import Compose
from tqdm import tqdm
import time
from datetime import datetime
from depth_anything.dpt import DepthAnything
from depth_anything.util.transform import Resize, NormalizeImage, PrepareForNet


def toBytes(message):
     
     return bytes(message.encode())


def Capture(): 
    cap = cv2.VideoCapture(2)

    now = datetime.now()
    print(datetime.now())
    time_id = now.strftime("%H%M%S")

    # カメラが正常にオープンされているか確認
    if not cap.isOpened():
        print("カメラが見つかりません。")
        exit()

    ret, frame = cap.read()

    # 相対値固定のため、余分な範囲を計算しないような画像のトリム設定
    ystart = 180
    yfinish= 400
    hight = yfinish -ystart
    xstart = 350
    xfinish = 470
    width = xfinish - xstart
    
    cropped_frame = frame[ystart:ystart+hight, xstart:xstart+width]

    if ret:
        # Specify the file name
        ext = ".jpg"
        file_name = str(time_id) + ext
        # Join the save directory path and file name
        global indir
        global outdir

        indir = "C:\\Users\\space\\Depth-Anything\\"
        outdir = indir
        indir = indir + "Test\\"
        outdir = outdir + "Tested\\"
        year = str(now.strftime("%Y"))
        time = str(now.strftime("%H%M%S"))
        month = str(now.strftime("%m"))
        day = str(now.strftime("%m%d"))
       

        indir = indir + year + "\\" + month + "\\" + day + "\\" + time
        outdir = outdir + year + "\\" + month + "\\" + day + "\\" + time


        if not os.path.exists(indir):
            os.makedirs(indir)
        else:
            pass

        save_path = os.path.join(indir,file_name)
        # Save the captured frame to the specified directory
        cv2.imwrite(save_path,cropped_frame)
        print("Image captured and saved successfully at:", save_path)
    else:
        print("Failed to capture image.")
    
    # Release the camera
    cap.release()

    

def DepAny():
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--encoder', type=str, default='vitl', choices=['vits', 'vitb', 'vitl'])
        parser.add_argument('--pred-only', dest='pred_only', action='store_true', help='only display the prediction')
        parser.add_argument('--grayscale', dest='grayscale', action='store_true', help='do not apply colorful palette')
    
        args = parser.parse_args()
    
        DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(datetime.now())

        print(DEVICE)
    
        #pre-trainedd model
        depth_anything = DepthAnything.from_pretrained('LiheYoung/depth_anything_{}14'.format(args.encoder)).to(DEVICE).eval()
    
        #situation
        total_params = sum(param.numel() for param in depth_anything.parameters())
        print('Total parameters: {:.2f}M'.format(total_params / 1e6))
    
        #resize
        transform = Compose([
            Resize(
                width=518,
                height=518,
                resize_target=False,
                keep_aspect_ratio=True,
                ensure_multiple_of=14,
                resize_method='lower_bound',
                image_interpolation_method=cv2.INTER_CUBIC,
            ),
            NormalizeImage(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            PrepareForNet(),
            ])

        # reading file
        if os.path.isfile(indir):
            if indir.endswith('txt'):
                with open(indir, 'r') as f:
                    filenames = f.read().splitlines()
            else:
                filenames = [indir]
        else:
            filenames = os.listdir(indir)
            filenames = [os.path.join(indir, filename) for filename in filenames if not filename.startswith('.')]
            filenames.sort()
    
        #make directory
        os.makedirs(outdir, exist_ok=True)
    
        for filename in tqdm(filenames):
            raw_image = cv2.imread(filename)
            image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB) / 255.0
        
            h, w = image.shape[:2]
        
            image = transform({'image': image})['image']
            image = torch.from_numpy(image).unsqueeze(0).to(DEVICE)
        
            with torch.no_grad():
                depth = depth_anything(image)
                depth = F.interpolate(depth[None], (h, w), mode='bilinear', align_corners=False)[0, 0]


            # relative depth tensor
            mean =depth.mean().item()
            max = depth.max().item()
            min = depth.min().item()
            median = depth.mean().item()

            Cam_to_Top = float(0.365) # User Difined Parameter[m]
            Top_to_Plate = float(0.090) # User Difined Parameter[m]


            # meter depth tensor
            depth_abs = (depth - depth.min()) / (depth.max() - depth.min()) *Top_to_Plate

            abs_max = Cam_to_Top + Top_to_Plate - depth_abs.min().item()
            abs_min = Cam_to_Top + Top_to_Plate - depth_abs.max().item()
            abs_mean = Cam_to_Top + Top_to_Plate - depth_abs.mean().item()
            abs_median = Cam_to_Top + Top_to_Plate - depth_abs.median().item()


            # raw image index
            max_index = depth.argmax() 
            max_position = np.unravel_index(max_index.cpu().numpy(), depth.shape)
            min_index = depth.argmin() 
            min_position = np.unravel_index(min_index.cpu().numpy(), depth.shape)

            # 降下距離導出のためネギ部分のみを切り取り
            ycstart = 0
            ycfinish = 140
            hc = ycfinish - ycstart
            xcstart = 20
            xcfinish = 120
            wc = xcfinish - xcstart


            depth_calc = depth_abs[ycstart:ycstart+hc,xcstart:xcstart+wc]
            calc_max = Cam_to_Top + Top_to_Plate - depth_calc.min().item()
            calc_min = Cam_to_Top + Top_to_Plate - depth_calc.max().item()
            calc_median = Cam_to_Top + Top_to_Plate - depth_calc.mean().item()
            calc_mean = Cam_to_Top + Top_to_Plate - depth_calc.median().item()


            size = depth.size()
            size_c = depth_calc.size()
            print("\n",size)
            print("\n",size_c)

            print("\nmin_abs_pos =",min_position)
            print("\nmax_abs_pos =",max_position)

            print("\nmax =",max,"\nmin =",min,"\nmean =",mean,"\nmedian =",median)
            print("\nabs_max =",abs_max,"\nabs_min =",abs_min,"\nabs_mean =",abs_mean,"\nabs_median =",abs_median)

            print("\ncalc_max =",calc_max,"\ncalc_min =",calc_min,"\ncalc_mean =",calc_mean,"\ncalc_median =",calc_median)
            
            # 実際にツールを降下させる距離の選定に使うデータ
            # Movement = DEPTH - (Cam to ToolPosition + Tool length) を想定
            DEPTH = calc_mean
            Movement = DEPTH - (0.05 + 0.10)
            print("\nDEPTH =",DEPTH)
            print("Movement =",Movement)

            #tranform depth data 
            depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
        
            depth = depth.cpu().numpy().astype(np.uint8)

            #gray scale option
            if args.grayscale:
                depth = np.repeat(depth[..., np.newaxis], 3, axis=-1)
            else:
                depth = cv2.applyColorMap(depth, cv2.COLORMAP_INFERNO)


        
            #readed filename 
            filename = os.path.basename(filename)
        
            cv2.imwrite(os.path.join(outdir, filename[:filename.rfind('.')] + '_depth.png'), depth)
               
            print("\n",datetime.now())


Capture()
DepAny()