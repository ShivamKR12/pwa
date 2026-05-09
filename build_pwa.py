import os
import sys
import shutil
import subprocess

def make_offline_pwa():
    # 1. Build the game using pygbag (generates the build/web directory)
    print("Building pygbag project...")
    subprocess.run([sys.executable, "-m", "pygbag", "--build", "main.py"], check=True)
    
    web_dir = os.path.join("build", "web")
    docs_dir = "docs"
    
    # Create or overwrite the docs directory for GitHub Pages
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    shutil.copytree(web_dir, docs_dir)

    index_path = os.path.join(docs_dir, "index.html")
    sw_path = os.path.join(docs_dir, "sw.js")

    # Ensure manifest and favicon are copied to the web root for PWA installation
    for file in ["manifest.json", "favicon.png"]:
        if os.path.exists(file):
            shutil.copy(file, os.path.join(docs_dir, file))
            
    # Find the game archive to precache
    archive_name = ""
    for file in os.listdir(docs_dir):
        if file.endswith(".tar.gz") or file.endswith(".apk"):
            archive_name = file
            break

    # 2. Inject Service Worker registration into index.html
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        # Ensure manifest and theme-color are properly linked in the HTML head
        if 'rel="manifest"' not in html and "rel='manifest'" not in html:
            html = html.replace('</head>', '  <link rel="manifest" href="./manifest.json">\n  <meta name="theme-color" content="#FFFFFF">\n</head>')
        else:
            html = html.replace('href="/manifest.json"', 'href="./manifest.json"')
            html = html.replace('href="manifest.json"', 'href="./manifest.json"')

        sw_registration = """
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => console.log('Service Worker registered!'))
      .catch(err => console.log('Service Worker registration failed: ', err));
  });
}
</script>
"""
        if "navigator.serviceWorker.register" not in html:
            html = html.replace("</body>", sw_registration + "\n</body>")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html)
            print("Service Worker registration injected into index.html")
            
    # 3. Create the Service Worker file (sw.js)
    sw_code = f"""const CACHE_NAME = 'pygame-pwa-cache-v3';
const PRECACHE_URLS = [
    './',
    './index.html',
    './favicon.png',
    './manifest.json',
    './favicons/favicon-192x192.png',
    './{archive_name}'
];

self.addEventListener('install', event => {{
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
    );
}});

self.addEventListener('activate', event => {{
    event.waitUntil(self.clients.claim());
}});

self.addEventListener('fetch', event => {{
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(response => {{
                // Cache successful GET requests for offline use
                if (response && (response.status === 200 || response.type === 'opaque')) {{
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {{
                        cache.put(event.request, responseClone);
                    }});
                }}
                return response;
            }})
            .catch(() => {{
                // Fallback to cache if network fails (offline mode)
                return caches.match(event.request, {{ ignoreSearch: true }});
            }})
    );
}});
"""
    with open(sw_path, "w", encoding="utf-8") as f:
        f.write(sw_code)
    print(f"Service Worker generated at {sw_path}")
    print("\\nReady for GitHub Pages! The 'docs' folder has been created.")
    print("To test locally, run:")
    print("python -m http.server --directory docs 8000")

if __name__ == "__main__":
    make_offline_pwa()