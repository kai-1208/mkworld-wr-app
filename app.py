from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import unquote_plus

app = Flask(__name__)

@app.route("/")
def index():
    url = "https://mkwrs.com/mkworld/"
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table.wr tr")
    tally_tables = soup.select("table.tally")

    records = []
    player_rankings = []
    nation_rankings = []

    for row in rows:
        col = row.find_all("td")
        if len(col) < 9:
            continue

        try:
            course = col[0].find("a").text.strip()
            time = col[1].find("a").text.strip()
            yt_url = col[1].find("a")["href"]
            player = col[2].find("a").text.strip()

            nation_img = col[3].find("img")
            nation = nation_img["alt"] if nation_img else "Unknown"

            date = col[4].text.strip()
            character = col[6].text.strip()
            vehicle = col[7].text.strip()
            splits = col[8].find("img")["onmouseover"]

            pattern = r"show_splits\(\s*'[^']*',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)'\s*\);"
            match = re.match(pattern, splits)
            if match:
                lap1, lap2, lap3 = match.group(1), match.group(2), match.group(3)
                coins = match.group(4)
                mushrooms = match.group(5)
            else:
                lap1 = lap2 = lap3 = coins = mushrooms = "N/A"

            records.append({
                "course": course,
                "time": time,
                "yt_url": yt_url,
                "player": player,
                "nation": nation,
                "date": date,
                "character": character,
                "vehicle": vehicle,
                "lap1": lap1,
                "lap2": lap2,
                "lap3": lap3,
                "coins": coins,
                "mushrooms": mushrooms
            })
        except Exception as e:
            print("Error", e)
            continue

    if len(tally_tables) > 0:
        player_rows = tally_tables[0].select("tr")[1:]
        for row in player_rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            player = cols[0].get_text(strip=True)
            nation_img = cols[1].find("img")
            nation = nation_img["alt"] if nation_img else "Unknown"
            wr_count = int(cols[2].text.strip())
            player_rankings.append({
                "player": player,
                "nation": nation,
                "wr_count": wr_count
            })

    if len(tally_tables) > 1:
        nation_rows = tally_tables[1].select("tr")[1:]
        for row in nation_rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            nation_img = cols[0].find("img")
            nation = nation_img["alt"] if nation_img else "Unknown"
            wr_count = int(cols[1].text.strip())
            nation_rankings.append((nation, wr_count))

    return render_template("index.html", records=records, player_rankings=player_rankings, nation_rankings=nation_rankings) # index.htmlを読み込んで、recordsを返す


def get_course_history(course_name):
    """指定されたコースのWR履歴を取得する共通関数"""
    encoded_name = urllib.parse.quote_plus(course_name)
    url = f"https://mkwrs.com/mkworld/display.php?track={encoded_name}"
    
    try:
        res = requests.get(url)
        res.raise_for_status() # HTTPエラーがあればここで例外を発生させる
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None, None, None # エラー時はNoneを返す

    rows = soup.select("table.wr tr")
    if not rows or len(rows) < 2:
        return [], [], f"No WR history found for {course_name}"

    header_cells = rows[0].find_all("th")
    lap_columns = [th.text.strip() for th in header_cells if th.text.strip().startswith("Lap")]

    history = []
    i = 1
    while i < len(rows):
        row1 = rows[i]
        cols1 = row1.find_all("td")
        
        # 行の列数が足りない場合はスキップする
        if len(cols1) < 4:
            i += 1
            continue

        is_rowspan = "rowspan" in str(row1)
        row2 = rows[i + 1] if is_rowspan and i + 1 < len(rows) else None
        cols2 = row2.find_all("td") if row2 else []

        try:
            date = cols1[0].text.strip()
            time = cols1[1].text.strip()
            player = cols1[2].text.strip()
            nation_img = cols1[3].find("img")
            nation = nation_img["alt"] if nation_img else "Unknown"

            base_idx = 5
            lap_times = [td.text.strip() for td in cols1[base_idx : base_idx + len(lap_columns)]]
            
            # --- 安全なデータ取得 ---
            data_idx = base_idx + len(lap_columns)
            if is_rowspan:
                coins = cols1[data_idx].text.strip() if len(cols1) > data_idx else "N/A"
                character = cols1[data_idx + 1].text.strip() if len(cols1) > data_idx + 1 else "N/A"
                shrooms = cols2[0].text.strip() if len(cols2) > 0 else "N/A"
                kart = cols2[1].text.strip() if len(cols2) > 1 else "N/A"
            else:
                coins = cols1[data_idx].text.strip() if len(cols1) > data_idx else "N/A"
                shrooms = cols1[data_idx + 1].text.strip() if len(cols1) > data_idx + 1 else "N/A"
                character = cols1[data_idx + 2].text.strip() if len(cols1) > data_idx + 2 else "N/A"
                kart = cols1[data_idx + 3].text.strip() if len(cols1) > data_idx + 3 else "N/A"

            history.append({
                "date": date, "time": time, "player": player, "nation": nation,
                "laps": lap_times, "coins": coins, "shrooms": shrooms,
                "character": character, "kart": kart
            })
            i += 2 if is_rowspan else 1
        except Exception as e:
            print(f"Error processing row, skipping. Details: {e}")
            i += 2 if is_rowspan else 1
            
    return history, lap_columns, None # 成功時はエラーメッセージなし


@app.route("/course/<course_name>")
def course_detail(course_name):
    history, lap_columns, error_msg = get_course_history(course_name)
    
    if error_msg:
        return error_msg, 404
        
    return render_template("course_detail.html", course_name=course_name, lap_columns=lap_columns, history=history)


@app.route("/filter")
def wr_filter():
    url = "https://mkwrs.com/mkworld/"
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table.wr tr")
    records = []

    for row in rows:
        col = row.find_all("td")
        if len(col) < 9:
            continue

        try:
            course = col[0].find("a").text.strip()
            time = col[1].find("a").text.strip()
            yt_url = col[1].find("a")["href"]
            player = col[2].find("a").text.strip()

            nation_img = col[3].find("img")
            nation = nation_img["alt"] if nation_img else "Unknown"

            date = col[4].text.strip()
            character = col[6].text.strip()
            vehicle = col[7].text.strip()
            splits = col[8].find("img")["onmouseover"]

            import re
            pattern = r"show_splits\(\s*'[^']*',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)'\s*\);"
            match = re.match(pattern, splits)
            if match:
                lap1, lap2, lap3 = match.group(1), match.group(2), match.group(3)
                coins = match.group(4)
                mushrooms = match.group(5)
            else:
                lap1 = lap2 = lap3 = coins = mushrooms = "N/A"

            records.append({
                "course": course,
                "time": time,
                "yt_url": yt_url,
                "player": player,
                "nation": nation,
                "date": date,
                "character": character,
                "vehicle": vehicle,
                "lap1": lap1,
                "lap2": lap2,
                "lap3": lap3,
                "coins": coins,
                "mushrooms": mushrooms
            })
        except:
            continue

    return render_template("wr_filter.html", records=records)


@app.route("/compare")
def compare_select():
    url = "https://mkwrs.com/mkworld/"
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table.wr tr")
    records = []

    for row in rows:
        col = row.find_all("td")
        if len(col) < 5:
            continue

        try:
            course = col[0].find("a").text.strip()
            time = col[1].find("a").text.strip()
            player = col[2].find("a").text.strip()
            date = col[4].text.strip()
            records.append({
                "course": course,
                "time": time,
                "player": player,
                "date": date
            })
        except:
            continue

    return render_template("compare_select.html", records=records)


@app.route("/compare/<course_name>")
def compare_course(course_name):
    decoded_name = unquote_plus(course_name)  # ← ここで '+' を ' ' に戻す
    
    history, lap_columns, error_msg = get_course_history(decoded_name)

    if error_msg:
        return error_msg, 404

    return render_template("compare_course.html", course_name=decoded_name, lap_columns=lap_columns, history=history)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10070, debug=True)
