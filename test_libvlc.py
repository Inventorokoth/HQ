#!/usr/bin/env python3
"""
Standalone libVLC test script.
Tests basic libVLC functionality: playback, volume, pause, resume, seek, status.
Does NOT depend on the music_player app.

Usage:
    python test_libvlc.py              # Interactive menu
    python test_libvlc.py <file_path>  # Play a specific file
"""

import vlc
import time
import sys
import os


def print_menu():
    """Print interactive menu."""
    print("\n" + "="*50)
    print("libVLC Test Menu")
    print("="*50)
    print("Commands:")
    print("  p          - Play/Resume")
    print("  s          - Stop")
    print("  pause      - Pause")
    print("  volume <0-100>  - Set volume")
    print("  seek <0.0-1.0>  - Seek to position (0.0=start, 1.0=end)")
    print("  status     - Show player status")
    print("  help       - Show this menu")
    print("  quit       - Exit")
    print("="*50)


def print_status(player):
    """Print current player status."""
    is_playing = player.is_playing()
    state = player.get_state()
    position = player.get_position()
    duration = player.get_length() / 1000.0 if player.get_length() > 0 else 0
    volume = player.audio_get_volume()
    media = player.get_media()
    title = media.get_mrl() if media else "None"

    print(f"\n--- Player Status ---")
    print(f"State:       {state}")
    print(f"Is Playing: {is_playing}")
    print(f"Position:   {position:.2f} ({position*100:.1f}%)")
    print(f"Duration:   {duration:.1f} seconds")
    print(f"Volume:     {volume}%")
    print(f"Media:      {title}")
    print("--------------------\n")


def test_local_file(file_path):
    """Test playback of a local file."""
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return

    print(f"\nTesting local file: {file_path}")
    print("="*50)

    # Create VLC instance with explicit audio output
    print("1. Creating VLC instance...")
    instance = vlc.Instance("--no-video", "--aout=pulse")
    print("   ✓ Instance created (audio output: pulseaudio)")

    # Create player
    print("2. Creating media player...")
    player = instance.media_player_new()
    print("   ✓ Player created")

    # Load media
    print("3. Loading media...")
    media = instance.media_new(file_path)
    player.set_media(media)
    print("   ✓ Media loaded")

    # Start playback
    print("4. Starting playback...")
    player.play()
    time.sleep(1)
    print("   ✓ Playback started")

    # Monitor playback
    print("5. Monitoring playback for 20 seconds...")
    for i in range(40):
        time.sleep(0.5)
        if player.is_playing():
            pos = player.get_position()
            dur = player.get_length() / 1000.0
            if i % 4 == 0:  # Print every 2 seconds
                print(f"   [{i*0.5:>4.1f}s] Playing: {pos*100:>5.1f}% ({pos*dur:>5.1f}s / {dur:>5.1f}s)")
        else:
            print(f"   [{i*0.5:.1f}s] Playback ended or paused")
            break

    # Stop
    player.stop()
    print("6. Playback stopped")
    print("="*50)


def test_url(url):
    """Test playback of a remote URL."""
    print(f"\nTesting remote URL: {url}")
    print("="*50)

    # Create VLC instance with explicit audio output
    print("1. Creating VLC instance...")
    instance = vlc.Instance("--no-video", "--aout=pulse")
    print("   ✓ Instance created (audio output: pulseaudio)")

    # Create player
    print("2. Creating media player...")
    player = instance.media_player_new()
    print("   ✓ Player created")

    # Load media with HTTP options
    print("3. Loading media from URL...")
    media = instance.media_new(url, ":http-user-agent=Mozilla/5.0")
    player.set_media(media)
    print("   ✓ Media loaded")

    # Start playback
    print("4. Starting playback...")
    player.play()
    time.sleep(1)
    print("   ✓ Playback started")

    # Monitor playback
    print("5. Monitoring playback for 20 seconds...")
    for i in range(40):
        time.sleep(0.5)
        if player.is_playing():
            pos = player.get_position()
            dur = player.get_length() / 1000.0
            if i % 4 == 0:  # Print every 2 seconds
                print(f"   [{i*0.5:>4.1f}s] Playing: {pos*100:>5.1f}%")
        else:
            print(f"   [{i*0.5:.1f}s] Playback ended or paused")
            break

    # Stop
    player.stop()
    print("6. Playback stopped")
    print("="*50)


def interactive_mode():
    """Interactive test mode."""
    print("\n" + "="*50)
    print("libVLC Interactive Test")
    print("="*50)

    # Get file or URL from user
    file_or_url = input("\nEnter file path or URL to play: ").strip()
    if not file_or_url:
        print("No input provided")
        return

    print("\nInitializing VLC...")
    instance = vlc.Instance("--no-video", "--aout=pulse")
    player = instance.media_player_new()

    media = instance.media_new(file_or_url)
    player.set_media(media)

    print_menu()

    # Main loop
    while True:
        try:
            cmd = input("vlc> ").strip().lower()

            if not cmd:
                continue

            if cmd == "quit" or cmd == "exit":
                print("Stopping playback...")
                player.stop()
                print("Goodbye!")
                break

            elif cmd == "p":
                if player.is_playing():
                    print("Resuming playback...")
                    player.play()
                else:
                    print("Starting playback...")
                    player.play()

            elif cmd == "s":
                print("Stopping playback...")
                player.stop()

            elif cmd == "pause":
                print("Pausing playback...")
                player.pause()

            elif cmd.startswith("volume"):
                try:
                    parts = cmd.split()
                    if len(parts) > 1:
                        vol = int(parts[1])
                        vol = max(0, min(vol, 100))
                        player.audio_set_volume(vol)
                        print(f"Volume set to {vol}%")
                    else:
                        print(f"Current volume: {player.audio_get_volume()}%")
                except ValueError:
                    print("ERROR: Volume must be a number 0-100")

            elif cmd.startswith("seek"):
                try:
                    parts = cmd.split()
                    if len(parts) > 1:
                        pos = float(parts[1])
                        pos = max(0.0, min(pos, 1.0))
                        player.set_position(pos)
                        print(f"Seeked to {pos*100:.1f}%")
                    else:
                        print("ERROR: seek <position> (0.0-1.0)")
                except ValueError:
                    print("ERROR: Position must be a float 0.0-1.0")

            elif cmd == "status":
                print_status(player)

            elif cmd == "help":
                print_menu()

            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for menu")

        except KeyboardInterrupt:
            print("\n\nInterrupted")
            player.stop()
            break
        except Exception as e:
            print(f"ERROR: {e}")


def main():
    """Main entry point."""
    print("\n" + "="*50)
    print("libVLC Test Script")
    print("="*50)

    # Check if libVLC is available
    try:
        print(f"VLC Version: {vlc.__version__}")
        print(f"libVLC Version: {vlc.libvlc_get_version()}")
    except Exception as e:
        print(f"ERROR: libVLC not available: {e}")
        return 1

    # Parse command line arguments
    if len(sys.argv) > 1:
        file_or_url = sys.argv[1]

        # Test local file or URL
        if file_or_url.startswith("http://") or file_or_url.startswith("https://"):
            test_url(file_or_url)
        else:
            test_local_file(file_or_url)
    else:
        # Interactive mode
        interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
