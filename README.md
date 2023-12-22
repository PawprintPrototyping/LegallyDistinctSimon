# LegallyDistinctSimon
A memory game of flashing lights and sounds that definitely isn't owned by Hasbro

> ℹ️ White is ground

## Serial Command Structure
The light component of Legally Distinct Simon is run by an ESP-WROOM-32 board programmed in the arduino style. The sketch is set to listen for serial commands from the main game computer (A raspberry pi 2 in our implementation), and light each pawbean appropriately. The command structure is as follows:

`Cmd_PawbeanIndex_RedValue_GreenValue_BlueValue`

EXAMPLE: `ON 1 100 200 300`

* *Cmd* _The command being issued. Currently only supports ON
* *PawbeanIndex* _The index of the pawbean to be affected. Beans are numbered left to right starting at 1. Setting the color for pawbean index 0 will affect all lights on the strip._
* *RedValue* _The amount of red to set, as a number from 0-255_
* *GreenValue* _The amount of green to set, as a number from 0-255_
* *BlueValue* _The amount of blue to set, as a number from 0-255_


