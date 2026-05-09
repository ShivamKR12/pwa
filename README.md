# Turning a Pygbag/Pygame-CE web game into a PWA

Turning a Pygbag/Pygame-CE web game into a fully functional, offline-capable Progressive Web App (PWA) for both desktop and mobile comes down to satisfying the strict requirements of modern web browsers.

Browsers will only offer the "Install App" prompt and enable offline mode if a specific checklist is completed flawlessly. Based on everything we've built, here is the universal, step-by-step guide to making any Pygbag game a successful PWA:

## 1. The Pygbag Foundation
Before worrying about PWA features, the game itself must be web-ready:

* **Async Main Loop:** The game must use `asyncio` with `await asyncio.sleep(0)` inside the main loop so it doesn't freeze the browser.
* **Relative Assets:** All images and sounds should be loaded from a local subdirectory (like `assets/`) relative to `main.py`.
* **Responsive Scaling:** Using `pygame.SCALED` along with `pygame.RESIZABLE` or `pygame.FULLSCREEN` ensures the game stretches correctly on different screen sizes.

## 2. The PWA "Trinity"
Every successful PWA requires three specific web assets to sit alongside your game files:

### A. The Web Manifest (`manifest.json`)
This acts as the "ID card" for your app. It tells the operating system how your app should behave when installed.
* `start_url`: Must be strictly relative (e.g., `"./"`) so the app doesn't break depending on where it's hosted.
* `display`: Set to `"fullscreen"` or `"standalone"` to remove the browser UI.
* `orientation`: Lock it to `"landscape"` or `"portrait"` depending on your game's design.
* `theme_color` & `background_color`: Essential for the OS to style the loading screens and status bars.

### B. The Icons
Browsers need icons to place on the home screen or desktop.
* At a bare minimum, you need one `512x512` PNG icon.
* If you want to satisfy strict app store guidelines (like Google Play via PWABuilder), you also need a `192x192` PNG icon. Both should ideally have the `"purpose": "any maskable"` property so Android can shape them nicely.

### C. The Service Worker (`sw.js`)
This is the heart of the offline experience. It is a background JavaScript file that acts as a network proxy.
* **Pre-caching:** The very first time the user opens the page, the Service Worker must download and save the HTML, Manifest, Icons, and—crucially—the Pygbag game archive (`.apk` or `.tar.gz`).
* **Fetch Interception:** Whenever the game tries to load a file, the Service Worker intercepts the request. If the user is offline, it serves the saved files from the cache instead of throwing a "No Internet" error.

## 3. The HTML Glue
Pygbag generates an `index.html` file to run your game, but it doesn't know about your PWA files. You must inject three things into the `<head>` of that HTML file:

1. `<link rel="manifest" href="manifest.json" />` (Android is incredibly strict about this exact formatting).
2. `<meta name="theme-color" content="#FFFFFF">`
3. A `<script>` tag that registers your Service Worker (`navigator.serviceWorker.register('./sw.js')`).

## 4. The Automation Script
Because Pygbag overwrites the `build/web` directory from scratch every time you compile the game, manually injecting the HTML tags and copying the Service Worker gets exhausting.

A successful PWA workflow always involves a build script (like the `build_pwa.py` we made). The script's job is to:

1. Run the Pygbag compiler.
2. Copy the manifest and icons into the final directory.
3. Dynamically generate the `sw.js` file (making sure to include the exact name of the generated game archive in the cache list).
4. Safely inject the required HTML tags into the compiled `index.html`.

## 5. Secure Hosting (HTTPS)
Service Workers are incredibly powerful, so browsers enforce a strict security rule: **PWAs will only install if they are hosted on a secure HTTPS connection.**

* You cannot install a PWA over a standard HTTP connection (except for `localhost` when testing).
* Platforms like **GitHub Pages** are the gold standard for indie web games because they automatically provide free, secure HTTPS hosting out of the box!

---

If you apply these 5 steps to any Pygame project, you will instantly have a web game that looks and acts like a true native application on iOS, Android, Windows, and Mac!