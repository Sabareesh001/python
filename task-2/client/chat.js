// ============================================================================
// Chat Client - WebSocket Communication & UI Logic
// ============================================================================

// State
const chatState = {
  username: null,
  currentRoom: "#general",
  connected: false,
  status: "online",
  rooms: [],
  members: {},
  typingUsers: {},
  ws: null,
};

// UI Elements
const messageDisplay = document.getElementById("messageDisplay");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const chatTitle = document.getElementById("chatTitle");
const roomList = document.getElementById("roomList");
const memberList = document.getElementById("memberList");
const usernameDisplay = document.getElementById("usernameDisplay");
const statusBtn = document.getElementById("statusBtn");
const statusDropdown = document.getElementById("statusDropdown");
const dmBtn = document.getElementById("dmBtn");
const dmModal = document.getElementById("dmModal");
const dmClose = document.getElementById("dmClose");
const userSelectList = document.getElementById("userSelectList");

// Generate username
function generateUsername() {
  return `user_${Math.floor(Math.random() * 10000)
    .toString()
    .padStart(4, "0")}`;
}

// ============================================================================
// WebSocket Connection
// ============================================================================

function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.hostname}:8765`;

  chatState.ws = new WebSocket(wsUrl);

  chatState.ws.onopen = () => {
    chatState.connected = true;
    updateConnectionStatus();
    log(`Connected to server`);

    // Send init message with username
    sendToServer({
      type: "init",
      username: chatState.username,
    });

    // Join default room
    sendToServer({
      type: "join_room",
      room: chatState.currentRoom,
    });
  };

  chatState.ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      handleServerMessage(message);
    } catch (e) {
      log(`Error parsing message: ${e.message}`);
    }
  };

  chatState.ws.onerror = (error) => {
    log(`WebSocket error: ${error}`);
    chatState.connected = false;
    updateConnectionStatus();
  };

  chatState.ws.onclose = () => {
    chatState.connected = false;
    updateConnectionStatus();
    log(`Disconnected from server`);

    // Auto-reconnect after 3 seconds
    setTimeout(connectWebSocket, 3000);
  };
}

function sendToServer(message) {
  if (chatState.ws && chatState.connected) {
    chatState.ws.send(JSON.stringify(message));
  }
}

// ============================================================================
// Server Message Handlers
// ============================================================================

function handleServerMessage(message) {
  const type = message.type;

  switch (type) {
    case "init_response":
      handleInitResponse(message);
      break;
    case "message":
      handleRoomMessage(message);
      break;
    case "dm":
      handleDirectMessage(message);
      break;
    case "typing":
      handleTypingIndicator(message);
      break;
    case "members":
      handleMembersUpdate(message);
      break;
    case "history":
      handleMessageHistory(message);
      break;
    case "join_notification":
      handleJoinNotification(message);
      break;
    case "rooms":
      handleRoomsUpdate(message);
      break;
    default:
      console.log("Unknown message type:", type);
  }
}

function handleInitResponse(message) {
  chatState.rooms = message.rooms || ["#general"];
  updateRoomList();
  log(`Initialized as ${message.username}`);
}

function handleRoomMessage(message) {
  if (message.room !== chatState.currentRoom) {
    return; // Ignore messages from other rooms
  }

  displayMessage(message.user, message.text, message.timestamp, false);
}

function handleDirectMessage(message) {
  // Show DM notification in current chat
  displaySystemMessage(`[DM from ${message.from}]: ${message.text}`);
}

function handleTypingIndicator(message) {
  if (message.room !== chatState.currentRoom) {
    return;
  }

  const user = message.user;
  chatState.typingUsers[user] = true;

  // Show typing indicator
  updateTypingIndicators();

  // Auto-clear after 5 seconds
  setTimeout(() => {
    delete chatState.typingUsers[user];
    updateTypingIndicators();
  }, 5000);
}

function handleMembersUpdate(message) {
  if (message.room !== chatState.currentRoom) {
    return;
  }

  chatState.members[message.room] = message.members || [];
  updateMemberList();
}

function handleMessageHistory(message) {
  if (message.room !== chatState.currentRoom) {
    return;
  }

  // Clear current messages
  messageDisplay.innerHTML = "";

  // Display all history messages
  for (const msg of message.messages || []) {
    displayMessage(msg.user, msg.text, msg.timestamp, false);
  }
}

function handleJoinNotification(message) {
  if (message.room !== chatState.currentRoom) {
    return;
  }

  displaySystemMessage(`${message.user} joined the room`);
}

function handleRoomsUpdate(message) {
  chatState.rooms = message.rooms || [];
  updateRoomList();
}

// ============================================================================
// UI Display Functions
// ============================================================================

function displayMessage(user, text, timestamp, isOwn) {
  const messageEl = document.createElement("div");
  messageEl.className = "message";

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = user[0].toUpperCase();

  const content = document.createElement("div");
  content.className = "message-content";

  const header = document.createElement("div");
  header.className = "message-header";
  header.innerHTML = `
        <span class="message-user">${escapeHtml(user)}</span>
        <span class="message-time">${timestamp}</span>
    `;

  const textEl = document.createElement("div");
  textEl.className = `message-text ${isOwn ? "own" : ""}`;
  textEl.textContent = text;

  content.appendChild(header);
  content.appendChild(textEl);

  messageEl.appendChild(avatar);
  messageEl.appendChild(content);

  messageDisplay.appendChild(messageEl);
  messageDisplay.scrollTop = messageDisplay.scrollHeight;
}

function displaySystemMessage(text) {
  const messageEl = document.createElement("div");
  messageEl.className = "system-message";
  messageEl.textContent = text;

  messageDisplay.appendChild(messageEl);
  messageDisplay.scrollTop = messageDisplay.scrollHeight;
}

function updateMemberList() {
  memberList.innerHTML = "";

  const members = chatState.members[chatState.currentRoom] || [];

  for (const member of members) {
    const memberEl = document.createElement("div");
    memberEl.className = "member-item";

    const dot = document.createElement("span");
    dot.className = `status-dot ${member.status}`;

    const nameEl = document.createElement("span");
    nameEl.textContent = member.name;

    memberEl.appendChild(dot);
    memberEl.appendChild(nameEl);
    memberList.appendChild(memberEl);
  }
}

function updateRoomList() {
  roomList.innerHTML = "";

  for (const room of chatState.rooms) {
    const roomEl = document.createElement("li");
    roomEl.className = `room-item ${room === chatState.currentRoom ? "active" : ""}`;
    roomEl.setAttribute("data-room", room);

    const members = chatState.members[room] || [];
    roomEl.innerHTML = `
            ${room}
            <span class="room-badge">${members.length}</span>
        `;

    roomEl.addEventListener("click", () => switchRoom(room));
    roomList.appendChild(roomEl);
  }
}

function updateTypingIndicators() {
  // Remove existing typing indicator
  const existing = document.querySelector(".typing-indicator");
  if (existing) {
    existing.remove();
  }

  // Add new typing indicator if someone is typing
  const typingUsers = Object.keys(chatState.typingUsers);
  if (typingUsers.length > 0) {
    const typingEl = document.createElement("div");
    typingEl.className = "typing-indicator";
    typingEl.innerHTML = `
            ${typingUsers.join(", ")} is typing
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
    messageDisplay.appendChild(typingEl);
    messageDisplay.scrollTop = messageDisplay.scrollHeight;
  }
}

function updateConnectionStatus() {
  const indicator = document.querySelector(".status-indicator");
  if (chatState.connected) {
    indicator.style.background = "#4caf50";
  } else {
    indicator.style.background = "#f44336";
  }
}

// ============================================================================
// Room & Messaging Functions
// ============================================================================

function switchRoom(room) {
  // Leave current room
  if (chatState.currentRoom) {
    sendToServer({
      type: "leave_room",
      room: chatState.currentRoom,
    });
  }

  // Join new room
  chatState.currentRoom = room;
  sendToServer({
    type: "join_room",
    room: room,
  });

  // Update UI
  chatTitle.textContent = room;
  messageDisplay.innerHTML = "";
  updateRoomList();

  log(`Switched to room ${room}`);
}

function sendMessage() {
  const text = messageInput.value.trim();

  if (!text) {
    return;
  }

  // Check if it's a DM command: /dm @username message
  if (text.startsWith("/dm ")) {
    const parts = text.slice(4).split(" ", 1);
    if (parts[0]) {
      const toUser = parts[0];
      const dmText = text.slice(4 + toUser.length).trim();
      sendToServer({
        type: "dm",
        to: toUser,
        text: dmText,
      });
      displaySystemMessage(`[DM to ${toUser}]: ${dmText}`);
    }
  } else {
    // Regular room message
    sendToServer({
      type: "message",
      room: chatState.currentRoom,
      text: text,
    });

    // Display own message immediately (optimistic)
    const timestamp = new Date().toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    displayMessage(chatState.username, text, timestamp, true);
  }

  messageInput.value = "";
  messageInput.style.height = "auto";
}

// ============================================================================
// Status Management
// ============================================================================

function updateStatus(status) {
  chatState.status = status;

  sendToServer({
    type: "status",
    status: status,
  });

  // Update button
  const statusSymbol = { online: "🟢", away: "🟡", offline: "⚫" };
  const statusText = status.charAt(0).toUpperCase() + status.slice(1);
  statusBtn.textContent = `${statusSymbol[status]} ${statusText}`;

  log(`Status changed to ${status}`);
}

// ============================================================================
// Event Listeners
// ============================================================================

// Send message on button click
sendBtn.addEventListener("click", sendMessage);

// Send message on Enter (Shift+Enter for newline)
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto-resize textarea
messageInput.addEventListener("input", (e) => {
  e.target.style.height = "auto";
  e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
});

// Send typing indicator
messageInput.addEventListener("input", () => {
  sendToServer({
    type: "typing",
    room: chatState.currentRoom,
  });
});

// Status dropdown
statusBtn.addEventListener("click", () => {
  statusDropdown.classList.toggle("active");
});

document.querySelectorAll(".dropdown-item").forEach((item) => {
  item.addEventListener("click", () => {
    const status = item.getAttribute("data-status");
    updateStatus(status);
    statusDropdown.classList.remove("active");
  });
});

// Direct message modal
dmBtn.addEventListener("click", () => {
  const members = chatState.members[chatState.currentRoom] || [];
  userSelectList.innerHTML = "";

  for (const member of members) {
    if (member.name === chatState.username) {
      continue;
    }

    const userEl = document.createElement("li");
    userEl.className = "user-select-item";

    const dot = document.createElement("span");
    dot.className = `status-dot ${member.status}`;

    const nameEl = document.createElement("span");
    nameEl.textContent = member.name;

    userEl.appendChild(nameEl);
    userEl.appendChild(dot);

    userEl.addEventListener("click", () => {
      const dmText = prompt(`Send a message to ${member.name}:`);
      if (dmText) {
        sendToServer({
          type: "dm",
          to: member.name,
          text: dmText,
        });
        displaySystemMessage(`[DM to ${member.name}]: ${dmText}`);
      }
      dmModal.classList.remove("active");
    });

    userSelectList.appendChild(userEl);
  }

  dmModal.classList.add("active");
});

dmClose.addEventListener("click", () => {
  dmModal.classList.remove("active");
});

dmModal.addEventListener("click", (e) => {
  if (e.target === dmModal) {
    dmModal.classList.remove("active");
  }
});

// ============================================================================
// Initialization
// ============================================================================

function log(message) {
  console.log(`[Chat] ${message}`);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Initialize chat
function initializeChat() {
  // Generate username
  chatState.username = generateUsername();
  usernameDisplay.textContent = chatState.username;

  // Connect to WebSocket
  connectWebSocket();

  log(`Initialized with username: ${chatState.username}`);
}

// Start chat when page loads
window.addEventListener("load", initializeChat);
