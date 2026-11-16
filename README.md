# Bob, the desk cat

![Bob's board](hardware/fab/bob-top.png)

## The story

Bob is a cat that I drew in my sketchbook. Further up he went into the Wispr Flow hiring challenge as the main character that introduces my portfolio for that challenge.

After the completion of the challenge I moved on to Hack Club's Fallen, which is like a hard hackathon lasting 2 months. You build the project by hand: no AI, no bot can help you. You record your time, you get your XP, and stuff like that.

## Why I'm building him

Bob, the bot named Bob, is my cat, my sketchbook inspiration. Why am I building him? The reason that I'm building Bob is that I could feel less lonely while coding and while doing things.

## What Bob can do

What Bob can do is this: he has a screen, a mic, a speaker, and 3 servos. When we touch Bob he acts like an ordinary cat. He yawns, sleeps, and wakes up. His mic, speaker, and servos are all connected.

## The board

The board that I'm using is the ESP32-S3, 73 mm x 62.5 mm, 38 parts, and USB-C. These are the parts that are going to be on the board. As for the checks there are 0 ERC errors, 0 DRC errors, and 0 unconnected things.

![Schematic](hardware/fab/bob-schematic.png)

## The hardest part

The next little bit of a bad story is that the USB D+ wire was a really tough one. That was the only single wire that I needed to connect in the entire schematic so that I could submit. As it was the last one, when I was going to connect it, there was no way. I had to reconnect so many wires, some of which I had to, and change the schematic design, replace parts, and stuff like that. It's been a really tough one until now.

## Cost and what's next

The cost of all the parts is about ₹2,600 as I'm from India. What's next is that I'm going to be submitting the online version of Bob for now: the schematic, the PCB design, the doc, and the readme. Then I have to order all the hardware parts that I need to build him so that we can move on more quickly and probably go design.

## How to use him

To start, plug Bob in with USB-C. He chirps "hello" and shows his face. When you pat his head, he half-shuts his eyes and rubs into your hand, his ears tilt and his tail sways. When you clap, he looks up and shakes his tail like he's a little angry or upset with you.

Alone for about 2 minutes, he falls asleep. A pat or a clap wakes him up.

Bob is my original idea of a cat from my sketchbook, which I drew. Status: the board and the code are done. Parts are going to be ordered after Fallen approves, and then I just have to build him for the Maker Faire in Shenzhen, China, which hopefully I get selected for.

## The shell

![Bob's shell: base tray + head](hardware/shell/bob-shell-assembly.png)

A base tray (81 × 70.5 × 25 mm) that the board screws onto with 3 M2.5 posts, with a USB-C slot, and a head on top with the round face window and two ear-servo slots. STEP files are in `hardware/shell/`.

Note: I got sick and was admitted to hospital right before the design deadline, so the shell (base + head), the firmware starter and parts of the PCB reroute were made with AI help (Claude). The idea, the drawing of Bob, the schematic and the board design are mine, and I'll tune and build everything myself.

## Files

- `hardware/` KiCad schematic and PCB
- `hardware/fab/` Gerbers for JLCPCB, BOM, parts positions, schematic PDF, board renders, board STEP
- `firmware/bob/` Bob's firmware (face, pat, clap, sleep)
- `bom.csv` shopping list
