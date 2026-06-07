import requests
import re
import os
from datetime import datetime

LEETCODE_USERNAME = "auamores"
README_PATH = "README.md"

START_MARKER = "<!-- LEETCODE:START -->"
END_MARKER = "<!-- LEETCODE:END -->"

GRAPHQL_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0"
}

def fetch_stats():
    query = """
    query userProfile($username: String!) {
      matchedUser(username: $username) {
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
      allQuestionsCount {
        difficulty
        count
      }
    }
    """
    r = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"username": LEETCODE_USERNAME}}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()["data"]

    solved_map = {x["difficulty"]: x["count"] for x in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]}
    total_map = {x["difficulty"]: x["count"] for x in data["allQuestionsCount"]}

    return {
        "easySolved": solved_map.get("Easy", 0),
        "mediumSolved": solved_map.get("Medium", 0),
        "hardSolved": solved_map.get("Hard", 0),
        "totalSolved": solved_map.get("All", 0),
        "totalEasy": total_map.get("Easy", 0),
        "totalMedium": total_map.get("Medium", 0),
        "totalHard": total_map.get("Hard", 0),
        "totalAll": total_map.get("All", 0),
    }

def fetch_contest():
    query = """
    query userContestInfo($username: String!) {
      userContestRanking(username: $username) {
        rating
        globalRanking
        totalParticipants
      }
    }
    """
    r = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"username": LEETCODE_USERNAME}}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()["data"]["userContestRanking"]
    if not data:
        return {"rating": "N/A", "globalRanking": "N/A"}
    return {
        "rating": round(data["rating"], 2),
        "globalRanking": data["globalRanking"],
    }

def build_section(stats, contest):
    easy = stats["easySolved"]
    medium = stats["mediumSolved"]
    hard = stats["hardSolved"]
    total = stats["totalSolved"]
    easy_total = stats["totalEasy"]
    medium_total = stats["totalMedium"]
    hard_total = stats["totalHard"]
    total_all = stats["totalAll"]

    rating = contest["rating"]
    rank = contest["globalRanking"]

    updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    section = f"""<!-- LEETCODE:START -->
### 🧩 LeetCode Stats
| Difficulty | Solved | Total |
|:----------:|:------:|:-----:|
| 🟢 Easy    | {easy} | {easy_total} |
| 🟡 Medium  | {medium} | {medium_total} |
| 🔴 Hard    | {hard} | {hard_total} |
| **Total**  | **{total}** | **{total_all}** |

> 🏆 Contest Rating: `{rating}` · Global Rank: `#{rank}`
>
> 🔄 *Auto-updated: {updated}*
<!-- LEETCODE:END -->"""
    return section

def update_readme(section):
    if not os.path.exists(README_PATH):
        print(f"README not found at {README_PATH}")
        return False

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print("Markers not found in README.")
        return False

    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    new_content = pattern.sub(section, content)

    if new_content == content:
        print("No changes detected.")
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README updated.")
    return True

if __name__ == "__main__":
    print("Fetching LeetCode stats...")
    stats = fetch_stats()
    contest = fetch_contest()
    section = build_section(stats, contest)
    update_readme(section)
    print("Done.")
