
from flask import Flask, jsonify, request
from playwright.async_api import async_playwright
import asyncio, re
import nest_asyncio
nest_asyncio.apply()

app = Flask(__name__)
API_KEY = "rahul123"

async def scrape_instagram(username):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

            # Wait for basic content to load
            await page.wait_for_selector('meta[name="description"]', timeout=20000)
            desc = await page.get_attribute('meta[name="description"]', 'content')
            title = await page.title()

            # Fallback: use any img tag as avatar if specific selector fails
            try:
                profile_pic = await page.get_attribute('img[data-testid="user-avatar"]', 'src')
            except:
                profile_pic = await page.get_attribute('img', 'src')

            followers = re.search(r'([\d,.]+)\s+Followers', desc)
            following = re.search(r'([\d,.]+)\s+Following', desc)
            posts = re.search(r'([\d,.]+)\s+Posts', desc)

            return {
                "username": username,
                "title": title,
                "profile_picture": profile_pic or "N/A",
                "followers": followers.group(1) if followers else "N/A",
                "following": following.group(1) if following else "N/A",
                "posts": posts.group(1) if posts else "N/A"
            }
    except Exception as e:
        return {"error": "Failed to scrape", "details": str(e)}

@app.route("/profile/<username>")
def profile(username):
    user_key = request.args.get("key")
    if user_key != API_KEY:
        return jsonify({"error": "Unauthorized ðŸ”’ Invalid API key"}), 401
    try:
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(scrape_instagram(username))
        return jsonify(data)
    except Exception as e:
        import traceback
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e),
            "trace": traceback.format_exc()
        }), 500

@app.route("/")
def home():
    return "âœ… IG Profile API is live. Use /profile/<username>?key=rahul123"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
