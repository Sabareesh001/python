import asyncio
import json
import sqlite3
import os
import time
from datetime import datetime
from pathlib import Path
import websockets
from websockets.server import WebSocketServerProtocol


# ============================================================================
# Database Setup
# ============================================================================

class ChatDatabase:
    """SQLite database for message persistence."""
    
    def __init__(self, db_path="data/messages.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._init_db()
      
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Room messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                user TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Direct messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dm_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user TEXT NOT NULL,
                to_user TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                status TEXT DEFAULT 'online',
                last_seen TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_message(self, room, user, text):
        """Save a room message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (room, user, text, timestamp) VALUES (?, ?, ?, ?)",
            (room, user, text, timestamp)
        )
        conn.commit()
        conn.close()
    
    def save_dm(self, from_user, to_user, text):
        """Save a direct message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dm_messages (from_user, to_user, text, timestamp) VALUES (?, ?, ?, ?)",
            (from_user, to_user, text, timestamp)
        )
        conn.commit()
        conn.close()
    
    def get_room_history(self, room, limit=50):
        """Retrieve recent messages from a room."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user, text, timestamp FROM messages WHERE room = ? ORDER BY id DESC LIMIT ?",
            (room, limit)
        )
        messages = [
            {"user": row[0], "text": row[1], "timestamp": row[2]}
            for row in reversed(cursor.fetchall())
        ]
        conn.close()
        return messages
    
    def get_dm_history(self, user1, user2, limit=50):
        """Retrieve DM history between two users."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT from_user, text, timestamp FROM dm_messages
            WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
            ORDER BY id DESC LIMIT ?
        """, (user1, user2, user2, user1, limit))
        messages = [
            {"from": row[0], "text": row[1], "timestamp": row[2]}
            for row in reversed(cursor.fetchall())
        ]
        conn.close()
        return messages
    
    def update_user_status(self, username, status):
        """Update user status."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (username, status, last_seen) VALUES (?, ?, ?)",
            (username, status, timestamp)
        )
        conn.commit()
        conn.close()


# ============================================================================
# Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages all active WebSocket connections."""
    
    def __init__(self):
        # rooms: {room_name: [connection1, connection2, ...]}
        self.rooms = {}
        # connections: {connection: {"username": str, "status": str, "rooms": [rooms], "last_activity": datetime}}
        self.connections = {}
    
    def register_connection(self, connection, username):
        """Register a new connection."""
        self.connections[connection] = {
            "username": username,
            "status": "online",
            "rooms": [],
            "last_activity": datetime.now(),
            "last_typing_time": {}  # Track last typing time per room
        }
        log(f"User '{username}' connected")
    
    def unregister_connection(self, connection):
        """Unregister a connection."""
        if connection in self.connections:
            username = self.connections[connection]["username"]
            rooms = self.connections[connection]["rooms"][:]
            del self.connections[connection]
            log(f"User '{username}' disconnected")
            return username, rooms
        return None, []
    
    def join_room(self, connection, room):
        """Add connection to a room."""
        if room not in self.rooms:
            self.rooms[room] = []
        
        if connection not in self.rooms[room]:
            self.rooms[room].append(connection)
            self.connections[connection]["rooms"].append(room)
            return True
        return False
    
    def leave_room(self, connection, room):
        """Remove connection from a room."""
        if room in self.rooms and connection in self.rooms[room]:
            self.rooms[room].remove(connection)
            if room in self.connections[connection]["rooms"]:
                self.connections[connection]["rooms"].remove(room)
            
            # Delete empty rooms
            if not self.rooms[room]:
                del self.rooms[room]
            return True
        return False
    
    def get_room_members(self, room):
        """Get all members in a room with their statuses."""
        if room not in self.rooms:
            return []
        
        members = []
        for conn in self.rooms[room]:
            if conn in self.connections:
                members.append({
                    "name": self.connections[conn]["username"],
                    "status": self.connections[conn]["status"]
                })
        return members
    
    async def broadcast_to_room(self, room, message, exclude_connection=None):
        """Send message to all users in a room."""
        if room not in self.rooms:
            return
        
        for conn in self.rooms[room]:
            if conn != exclude_connection:
                try:
                    await conn.send(json.dumps(message))
                except Exception as e:
                    log(f"Error broadcasting to room {room}: {e}")
    
    async def send_to_user(self, username, message):
        """Send a direct message to a specific user."""
        for conn, info in self.connections.items():
            if info["username"] == username:
                try:
                    await conn.send(json.dumps(message))
                    return True
                except Exception as e:
                    log(f"Error sending to user {username}: {e}")
                    return False
        return False
    
    def get_all_rooms(self):
        """Get list of all active rooms."""
        return list(self.rooms.keys())
    
    def update_last_activity(self, connection):
        """Update last activity timestamp."""
        if connection in self.connections:
            self.connections[connection]["last_activity"] = datetime.now()
    
    def get_user_status(self, connection):
        """Get user's current status."""
        if connection in self.connections:
            return self.connections[connection]["status"]
        return None


# ============================================================================
# Logging
# ============================================================================

def log(message):
    """Simple logging function."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


# ============================================================================
# Global State
# ============================================================================

db = ChatDatabase()
manager = ConnectionManager()


# ============================================================================
# Message Handlers
# ============================================================================

async def handle_join_room(connection, room):
    """Handle user joining a room."""
    username = manager.connections[connection]["username"]
    
    # Add to room
    if manager.join_room(connection, room):
        log(f"User '{username}' joined room {room}")
        
        # Broadcast join notification
        await manager.broadcast_to_room(room, {
            "type": "join_notification",
            "user": username,
            "room": room
        })
        
        # Send room member list
        members = manager.get_room_members(room)
        await connection.send(json.dumps({
            "type": "members",
            "room": room,
            "members": members
        }))
        
        # Send message history
        history = db.get_room_history(room)
        await connection.send(json.dumps({
            "type": "history",
            "room": room,
            "messages": history
        }))


async def handle_message(connection, room, text):
    """Handle room message."""
    username = manager.connections[connection]["username"]
    
    # Save to database
    db.save_message(room, username, text)
    
    # Broadcast to room
    timestamp = datetime.now().strftime("%H:%M:%S")
    await manager.broadcast_to_room(room, {
        "type": "message",
        "user": username,
        "text": text,
        "timestamp": timestamp,
        "room": room
    })


async def handle_dm(connection, to_user, text):
    """Handle direct message."""
    from_user = manager.connections[connection]["username"]
    
    # Save to database
    db.save_dm(from_user, to_user, text)
    
    # Send to user
    timestamp = datetime.now().strftime("%H:%M:%S")
    await manager.send_to_user(to_user, {
        "type": "dm",
        "from": from_user,
        "text": text,
        "timestamp": timestamp
    })


async def handle_typing(connection, room):
    """Handle typing indicator."""
    username = manager.connections[connection]["username"]
    current_time = time.time()
    last_typing_time = manager.connections[connection]["last_typing_time"].get(room, 0)
    
    # Only broadcast if 5 seconds have passed since last typing indicator
    if current_time - last_typing_time >= 5:
        manager.connections[connection]["last_typing_time"][room] = current_time
        
        # Broadcast typing indicator (exclude sender)
        await manager.broadcast_to_room(room, {
            "type": "typing",
            "user": username,
            "room": room
        }, exclude_connection=connection)


async def handle_status_change(connection, status):
    """Handle user status change."""
    username = manager.connections[connection]["username"]
    manager.connections[connection]["status"] = status
    
    # Update database
    db.update_user_status(username, status)
    
    # Broadcast to all rooms user is in
    for room in manager.connections[connection]["rooms"]:
        members = manager.get_room_members(room)
        await manager.broadcast_to_room(room, {
            "type": "members",
            "room": room,
            "members": members
        })


async def handle_get_history(connection, room):
    """Send message history for a room."""
    history = db.get_room_history(room)
    await connection.send(json.dumps({
        "type": "history",
        "room": room,
        "messages": history
    }))


# ============================================================================
# Main Message Handler
# ============================================================================

async def handle_client_message(websocket: WebSocketServerProtocol, path):
    """Main WebSocket connection handler."""
    
    # Get username from first message
    try:
        msg = await websocket.recv()
        data = json.loads(msg)
        
        if data.get("type") != "init":
            await websocket.send(json.dumps({"error": "First message must be init"}))
            return
        
        username = data.get("username", f"user_{id(websocket) % 10000}")
        manager.register_connection(websocket, username)
        
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "init_response",
            "username": username,
            "rooms": manager.get_all_rooms()
        }))
        
    except Exception as e:
        log(f"Error during init: {e}")
        return
    
    # Main message loop
    try:
        async for msg in websocket:
            try:
                data = json.loads(msg)
                msg_type = data.get("type")
                
                manager.update_last_activity(websocket)
                
                # Route message by type
                if msg_type == "join_room":
                    await handle_join_room(websocket, data.get("room"))
                
                elif msg_type == "leave_room":
                    room = data.get("room")
                    username = manager.connections[websocket]["username"]
                    if manager.leave_room(websocket, room):
                        log(f"User '{username}' left room {room}")
                        members = manager.get_room_members(room)
                        await manager.broadcast_to_room(room, {
                            "type": "members",
                            "room": room,
                            "members": members
                        })
                
                elif msg_type == "message":
                    await handle_message(
                        websocket,
                        data.get("room"),
                        data.get("text")
                    )
                
                elif msg_type == "dm":
                    await handle_dm(
                        websocket,
                        data.get("to"),
                        data.get("text")
                    )
                
                elif msg_type == "typing":
                    await handle_typing(websocket, data.get("room"))
                
                elif msg_type == "status":
                    await handle_status_change(websocket, data.get("status"))
                
                elif msg_type == "get_history":
                    await handle_get_history(websocket, data.get("room"))
                
                elif msg_type == "get_rooms":
                    await websocket.send(json.dumps({
                        "type": "rooms",
                        "rooms": manager.get_all_rooms()
                    }))
            
            except json.JSONDecodeError:
                log(f"Invalid JSON from {manager.connections.get(websocket, {}).get('username', 'unknown')}")
            except Exception as e:
                log(f"Error processing message: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        pass
    
    finally:
        # Cleanup
        username, rooms = manager.unregister_connection(websocket)
        
        if username:
            # Notify rooms of leave
            for room in rooms:
                members = manager.get_room_members(room)
                await manager.broadcast_to_room(room, {
                    "type": "members",
                    "room": room,
                    "members": members
                })


# ============================================================================
# Server Startup
# ============================================================================

async def main():
    """Start the WebSocket server."""
    # Ensure #general room exists
    manager.join_room = lambda *args, **kwargs: None  # Dummy
    if "#general" not in manager.rooms:
        manager.rooms["#general"] = []
    manager.join_room = ConnectionManager.join_room.__get__(manager, ConnectionManager)
    
    # Start server
    server = await websockets.serve(
        handle_client_message,
        "0.0.0.0",
        8765
    )
    
    log("Chat server started on ws://0.0.0.0:8765")
    log("Press Ctrl+C to stop")
    
    # Run forever
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped")
