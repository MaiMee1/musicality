# musicality
## Description
A _beginner_ python music/rhythm game school project. Inspired partly by those of the same kind, but 
with a twist. (Sadly not fully completed.) Project is currently suspended indefinitely.

## Requirements
`python 3.6`+ (code has variable annotations and 'F' prefix)
 (might be edited out in the future, but not currently)

libraries:
- `arcade (2.0.0+)`
- `pyglet (1.3.7+)`

Codec Decoder:
- `FFmpeg` [Get it here](https://ffmpeg.org/download.html)
- `AVbin` (requirement of pyglet's sound library)

System Requirements:
- currently might not work with __mac OS__ (sound/codec problems).
As the repository owner does not use mac OS, the game is not tested in mac OS and 
he is not able to debug/provide you with much help regarding this problem currently
- might lag somewhat if you're on your laptop's __battery__. (The repository owner is only 
getting started with GUI and cannot overcome the current limitations yet.)

## Information
### Installation
clone this repository somewhere
### Playing
Run `init.py` which is directly inside the repository (path should be `musicality/init.py`).
Game should take some time to load the beatmap but not too long.

### Adding more songs
There are some songs already included in this repository but you can add more if you want, as the game
 will process any .osu files inside the folder.
 
1. Get new songs from Osu! by going to its [website](https://osu.ppy.sh) and downloading a beatmap.
(You need an Osu! account in order to download a beatmap and the game in order to process .osz file)
2. Copy the beatmap's song folder (usually in `C:\Users\[Your username]\AppData\Local\osu!\Songs`) and 
paste the folder in `musicality/resources/Songs`. (Just make things look like it already looks and it 
should be OK. Things should go where they look like they should go.)
 
## FAQ
Q. Game doesn't run?\
A. Try running from the terminal or an IDE. Running by opening the `init.py` 
file directly doesn't always work.

Q. It still doesn't run.\
A. Check the requirements and see if you meet it. If you already have, I also don't know why 
you can't play the game.

Q. How do I play the song?\
A. This is my fault for rushing but, if you go into Start and select a song, 
when you hover over the song it says "press Enter to play". You can then press 'P' to start the game.

Q. How do I play?\
A. Again, this is my fault for not making a good tutorial but... It is like other rhythm games.
Maybe you can play them before you play this one.

Q. Will there be updates?\
A. If I feel like it. ~~I'm currently busy with other things, but when I'm done, I might make an easier
GUI library to use as a basis for this game and other programs I might make from python. But I also might
not do it because I'm not sure why you would use python for GUI. (And also because OpenGL4.0 which is the
basis of pyglet—the library this game uses—is being depreciated in favour of Vulcan, or so I've heard.)~~
This is a school projcet that I'm already done with.
I'm not a game designer and so I don't really feel like trying to make a game enjoyable, but if it 
already is and you really enjoy playing it, or have some ideas about ways to improve it so that it can be
enjoyable enough for you/other people to play it regularly enough, contact me. (I'll think about how later.)

Q. Is this project dead?\
A. No, not yet (as of 2019). I'll call it a temporary hiatus.
