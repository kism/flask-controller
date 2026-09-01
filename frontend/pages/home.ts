export {}; // Makes this a module, so the global augmentation below is legal.

// One entrypoint per template, home.html.j2 loads the bundle this builds to as static/home.js.

// The console is the ui for renaming yourself, so clientid lives on window rather than in module scope.
declare global {
  interface Window {
    clientid: string;
  }
}

interface Button {
  id: string; // The <td> id in home.html.j2, and the name the api expects.
  held: boolean; // Windows repeats keydown while held, this stops the duplicate POSTs.
}

// KeyboardEvent.keyCode -> button.
const buttons: Record<number, Button> = {
  65: { id: "GBA_L", held: false },
  83: { id: "GBA_R", held: false },
  68: { id: "GBA_START", held: false },
  90: { id: "GBA_B", held: false },
  88: { id: "GBA_A", held: false },
  67: { id: "GBA_SELECT", held: false },
  38: { id: "GBA_UP", held: false },
  40: { id: "GBA_DOWN", held: false },
  37: { id: "GBA_LEFT", held: false },
  39: { id: "GBA_RIGHT", held: false },
};

const GREEN = "#CCFFCC";
const RED = "#FFCCCC";
const GREY = "#C8C8C8";

const latency = document.getElementById("HTTP_LATENCY")!;
const sockStatus = document.getElementById("FLASK_MGBA_STATS")!;
const playerCount = document.getElementById("PLAYER_COUNT")!;

function set(element: HTMLElement, text: string, color: string): void {
  element.textContent = text;
  element.style.color = color;
}

function latencyText(frames: number): string {
  if (frames < 1) return "＜1 frame"; // Fullwidth chars pad the short strings so the table doesn't jump.
  if (frames === 1) return "　1 frame";
  if (frames < 10) return `　${frames} frames`;
  return `${frames} frames`;
}

function unreachable(): void {
  set(latency, "Cannot reach webserver", RED);
  set(sockStatus, "???", GREY);
  set(playerCount, "???", GREY);
}

async function postKey(button: Button, down: boolean): Promise<void> {
  const start = performance.now();
  const key = `${down ? "D_" : "U_"}${button.id}`;

  try {
    const response = await fetch(`input/${key}`, { method: "POST", headers: { "client-id": window.clientid } });
    console.log("Sent:", key, "| Response code:", response.status);

    if (!response.ok) {
      set(latency, "Something is wrong", RED);
      return;
    }

    const frames = Math.round((performance.now() - start) * (1 / 60));
    set(latency, latencyText(frames), frames < 4 ? GREEN : RED);
  } catch (error) {
    console.error("Could not ProcessUserInput to webserver: ", error);
    unreachable();
  }
}

async function getUpdate(): Promise<void> {
  try {
    const response = await fetch("GetStatus", { method: "GET", headers: { "client-id": window.clientid } });
    if (!response.ok) throw new Error(`Network response was not ok: ${response.status}`);

    const data: { sock_connected: boolean; players_connected: number } = await response.json();
    set(sockStatus, data.sock_connected ? "Connected" : "Disconnected", data.sock_connected ? GREEN : RED);
    playerCount.textContent = `${data.players_connected}`;
  } catch (error) {
    console.error("Could not GetStatus from webserver: ", error);
    unreachable();
  }
}

function makeId(): string {
  const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  return Array.from({ length: 6 }, () => characters.charAt(Math.floor(Math.random() * characters.length))).join("");
}

document.addEventListener("keydown", (event) => {
  const button = buttons[event.keyCode];
  if (!button || button.held) {
    console.log("Ignoring duplicate or invalid input");
    return;
  }
  button.held = true;
  document.getElementById(button.id)!.style.backgroundColor = "#003F87";
  void postKey(button, true);
});

document.addEventListener("keyup", (event) => {
  const button = buttons[event.keyCode];
  if (!button) return;
  button.held = false;
  document.getElementById(button.id)!.style.backgroundColor = "#222222";
  void postKey(button, false);
});

document.getElementById("CHANGE_USERNAME")!.addEventListener("click", (event) => {
  event.preventDefault();
  window.clientid = prompt("Enter six character username:") ?? window.clientid;
});

window.clientid = makeId(); // Not a const, it's fun to let players rename themselves from the js console.
void getUpdate(); // Call on page load, setInterval waits for the interval before its first call.
setInterval(getUpdate, 5000);
