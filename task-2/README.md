# Task 2: Real-Time Chat Application with WebSockets

## Overview

A multi-room chat server built with WebSockets, supporting real-time messaging, private messages, typing indicators, and user presence tracking with persistent message storage.

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python chat_server.py
```

You should see:

```
[INFO] Chat server started on ws://0.0.0.0:8765
```

### 4. Open the Client

- **Option 1**: Serve locally using Python

  ```bash
  python -m http.server 8000 -d client
  ```

  Then open `http://localhost:8000` in your browser

- **Option 2**: Open `client/index.html` directly in your browser

## Features

### Chat Rooms

- Join/create chat rooms (e.g., #general, #random)
- See all members in a room
- View message history (last 50 messages from room)
- Real-time member list updates

### Direct Messages

- Send private messages to other users
- DM history persists
- Notifications when users send DMs

### Typing Indicators

- Real-time "user is typing..." indicator
- Auto-clears after 5 seconds of inactivity

### User Presence

- **Online** (green) – actively using chat
- **Away** (yellow) – idle for 30+ seconds
- **Offline** (gray) – disconnected

### Message Persistence

- All messages stored in SQLite database
- Automatic history loading on join
- Search through message history

## Testing Checklist

- [ ] Open two browser windows with different usernames
- [ ] Send messages in #general and see them in real-time
- [ ] Try sending a private message
- [ ] Watch typing indicators appear and disappear
- [ ] Change your status to "Away" and see indicator update
- [ ] Refresh browser and see message history persists
- [ ] Create a new room and verify room list updates

## Project Structure

```
task-2/
├── README.md              # This file
├── TECHNICAL_GUIDE.md     # Architecture details
├── requirements.txt       # Dependencies
├── chat_server.py         # WebSocket server
├── client/
│   ├── index.html        # Chat UI
│   └── chat.js           # Client-side logic
└── data/
    └── messages.db       # SQLite database (auto-created)
```

## WebSocket Message Protocol

All messages are JSON format:

### Client → Server

- `{"type": "join_room", "room": "#general"}`
- `{"type": "message", "room": "#general", "text": "Hello!"}`
- `{"type": "dm", "to": "alice", "text": "Hi Alice!"}`
- `{"type": "typing", "room": "#general"}`
- `{"type": "status", "status": "away"}`
- `{"type": "get_history", "room": "#general"}`

### Server → Clients

- `{"type": "join_notification", "user": "alice", "room": "#general"}`
- `{"type": "message", "user": "bob", "text": "Hello!", "timestamp": "14:32:01", "room": "#general"}`
- `{"type": "dm", "from": "bob", "text": "Hi!", "timestamp": "14:32:05"}`
- `{"type": "typing", "user": "alice", "room": "#general"}`
- `{"type": "members", "room": "#general", "members": [{"name": "alice", "status": "online"}, ...]}`
- `{"type": "history", "messages": [...]}`

## Common Issues

**Q: Server won't start**

- Check port 8765 is not in use: `netstat -an | grep 8765`
- Try different port: Modify `asyncio.run(main())` in chat_server.py

**Q: Can't connect from browser**

- Ensure server is running: `python chat_server.py`
- Check firewall settings
- Verify WebSocket URL is correct: `ws://localhost:8765`

**Q: Messages not persisting**

- Ensure `data/` directory exists
- Check SQLite installation: `python -c "import sqlite3; print(sqlite3.version)"`
