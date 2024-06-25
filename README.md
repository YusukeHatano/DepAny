Depth-Anything使用の深度画像生成もとにラーメンプロジェクト用ロボットで絶対距離を算出するプログラム.

初使用の際には DepAny.pyと同じディレクトリにて　pip install -r requirements.txt　を実行すること。

【注意】
settingについて

1.キャプチャについてセッティングをDepAny.pyのトリムを行わずカメラframe全体を保存するバージョンの設定用プログラムDepAny_setting.pyにて生成される画像をもとに変更すること(init内xy min max)

1.カメラと容器上部までの距離Cam_to_Topと容器の深さTop_to_Plateについてハードウェア組み立てのたび更新すること
【オプションプログラム】
DepAnyLoop 複数回連続実行　Loop回数最下部で指定
Logread 最下部のディレクトリと階層変更、行数の指定で指定ディレクトリより深いところにあるLog.txtの特定情報の読み取り可能
1 開始時刻
24　容器内平均デプス
25　終了時刻
