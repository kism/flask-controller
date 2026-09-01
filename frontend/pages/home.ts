// One entrypoint per template, home.html.j2 loads the bundle this builds to as static/home.js.
// The sdk in ../generated is generated from the running app's OpenAPI schema, regenerate with `bun run codegen`
// after any api change. A renamed endpoint, a new button or a changed response model then fails `bun run check`.
import { type Button, getStatus, postInput } from "../generated";

// The console is the ui for renaming yourself, so clientid lives on window rather than in module scope.
declare global {
  interface Window {
    clientid: string;
  }
}

// KeyboardEvent.keyCode -> the button it sends, and whether it's currently held. Windows repeats keydown while a
// key is held, the flag stops the duplicate POSTs.
const keymap = new Map<number, { button: Button; held: boolean }>([
  [65, { button: "GBA_L", held: false }],
  [83, { button: "GBA_R", held: false }],
  [68, { button: "GBA_START", held: false }],
  [90, { button: "GBA_B", held: false }],
  [88, { button: "GBA_A", held: false }],
  [67, { button: "GBA_SELECT", held: false }],
  [38, { button: "GBA_UP", held: false }],
  [40, { button: "GBA_DOWN", held: false }],
  [37, { button: "GBA_LEFT", held: false }],
  [39, { button: "GBA_RIGHT", held: false }],
]);

const GREEN = "#CCFFCC";
const RED = "#FFCCCC";
const GREY = "#C8C8C8";

const latency = document.getElementById("HTTP_LATENCY")!;
const sockStatus = document.getElementById("SOCKET_STATUS")!;
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

async function sendInput(button: Button, down: boolean): Promise<void> {
  const start = performance.now();

  try {
    // AbortSignal.timeout() is native, no AbortController/setTimeout/clearTimeout dance needed.
    const { error, response } = await postInput({
      body: { button, down },
      headers: { "client-id": window.clientid },
      signal: AbortSignal.timeout(1000),
    });

    if (error || !response?.ok) {
      set(latency, response ? "Something is wrong" : "Cannot reach webserver", RED);
      return;
    }

    const frames = Math.round((performance.now() - start) * (1 / 60));
    set(latency, latencyText(frames), frames < 4 ? GREEN : RED);
  } catch (error) {
    console.error("Could not send input to the webserver: ", error); // Belt and braces, the client returns rather than throws.
    unreachable();
  }
}

async function poll(): Promise<void> {
  try {
    const { data } = await getStatus({
      headers: { "client-id": window.clientid },
      signal: AbortSignal.timeout(1000),
    });

    if (!data) {
      unreachable(); // Non 2xx leaves data undefined, so do network failures and the timeout.
      return;
    }

    // data is typed as StatusResponse, so these fields are checked against the app's pydantic model.
    set(sockStatus, data.sock_connected ? "Connected" : "Disconnected", data.sock_connected ? GREEN : RED);
    playerCount.textContent = `${data.players_connected}`;
  } catch (error) {
    console.error("Could not get status from the webserver: ", error);
    unreachable();
  }
}

function makeId(): string {
  const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  return Array.from({ length: 6 }, () => characters.charAt(Math.floor(Math.random() * characters.length))).join("");
}

document.addEventListener("keydown", (event) => {
  const key = keymap.get(event.keyCode);
  if (!key || key.held) return;
  key.held = true;
  document.getElementById(key.button)!.style.backgroundColor = "#003F87";
  void sendInput(key.button, true);
});

document.addEventListener("keyup", (event) => {
  const key = keymap.get(event.keyCode);
  if (!key) return;
  key.held = false;
  document.getElementById(key.button)!.style.backgroundColor = "#222222";
  void sendInput(key.button, false);
});

document.getElementById("CHANGE_USERNAME")!.addEventListener("click", (event) => {
  event.preventDefault();
  window.clientid = prompt("Enter six character username:") ?? window.clientid;
});

window.clientid = makeId(); // Not a const, it's fun to let players rename themselves from the js console.
void poll(); // Call on page load, setInterval waits for the interval before its first call.
setInterval(poll, 5000);
