# uPyIoT

Spring in Europe has already started and many people are also having allergy problems. Therefore, I thought of making a project to measure air quality and collect this data to train a model that can tell me, when is the best time to open my apartment windows to ventilate the rooms and thus minimize possible allergy attacks and sneezing! Like almost everyone right now (thanks to COVID-19), I'm working from home and this photo shows the possible causes of allergies:

|       |
|:-----:|
|<img src="https://lemariva.com/storage/app/uploads/public/5e8/a10/3a0/5e8a103a0e68e594189329.jpg" width="400px" style="max-width:400px">|
|Courtyard of my department|

This code allows you to connect an M5Stack ATOM running MicroPython to the Google Cloud Platform (GCP) to collect air-quality variables obtained from reading two sensors:
* **BME680**: a gas sensor that integrates high-linearity and high-accuracy gas, pressure, humidity and temperature sensors. 
* **PMSA003A**: a digital and universal particle concentration sensor, which can be used to obtain the number of suspended particles in the air, i.e. the concentration of particles, and output them to a digital interface.

## Video
Check out this video:

[![Google Cloud Platform getting data from an M5Stack ATOM sensing the air-quality](https://img.youtube.com/vi/DTF0sHlUx7Y/0.jpg)](https://www.youtube.com/watch?v=DTF0sHlUx7Y)


## References
Connection to GCP taken from <a href="https://github.com/GoogleCloudPlatform/iot-core-micropython" target="_blank">GoogleCloudPlatform/iot-core-micropython</a>
