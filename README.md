# uit_car_racing
Download [**weights**](https://drive.google.com/drive/folders/1UC60MkFcgfEHsx8GfxrrNr7o5oSq3Asa?usp=sharing) to folder **models**
1. docker build -t cauhamau/uit_car_racing:v2 .
2. docker run -it --gpus all --name uit_car_racing --add-host=host.docker.internal:host-gateway cauhamau/uit_car_racing bash
3. python3 main_test.py 
