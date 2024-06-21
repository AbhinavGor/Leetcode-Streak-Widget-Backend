from fastapi import FastAPI, HTTPException
import requests
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

def get_leetcode_streak(username):
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/"
    }
    query = """
    query userProfilePublicProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submissionCalendar
        }
    }
    """
    variables = {
        "username": username
    }
    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data['data']['matchedUser']:
            raise HTTPException(status_code=404, detail="User not found")
        submission_calendar = data['data']['matchedUser']['submissionCalendar']
        streak = calculate_streak(submission_calendar)
        return streak
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def calculate_streak(submission_calendar):
    submission_data = eval(submission_calendar)
    submission_dates = [datetime.fromtimestamp(int(timestamp)).date() for timestamp in submission_data.keys()]
    submission_dates.sort()
    
    current_streak = 0
    longest_streak = 0
    streak_ongoing = False

    for i in range(len(submission_dates)):
        if i == 0:
            current_streak = 1
            longest_streak = 1
            streak_ongoing = True
        else:
            if submission_dates[i] == submission_dates[i - 1] + timedelta(days=1):
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
            else:
                if submission_dates[i] != submission_dates[i - 1]:
                    current_streak = 1

    return longest_streak if not streak_ongoing else current_streak

@app.get("/streak/{username}")
def read_streak(username: str):
    try:
        streak_length = get_leetcode_streak(username)
        return {"username": username, "streak_length": streak_length}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

