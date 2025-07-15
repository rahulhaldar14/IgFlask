from flask import Flask, jsonify, request
from playwright.async_api import async_playwright
import asyncio, re

app = Flask(__name__)

API_KEY = "rahul123"

async def scrape_instagram(username):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        await page.wait_for_selector('meta[name="description"]', timeout=10000)
        desc = await page.get_attribute('meta[name="description"]', 'content')
        title = await page.title()
        profile_pic = await page.get_attribute('img[data-testid="user-avatar"]', 'src')

        followers = re.search(r'([\d,.]+)\s+Followers', desc)
        following = re.search(r'([\d,.]+)\s+Following', desc)
        posts = re.search(r'([\d,.]+)\s+Posts', desc)

        return {
            "username": username,
            "title": title,
            "profile_picture": profile_pic,
            "followers": followers.group(1) if followers else "N/A",
            "following": following.group(1) if following else "N/A",
            "posts": posts.group(1) if posts else "N/A"
        }

@app.route("/profile/<username>")
def profile(username):
    user_key = request.args.get("key")
    if user_key != API_KEY:
        return jsonify({"error": "Unauthorized 🔒 Invalid API key"}), 401
    data = asyncio.run(scrape_instagram(username))
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
