import os
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# ✅ 工廠實驗室 MySQL 連線參數（從環境變數讀取）
MYSQL_HOST  = os.getenv('MYSQL_HOST')
MYSQL_PORT  = os.getenv('MYSQL_PORT')
MYSQL_USER  = os.getenv('MYSQL_USER')
MYSQL_PASS  = os.getenv('MYSQL_PASSWORD')
MYSQL_DB    = os.getenv('MYSQL_DATABASE')
MYSQL_TABLE = os.getenv('MYSQL_TABLE')

@function_tool
def get_vibration_all_on_date(date_str: str):
    """
    取得指定日期的所有振動資料（以自動偵測到的時間欄位排序），並且對振動值取 ABS。
    回傳字串（每列一行）。
    """
    print(f"[debug] getting all vibration data for date: {date_str}")
    import mysql.connector

    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASS, database=MYSQL_DB
        )
        cursor = conn.cursor()

        # 找欄位（自動偵測 time/date 與 vibration）
        cursor.execute(f"SHOW COLUMNS FROM `{MYSQL_TABLE}`")
        columns = [row[0] for row in cursor.fetchall()]
        vibration_col = next((c for c in columns if 'vibration' in c.lower()), None)
        time_columns  = [c for c in columns if 'time' in c.lower() or 'date' in c.lower()]

        if not vibration_col:
            return "No vibration column found."
        if not time_columns:
            return "No time/date columns found for filtering."

        time_col = time_columns[0]

        # ✅ 用 ABS() 取絕對值並以別名輸出，避免負值干擾
        query = (
            f"SELECT `{time_col}`, ABS(`{vibration_col}`) AS vib_abs "
            f"FROM `{MYSQL_TABLE}` "
            f"WHERE DATE(`{time_col}`) = %s "
            f"ORDER BY `{time_col}` ASC"
        )
        cursor.execute(query, (date_str,))
        rows = cursor.fetchall()

        if not rows:
            return f"{date_str} 沒有資料。"

        result_lines = [f"{time_col}: {r[0]}, {vibration_col}(abs): {r[1]}" for r in rows]
        return "\n".join(result_lines)

    except Exception as e:
        return f"Error retrieving vibration data: {e}"
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

@function_tool
def find_vibration_outliers_on_date(date_str: str, threshold: float = 3.0):
    """
    取得指定日期的資料，對振動欄位做均值±threshold*std 的離群值判定（針對 ABS 後的值），
    回傳每筆離群列的所有欄位（字串）。
    """
    print(f"[debug] finding vibration outliers for date: {date_str} with threshold {threshold}")
    import mysql.connector

    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASS, database=MYSQL_DB
        )
        cursor = conn.cursor(dictionary=True)

        # 欄位偵測
        cursor.execute(f"SHOW COLUMNS FROM `{MYSQL_TABLE}`")
        columns = [row["Field"] for row in cursor.fetchall()]
        vibration_col = next((c for c in columns if 'vibration' in c.lower()), None)
        time_columns  = [c for c in columns if 'time' in c.lower() or 'date' in c.lower()]

        if not vibration_col:
            return "No vibration column found."
        if not time_columns:
            return "No time/date columns found for filtering."

        time_col = time_columns[0]

        # 取出當日所有資料（並在 Python 端做 ABS 與離群判定）
        query = f"SELECT * FROM `{MYSQL_TABLE}` WHERE DATE(`{time_col}`) = %s"
        cursor.execute(query, (date_str,))
        rows = cursor.fetchall()
        if not rows:
            return f"{date_str} 沒有資料。"

        # 將振動值取 ABS 以利判定
        vals = []
        for r in rows:
            v = r.get(vibration_col)
            if isinstance(v, (int, float)):
                vals.append(abs(v))

        if not vals:
            return "No valid vibration data found."

        avg = sum(vals) / len(vals)
        std = (sum((x - avg) ** 2 for x in vals) / len(vals)) ** 0.5

        if std == 0:
            return "資料無變異（std=0），無法進行離群判定。"

        outliers = []
        for r in rows:
            v = r.get(vibration_col)
            if isinstance(v, (int, float)):
                v_abs = abs(v)
                if abs(v_abs - avg) > threshold * std:
                    outliers.append(r)

        if not outliers:
            return f"{date_str} 沒有發現離群值。"

        # 輸出所有欄位（字串），方便你後續比對
        lines = ["離群值資料如下："]
        for i, o in enumerate(outliers, 1):
            pairs = ", ".join(f"{k}: {o.get(k)}" for k in columns)
            lines.append(f"{i}. {pairs}")
        return "\n".join(lines)

    except Exception as e:
        return f"Error finding vibration outliers: {e}"
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

@function_tool
def analyze_vibration_list(values: list[float]) -> dict:
    """
    分析一串振動數列（會先做 ABS），回傳平均、變異數、最大、最小。
    """
    print(f"[debug] analyzing vibration list: {values}")
    if not values:
        return {"error": "Input list is empty."}

    vals = [abs(x) for x in values if isinstance(x, (int, float))]
    if not vals:
        return {"error": "No valid numeric values."}

    n = len(vals)
    avg = sum(vals) / n
    var = sum((x - avg) ** 2 for x in vals) / n
    return {"平均值": avg, "變異數": var, "最大值": max(vals), "最小值": min(vals)}

@function_tool
def get_vibration_max_on_date(date_str: str):
    """
    取得指定日期的最大振動值（ABS 後），以及對應的時間點。
    """
    print(f"[debug] getting max vibration data for date: {date_str}")
    import mysql.connector

    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASS, database=MYSQL_DB
        )
        cursor = conn.cursor()

        # 欄位偵測
        cursor.execute(f"SHOW COLUMNS FROM `{MYSQL_TABLE}`")
        columns = [row[0] for row in cursor.fetchall()]
        vibration_col = next((c for c in columns if 'vibration' in c.lower()), None)
        time_columns  = [c for c in columns if 'time' in c.lower() or 'date' in c.lower()]

        if not vibration_col:
            return "No vibration column found."
        if not time_columns:
            return "No time/date columns found for filtering."

        time_col = time_columns[0]

        # ✅ 用 ABS() 判斷最大值，再取對應時間
        query = (
            f"SELECT `{time_col}`, ABS(`{vibration_col}`) AS vib_abs "
            f"FROM `{MYSQL_TABLE}` "
            f"WHERE DATE(`{time_col}`) = %s "
            f"ORDER BY vib_abs DESC "
            f"LIMIT 1"
        )
        cursor.execute(query, (date_str,))
        row = cursor.fetchone()
        if row:
            return f"在 {date_str}，最大 {vibration_col}(abs) = {row[1]}，發生於 {time_col}: {row[0]}"
        else:
            return f"{date_str} 沒有資料。"

    except Exception as e:
        return f"Error retrieving vibration data: {e}"
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@function_tool  
async def current_time() -> str:
    """Fetch the current time for a given location.

    Args:
        location: The location to fetch the current time for.
    """
    import datetime
    return str(datetime.datetime.now().isoformat())



# Define the agent
agent = Agent(
    name="introduction agent",
    instructions=
            """你只用繁體中文回覆。你是一位設備維護工程師，會用對應的 tools 查詢 SQL 資料庫（振動值一律取 ABS），
            並提供設備的振動數據分析、維護建議與故障排除步驟。大致流程為：[取得資料]->[分析資料]->[解析資料]。
            可選工具：
            [取得資料]: get_vibration_all_on_date, get_vibration_max_on_date;
            [分析資料]: analyze_vibration_list;
            [解析資料]: find_vibration_outliers_on_date;""",
    model="gpt-5-mini",
    tools=[
        current_time,
        get_vibration_all_on_date,
        find_vibration_outliers_on_date,
        analyze_vibration_list,
        get_vibration_max_on_date
    ],
)

async def main():
    result = await Runner.run(agent, "請列出 2025-07-27 與 7-28 兩天的所有振動資料，並分析異常值，提供維護建議。")
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())     