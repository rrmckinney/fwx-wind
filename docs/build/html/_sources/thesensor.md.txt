# The Expendable Wind Sensor

The expendable wind sensors were adapted from [cactus.io](http://cactus.io/hookups/weather/anemometer/davis/hookup-arduino-to-davis-anemometer).

Wildfire models serve as an invaluable tool in aiding first reposnders in estimating fire growth and spread dynamics [(NCAR)](https://ral.ucar.edu/solutions/products/wrf-fire-wildland-fire-modeling). Validation of these models is difficult as wildfires are dangerous at scale [(Morvan,2019)](https://doi.org/10.1007/978-3-319-51727-8_59-1). At UBC, we hope to overcome this barrier though with expendable wind sensors that will be placed in the path of prescribed wildfires.

The configuration utilizes a Davis cup anemometer and Arduino hardware. the Davis cup anemometers are reliable instruments that are used for a suite of applications, including a network of wind sensors currently ran by the UBC Weather Forecasting Research Team [(WFRT)](https://doi.org/10.1007/978-3-319-51727-8_59-1). Arduino is also a commenable comapany with low-cost hardware and open source software that is used for many applications as well [(adafruit)](https://www.adafruit.com/category/17). 

In summary the wind sensors are composed of: 
- A Davis cup anemometer
- An Arduino UNO board; and 
- An Arduino UNO SD card board extension

The full circuit diagram for the setup is shown below:
![Wind Sensor Circuit Diagram.](/pics/circuit_diagram.png)

This setup allows the Davis station to be placed at canopy height (4-6m) with the circuit board and sd card buried beneath ground for safe keeping. Since water is the main issue of concern under the ground, the electronics were placed in tupperware containers with all holes sealed with sealant.

![Full instrument setup.](/pics/expendable_sensors.jpg)

To place the sensors at canopy height, they are mounted onto two sections of 10ft aluminuim poles and secured to three nearby trees with guy wiress. 

![Sensor field mount setup.](/pics/field_setup.png)
