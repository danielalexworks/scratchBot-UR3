//config
int forwardDirection = 1;   //mayneed to flip these
int backwardDirection = 0;
int stepDelay = 2;//10000;          //microseconds

         //for manually changign directions (might use for more, might not need)
int dirP = 16;               //pin for controlling motor direction
int dirN = 17;               //pin for controlling motor direction
int stepPinP = 27;            //pin to trigger motor step
int stepPinN = 14;            //pin to trigger motor step
int dir = forwardDirection; //current direction of motor
bool isbuttonHigh = false;  //used to make sure no double button press
int led = 2;               //onboard led pin
int stopPinFront = 19;       //pin for button stop
int stopPinBack = 18;        //pin for button stop

long stepsFromBack = 0;
long stepsFromFront = 0;
long totalSteps = 0;
bool isPositionKnown = false;


//TODO
//SET up translation between ticket position and camera position


//gotToFront() move in foward direction until hits end stop
//      prints complete to Serial

//gotToBack() move in backward direction until hits end stop
//      prints complete to Serial

//checkStops() returns 0 if not hitting end stop, returns pinNumber of endstop button if pressed

//changeDirection() toggles direction
//      prints complete to Serial

//changeDirectionTo("forward" or "backward") set direction to _
//      prints complete to Serial

//takeAStep() cycle motor once with stepDelay set in //config

//checkChangeDirectionButton() changes direction of motor when button Pressed (for debugging most liklely)

//figureCurrentPosition() Moves cam to back stop, returns to location where motion started and updates stepsFromBack
//      prints stepsFromBack to Serial

//moveToStep(long x) move to x steps away from backstop, if position not known, return error
//      prints stepsFromBack to Serial

//toLong(String str) converts str to long

//setTotalSteps(long num)       sets value in sketch
//setStepsFromBack(long num)    sets value in sketch
//setStepsFromFront(long num)   sets value in sketch

void setup() {
  Serial.begin(115200);

  pinMode(led,OUTPUT);
  
  pinMode(dirP, OUTPUT);
  pinMode(dirN, OUTPUT);
  pinMode(stepPinP, OUTPUT);
  pinMode(stepPinN, OUTPUT);
  pinMode(stopPinBack, INPUT);
  pinMode(stopPinFront, INPUT);
  

  digitalWrite(dirP, LOW);
  digitalWrite(dirN, LOW);
  digitalWrite(stepPinP, LOW);
  digitalWrite(stepPinN, HIGH);
  Serial.println("setup omplete");
  
}



void loop() {
  
  String cs = checkSerial();
  if (cs) {
    evalSerial(cs);
  }
  

  yield();
  
}


String checkSerial() {
  if (Serial.available()) {
    String in = Serial.readString();
    return in;
  } else {
    return "0";
  }
}


void evalSerial(String in) {
  if (in == "calibrate") {
    totalSteps = calibrateSteps();
    stepsFromBack = 0;
    Serial.println("complete");
  } else if (in == "changeDirection") {
    changeDirection();
    Serial.println("complete");
  } else if (in == "forward") {
    setDirection(1);
    Serial.println("complete");
  } else if (in == "backward") {
    setDirection(0);
    Serial.println("complete");
  } else if (in == "goToFront") {
    goToFront();
    Serial.println("complete");
  } else if (in == "goToBack") {
    goToBack();
    Serial.println("complete");
  } else if (in.startsWith("moveToStep")) {
    blinkLED(2);
    moveToStep( toLong(in.substring(10)));
    blinkLED(2);
    Serial.println(stepsFromBack);
  } else if (in == "figureCurrentPosition") {
    stepsFromBack = figureCurrentPosition();
  } else if (in.startsWith("setTotalSteps")) {
    setTotalSteps( toLong(in.substring(13)));
    Serial.println("complete");
  } else if (in.startsWith("setStepsFromBack")) {
    setStepsFromBack( toLong(in.substring(16)));
    Serial.println("complete");
  } else if (in.startsWith("setStepsFromFront")) {
    setStepsFromFront( toLong(in.substring(17)));
    Serial.println("complete");
  }else if (in.startsWith("setStepDelay")) {
    setStepDelay( toLong(in.substring(12)));
    Serial.println("complete");
  }
  else if ( in == "getStepsFromFront") {
    Serial.println(stepsFromFront);
  } else if ( in == "getStepsFromBack") {
    Serial.println(stepsFromBack);
  } else if ( in == "getTotalSteps") {
    Serial.println(totalSteps);
  }
}
long figureCurrentPosition() {
  long stepCount = 0;
  setDirection(0);
  while (checkStops() != stopPinBack) {
    takeAStep();
    stepCount++;
  }

  moveToStep(stepCount);
  isPositionKnown = true;
  stepsFromBack = stepCount;
  Serial.println(stepCount);
  return stepCount;
}

void moveToStep(long target) {
  bool broke = false;

  //purge Serial
  while (Serial.available()) {
    Serial.read();
  }

  String mess;
  bool dir = 1;
  if (isPositionKnown) {
    long dis = target - stepsFromBack;
    if (dis < 0) {
      setDirection(0);
      dir = 0;
    } else {
      setDirection(1);
      dir = 1;
    }

    stepsFromBack += dis;
    stepsFromFront = totalSteps - stepsFromBack;
    dis = abs(dis);


    while (dis) {
      mess = checkSerial();
      if (mess != "0") {
        broke = true;
        break;
      }
      //need check appropriate stop here
      /*
      if (checkStop(dir)) {
        break;
      }
      */
      takeAStep();
      dis--;
    }


    //if move interrupted, figure position
    if (broke) {
      stepsFromBack -= dis;
      stepsFromFront = totalSteps - stepsFromBack;
      evalSerial(mess);
    }

    //    Serial.println(stepsFromBack);

  } else {
    Serial.println("error: position unknown");
  }
}



void goToFront() {
  setDirection(1);

  while (checkStops() != stopPinFront) {
    takeAStep();
  }
  isPositionKnown = true;
  stepsFromFront = 0;
  stepsFromBack = totalSteps;
}
void goToBack() {
  setDirection(0);

  while (checkStops() != stopPinBack) {
    takeAStep();
  }
  isPositionKnown = true;
  stepsFromBack = 0;
  stepsFromFront = totalSteps;
}

int checkStops() {
  if (digitalRead(stopPinFront)) {
    isPositionKnown = true;
    stepsFromFront = 0;
    stepsFromBack = totalSteps;
    return stopPinFront;
  } else if (digitalRead(stopPinBack)) {
    isPositionKnown = true;
    stepsFromBack = 0;
    stepsFromFront = totalSteps;
    return stopPinBack;
  } else {
    return 0;
  }
}

bool checkStop(bool front) {
  if (front) {
    if (digitalRead(stopPinFront)) {
      isPositionKnown = true;
      stepsFromFront = 0;
      stepsFromBack = totalSteps;
      return true;
    } else {
      return false;
    }
  } else {
    if (digitalRead(stopPinBack)) {
      isPositionKnown = true;
      stepsFromFront = totalSteps;
      stepsFromBack = 0;
      return true;
    } else {
      return false;
    }
  }
}

void changeDirection() {
  digitalWrite(dirP, !digitalRead(dirP));
  digitalWrite(dirN, !digitalRead(dirN));
}


void takeAStep() {

  //digitalWrite(led, HIGH);
  digitalWrite(stepPinP, !digitalRead(stepPinP));
  digitalWrite(stepPinN, !digitalRead(stepPinN));
  delayMicroseconds(stepDelay);
  //digitalWrite(led, LOW);
  digitalWrite(stepPinP, !digitalRead(stepPinP));
  digitalWrite(stepPinN, !digitalRead(stepPinN));
  //delayMicroseconds(stepDelay);
}


long calibrateSteps() {
  goToBack();
  //Serial.println("at back");
  delay(1000);
  long stepCount = 0;
  setDirection(1);
  while (checkStops() != stopPinFront) {
    takeAStep();
    stepCount++;
  }
  //Serial.println(stepCount);
  delay(1000);
  setDirection(0);
  while (checkStops() != stopPinBack) {
    takeAStep();
    stepCount++;
  }
  //Serial.println(stepCount);

  delay(1000);
  isPositionKnown = true;
  stepsFromFront = stepCount / 2;
  stepsFromBack = 0;
  return long(stepCount / 2);
}

long toLong(String str) {
  char buffer[20];          // Buffer to hold the string for conversion
  str.toCharArray(buffer, sizeof(buffer)); // Convert String to char array

  long num = strtol(buffer, NULL, 10);
  return num;

}

void setStepDelay(int ms){
  stepDelay = ms;
}

void setTotalSteps(long num) {
  totalSteps = num;
}
void setStepsFromBack(long num) {
  stepsFromBack = num;
  if (totalSteps) {
    stepsFromFront = totalSteps - num;
  }
  isPositionKnown = true;
}
void setStepsFromFront(long num) {
  stepsFromFront = num;
  if (totalSteps) {
    stepsFromBack = totalSteps - num;
  }
  isPositionKnown = true;
}

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(led, HIGH);
    delay(200);
    digitalWrite(led, LOW);
    delay(200);
  }
}

void setDirection(bool forward) {
  if (forward) {
    digitalWrite(dirP, HIGH);
    digitalWrite(dirN, LOW);
  } else {
    digitalWrite(dirP, LOW);
    digitalWrite(dirN, HIGH);
  }
}
