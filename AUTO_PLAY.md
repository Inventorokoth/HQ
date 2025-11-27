# Auto-Play Timeout Feature

## Overview

The Music Stream Player now includes an intelligent auto-play feature that automatically selects and plays the first search result if you don't make a selection within 5 seconds.

## How It Works

When you search for music using the `play` command:

1. **Search Results Displayed**: The app shows 5 search results with titles and durations
2. **Auto-Select Countdown**: The prompt shows "Auto-selecting first result in 5 seconds..."
3. **User Options**:
   - **Enter a number (1-5)** within 5 seconds to select that result
   - **Enter 'c'** to cancel the search
   - **Do nothing** and wait 5 seconds - the first result will auto-select

## Examples

### Example 1: Auto-Select (Wait for Timeout)

```
🎵 > play sia cheap thrills
🔍 Searching for: sia cheap thrills

📋 Search Results:
1. Sia - Cheap Thrills (Official Video) (3:31)
2. Sia - Cheap Thrills (Alternative version) (4:12)
3. Cheap Thrills - Remix Collection (5:45)
4. Sia Cheap Thrills Lyrics (3:31)
5. Cheap Thrills Dance Cover (4:02)

⏱️  Auto-selecting first result in 5 seconds...
🎯 Select track (1-5) or 'c' to cancel: 

⏰ Auto-selecting: #1
🔄 Getting audio stream...
📥 Downloading audio to cache...
🎶 Now playing: Sia - Cheap Thrills (Official Video)
```

### Example 2: Manual Selection

```
🎵 > play rock music
🔍 Searching for: rock music

📋 Search Results:
1. Queen - Bohemian Rhapsody (5:55)
2. Led Zeppelin - Whole Lotta Love (5:33)
3. AC/DC - Back in Black (4:15)
4. Pink Floyd - Wish You Were Here (5:34)
5. The Who - My Generation (3:34)

⏱️  Auto-selecting first result in 5 seconds...
🎯 Select track (1-5) or 'c' to cancel: 3

🔄 Getting audio stream...
🎶 Now playing: AC/DC - Back in Black
```

### Example 3: Cancel Search

```
🎵 > play jazz

📋 Search Results:
[Results shown...]

⏱️  Auto-selecting first result in 5 seconds...
🎯 Select track (1-5) or 'c' to cancel: c

❌ Cancelled
🎵 > 
```

## Technical Details

- **Timeout Duration**: 5 seconds
- **Implementation**: Uses `select.select()` for non-blocking input on Unix/Linux
- **Fallback**: On Windows or if select fails, defaults to auto-selecting result #1
- **Default Selection**: Result #1 (the most relevant/popular result according to YouTube search)

## Use Cases

1. **Quick Playlist Creation**: Say "play [song]" and let the first result auto-play
2. **Hands-Free Operation**: Combined with voice commands, you don't need to interact with the app at all
3. **Lazy Browsing**: Let it play while you consider other options

## Interaction with Voice Commands

The auto-play feature works seamlessly with voice commands:

```
🎵 > voice
🎤 Listening... (speak now)
# You say: "play black mirror"
✓ Recognized: play black mirror
📝 Executing: play black mirror
🔍 Searching for: black mirror

📋 Search Results:
[Results shown...]

⏰ Auto-selecting: #1
🎶 Now playing: [First result]
```

Perfect for a completely hands-free experience!
