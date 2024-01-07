#include <FastLED_NeoPixel.h>

// Which pin on the Arduino is connected to the LEDs?
#define DATA_PIN 4
// How many LEDs are attached to the Arduino?
#define NUM_LEDS 1200
// LED brightness, 0 (min) to 255 (max)
#define BRIGHTNESS 255

/* Declare the NeoPixel strip object:
*     * Argument 1 = Number of LEDs in the LED strip
*     * Argument 2 = Arduino pin number
*     * Argument 3 = LED strip color order
*
* The FastLED_NeoPixel version uses template arguments instead of function
* arguments. Note the use of '<>' brackets!
*
* You can switch between libraries by commenting out one of these two objects.
* In this example they should behave identically.
*/
// Adafruit_NeoPixel strip(NUM_LEDS, DATA_PIN, NEO_GRB);  // <- Adafruit NeoPixel version
FastLED_NeoPixel<NUM_LEDS, DATA_PIN, NEO_GRB> strip;      // <- FastLED NeoPixel version

struct pawbean{
   int start;
   int end;
};

// pawbean0 is a special pawbean that addresses the whole strip
const pawbean pawbean0 = {0, 35+42+42+34};
const pawbean pawbean1 = {0, 34};
const pawbean pawbean2 = {35, 35+41};
const pawbean pawbean3 = {35+42, 35+42+41};
const pawbean pawbean4 = {35+42+42, 35+42+42+34};

// Zero-index be damned!!
pawbean pawbean_arr[] = {pawbean0, pawbean1, pawbean2, pawbean3, pawbean4};

String serial_cmd;

void setup() {
	strip.begin();  // initialize strip (required!)
	strip.setBrightness(BRIGHTNESS);
  Serial.begin(115200);
}

void loop() {
  if(Serial.available() > 0) {
    serial_cmd = Serial.readStringUntil('\n');
    processSerial(serial_cmd);
  }

  // These are the default simon colors, keeping them around as reference.
  // colorSetPaw(strip.Color(0, 255, 0), pawbean1); // green
  // colorSetPaw(strip.Color(255, 0, 0), pawbean2); // red
  // colorSetPaw(strip.Color(0, 0, 255), pawbean3); // blue
  // colorSetPaw(strip.Color(255, 255, 0), pawbean4); // yellow
}

/*
* Takes an input string read from serial and calls the functions
* needed to respond appropriately
* 
*     1. Serial command as a string
*/
void processSerial(String serial_cmd) {
  int prev_space = 0;
  int next_space = serial_cmd.indexOf(" ");
  String command = serial_cmd.substring(0, next_space);
  Serial.println("command is " + command);

  if(command != "ON") {
    Serial.println("Unsupported command");
    return;
  }

  prev_space = next_space + 1;
  next_space = serial_cmd.indexOf(" ", prev_space);
  int pawbean_index = serial_cmd.substring(prev_space, next_space).toInt();
  Serial.println("pawbean_index is " + String(pawbean_index));

  prev_space = next_space + 1;
  next_space = serial_cmd.indexOf(" ", prev_space);
  int red_value = serial_cmd.substring(prev_space, next_space).toInt();
  Serial.println("red_value is " + String(red_value));

  prev_space = next_space + 1;
  next_space = serial_cmd.indexOf(" ", prev_space);
  int green_value = serial_cmd.substring(prev_space, next_space).toInt();
  Serial.println("green_value is " + String(green_value));

  prev_space = next_space + 1;
  next_space = serial_cmd.indexOf(" ", prev_space);
  int blue_value = serial_cmd.substring(prev_space, next_space).toInt();
  Serial.println("blue_value is " + String(blue_value));

  colorSetPaw(strip.Color(red_value, green_value, blue_value), pawbean_arr[pawbean_index]);
  Serial.println("Setting pawbean " + String(pawbean_index) + " to " + String(red_value) + "," + String(green_value) + "," + String(blue_value));
}

/*
* Fills a strip with a specific color, starting at 0 and continuing
* until the entire strip is filled. Takes two arguments:
* 
*     1. the color to use in the fill
*     2. the amount of time to wait after writing each LED
*/
void colorWipe(uint32_t color, unsigned long wait) {
	for (unsigned int i = 0; i < strip.numPixels(); i++) {
		strip.setPixelColor(i, color);
		strip.show();
		delay(wait);
	}
}

/*
* Sets a pawbean to one color
*   
*     1. the color to use in the fill
*     2. the pawbean to color
*/
void colorSetPaw(uint32_t color, pawbean pawbean) {
  colorSet(color, pawbean.start, pawbean.end);
}
/*
* Sets LEDs completely to one color
* 
*     1. the color to use in the fill
*     2. the index to start at
*     3. the index to end on
*/
void colorSet(uint32_t color, int start, int end) {
  // Get full strip length strip.numPixels()

	for (unsigned int i = start; i <= end; i++) {
		strip.setPixelColor(i, color);
	}
  strip.show();
}

/*
* Runs a marquee style "chase" sequence. Takes three arguments:
*
*     1. the color to use in the chase
*     2. the amount of time to wait between frames
*     3. the number of LEDs in each 'chase' group
*     3. the number of chases sequences to perform
*/
void theaterChase(uint32_t color, unsigned long wait, unsigned int groupSize, unsigned int numChases) {
	for (unsigned int chase = 0; chase < numChases; chase++) {
		for (unsigned int pos = 0; pos < groupSize; pos++) {
			strip.clear();  // turn off all LEDs
			for (unsigned int i = pos; i < strip.numPixels(); i += groupSize) {
				strip.setPixelColor(i, color);  // turn on the current group
			}
			strip.show();
			delay(wait);
		}
	}
}


/*
* Simple rainbow animation, iterating through all 8-bit hues. LED color changes
* based on position in the strip. Takes two arguments:
* 
*     1. the amount of time to wait between frames
*     2. the number of rainbows to loop through
*/
void rainbow(unsigned long wait, unsigned int numLoops) {
	for (unsigned int count = 0; count < numLoops; count++) {
		// iterate through all 8-bit hues, using 16-bit values for granularity
		for (unsigned long firstPixelHue = 0; firstPixelHue < 65536; firstPixelHue += 256) {
			for (unsigned int i = 0; i < strip.numPixels(); i++) {
				unsigned long pixelHue = firstPixelHue + (i * 65536UL / strip.numPixels()); // vary LED hue based on position
				strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue)));  // assign color, using gamma curve for a more natural look
			}
			strip.show();
			delay(wait);
		}
	}
}

/*
* Blanks the LEDs and waits for a short time.
*/
void blank(unsigned long wait) {
	strip.clear();
	strip.show();
	delay(wait);
}