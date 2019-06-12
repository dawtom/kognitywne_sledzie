# Move-Play

This program enable translate moving any green object to music.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Project require Python version 3.6.

| Library       | Version       | Usage                           |
| ------------- | ------------- | -------------                   |
| PyAudio       | 0.2.11        | Play sounds                     |
| opencv-python | 4.0.0.21      | Track move in live wideo        |
| numpy         | 1.15.0        | Basic math functions            |
| imutils       | 0.5.2         | To make basic image processing  |



### Installing

Use pip install command to install all required prerequisities described above.

```
pip install PyAudio
```

### Run program
To run application run class move_play.py.

## Application Description

### Objectives
Initially, we wanted to make an application, which enable moving mouse using any colorful object.
We did not have any ideas how to make this useful.

Then, we decided to make a toy, application which enables playing the sound using colorful object and provides the opportunity to change the amplitude of the sound (volume) and the frequency of the sound (sound pitch).

### Methodology
1. Image recognition using opencv-python
2. Playing sounds using initially audiogen library, finally pyaudio
3. Playing sounds depends on image recognition - merge step 1 and 2
4. Testing by piano players and amateurs

### Evaluation
Move & Play was tested by one beginner player, two intermediate player and one advance player.
Each player tried to play simple melody.

Nice toy
Image recognition does not work ideally
Image recognition working depends on the lights, the day time

### Discussion
Toy was generally approved

Some proposition to improve:
There should be possibility to stop playing the sound and manipulate the durability of the sound.

Proposal changes:
Green object turn on the sound
Another colorful object turn off the sound
Sound lasting until you turn off them
Therefore, it would be easier to play something interesting.



## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
