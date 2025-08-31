git clone --progress --verbose https://github.com/ultralytics/ultralytics
cd ./ultralytics/
mkdir .\objectImages
mkdir .\ultralytics\Dataset\images\test
mkdir .\ultralytics\Dataset\images\train
mkdir .\ultralytics\Dataset\labels\test
mkdir .\ultralytics\Dataset\labels\train
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
pip install -U ultralytics tqdm>=4.41.0 pillow
mkdir VOCdevkit
cp ../VOCtest_06-Nov-2007.tar ./VOCdevkit/
cp ../VOCtrainval_06-Nov-2007.tar ./VOCdevkit/
tar -xvf ./VOCdevkit/VOCtrainval_06-Nov-2007.tar
tar -xvf ./VOCdevkit/VOCtest_06-Nov-2007.tar
cp ../VOCtoYOLO.py .
python ./VOCtoYOLO.py
rm ./VOCdevkit/VOCtrainval_06-Nov-2007.tar
rm ./VOCdevkit/VOCtest_06-Nov-2007.tar
rm ./VOCtoYOLO.py