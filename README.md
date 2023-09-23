# uit_car_racing
Demo [**here**](https://www.youtube.com/live/yspJeNuXQY8?si=Si7b0kadvPlJWEpt&t=959)

Download [**weights**](https://uithcm-my.sharepoint.com/:u:/g/personal/20520490_ms_uit_edu_vn/EfFvjaZ4ttBJrWHXUBIXpzQBUUw9npr0g4fT0Vy2J9-LrQ?e=smiucu) to folder **models**
1. docker build -t cauhamau/uit_car_racing:v2 .
2. docker run -it --gpus all --name uit_car_racing --add-host=host.docker.internal:host-gateway cauhamau/uit_car_racing bash
3. python3 main_test.py 
