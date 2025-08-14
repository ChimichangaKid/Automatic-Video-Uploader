# Taquitobot - Discord Bot To Make YouTube Shorts

GitHub codebase for a personal discord bot to play music and upload automated YouTube Shorts.

##### Version 1.2.2 
##### Last updated 2025-08-13

## Commands
Commands are followed by a "$" prefix


### Music Commands
#### Play (aliases 'p', 'P') Args: song_name
Queues a song to be played on the bot next, if no songs are playing immediately play the queued song. Songs queued are played in a FIFO order.

#### Pause
Pauses the current track if the track is playing otherwise resume the track.

#### Leave (aliases 'disconnect', 'l', 'L')
Disconnects the bot from the current discord channel if possible.

#### Skip (aliases 's', 'S')
Skips the current song that is playing and plays the next song in queue if possible.

#### Queue (aliases 'q', 'Q')
Shows the current songs that are in queue.

#### Remove (aliases 'r', 'R') Args: index
Removes the song in the queue at the specified index.

### League Commands
#### Chest (aliases 'c', 'C') Args: username, champion
Command to request if a champion mastery chest is available in League of Legends by Riot Games. Checks if the specified user can obtain a chest on the specified champion.

#### OPGG (aliases 'op') Args: username(s)
Command that will generate an opgg link for the specified usernames. Takes any amount of usernames separated by spaces. 

## Additional Features

### Clip Capturing

The bot will automatically recognize clips from outplayed.tv and edit them. The editing consists of converting to 9:16 aspect ratio and adding audio synced to the highlight of the clip. The program will then upload videos to the YouTube account that is currently logged in.
