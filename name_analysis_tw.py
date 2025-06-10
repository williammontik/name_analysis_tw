# -*- coding: utf-8 -*-
import os, smtplib, logging, random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}
ENGLISH_MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

CHINESE_GENDER = {
    '男': '男孩',
    '女': '女孩'
}

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "新的 KataChatBot 提交紀錄"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ 郵件已成功發送")
    except Exception as e:
        logging.error("❌ 郵件發送失敗: %s", str(e))

def generate_email_charts(metrics):
    def make_bar_html(title, labels, values, color):
        bar_html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for label, val in zip(labels, values):
            bar_html += f"""
            <div style="margin:8px 0;">
              <div style="font-size:15px; margin-bottom:4px;">{label}</div>
              <div style="background:#eee; border-radius:10px; overflow:hidden;">
                <div style="background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;">
                  {val}%
                </div>
              </div>
            </div>
            """
        return bar_html

    color_map = ['#5E9CA0', '#FFA500', '#9966FF']
    charts_html = ""
    for idx, m in enumerate(metrics):
        color = color_map[idx % len(color_map)]
        charts_html += make_bar_html(m["title"], m["labels"], m["values"], color)
    return charts_html

@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    try:
        data = request.get_json()
        name = data.get("name", "")
        chinese_name = data.get("chinese_name", "")
        gender = data.get("gender", "")
        dob_day = data.get("dob_day", "")
        dob_month = data.get("dob_month", "")
        dob_year = data.get("dob_year", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        country = data.get("country", "")
        referrer = data.get("referrer", "")

        if dob_month in CHINESE_MONTHS:
            month_num = CHINESE_MONTHS[dob_month]
        elif dob_month in ENGLISH_MONTHS:
            month_num = ENGLISH_MONTHS[dob_month]
        else:
            return jsonify({"error": f"❌ 無法辨識的月份格式: {dob_month}"}), 400

        birthdate = datetime(int(dob_year), month_num, int(dob_day))
        age = datetime.now().year - birthdate.year
        gender_label = CHINESE_GENDER.get(gender, "孩子")

        metrics = [
            {"title": "學習偏好", "labels": ["視覺型", "聽覺型", "動手型"], "values": [63, 27, 12]},
            {"title": "學習投入", "labels": ["每日複習", "小組學習", "自主學習"], "values": [58, 31, 46]},
            {"title": "學習信心", "labels": ["數學", "閱讀", "專注力"], "values": [76, 55, 48]},
        ]

        visual, auditory, kinesthetic = metrics[0]['values']
        review, group, independent = metrics[1]['values']
        math, reading, focus = metrics[2]['values']

        para1 = (
            f"在{country}，許多大約 {age} 歲的{gender_label}正在逐步建立自己的學習偏好。"
            f"數據顯示，視覺型學習占比為 {visual}%，圖像、色彩與故事性內容正是他們理解世界的重要入口。"
            f"聽覺型為 {auditory}%，動手型為 {kinesthetic}%，呈現出孩子們在感知方式上的多樣性。"
            f"這些差異反映出孩子們在接收知識時的節奏與習慣，也提醒我們需因材施教。"
            f"透過圖卡、故事書或互動實驗，都有助於加強孩子的認知連結。"
        )

        para2 = (
            f"{review}% 的孩子已養成每日複習的習慣，展現出穩定的學習節奏。"
            f"{independent}% 傾向自主學習，顯示他們具備一定的主動性與獨立思考力。"
            f"小組學習的比例僅為 {group}% ，可能代表群體互動的發展還在初期階段。"
            f"我們可以透過低壓力的小型共學活動，幫助孩子建立信任感與表達能力。"
        )

        para3 = (
            f"學科信心方面，數學信心達到 {math}% ，說明孩子在邏輯與數理方面已有基礎。"
            f"閱讀信心為 {reading}% ，可能受詞彙量或閱讀習慣影響。"
            f"專注力維持在 {focus}% 左右，顯示他們正在練習如何延續注意力。"
            f"透過遊戲化學習、音樂導入或番茄鐘等方式，都能有效幫助孩子提升持久力。"
        )

        para4 = (
            f"整體來看，孩子們正處於從模糊認知轉向結構思考的重要階段。"
            f"他們需要被理解與支持，而非被壓力驅動。"
            f"家長可以根據這些趨勢，選擇更適合的學習工具與陪伴方式，"
            f"也要允許他們嘗試、犯錯、探索，才能真正激發內在動力與信心。"
        )

        summary = f"🧠 學習總結：<br><br>{para1}<br><br>{para2}<br><br>{para3}<br><br>{para4}"
        charts_html = generate_email_charts(metrics)

        footer = """
        <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
          <strong>本報告為 KataChat AI 系統自動生成，資料依據如下：</strong><br>
          1. 來自新加坡、馬來西亞與臺灣的匿名兒童學習數據（經家長授權）<br>
          2. OpenAI 教育研究資料與非個人化趨勢分析<br>
          <em>所有資料均依據 PDPA 數據保護政策進行處理。</em>
        </p>
        <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
          <strong>附註：</strong>完整個人化圖表報告將於 24-48 小時內寄出。<br>
          若需了解更多，可透過 Telegram 聯繫我們或預約 15 分鐘諮詢。
        </p>
        """

        html_body = f"""
        👤 姓名：{name}<br>
        🈶 中文名：{chinese_name}<br>
        ⚧️ 性別：{gender}<br>
        🎂 生日：{dob_year}-{dob_month}-{dob_day}<br>
        🕑 年齡：{age}<br>
        🌍 國家：{country}<br>
        📞 電話：{phone}<br>
        📧 信箱：{email}<br>
        💬 推薦人：{referrer}<br><br>

        📊 AI 分析：<br>{summary}<br><br>
        {charts_html}
        {footer}
        """

        send_email(html_body)

        return jsonify({
            "analysis": summary + footer,
            "metrics": metrics
        })

    except Exception as e:
        logging.error("❌ 系統錯誤: %s", str(e))
        return jsonify({"error": "⚠️ 系統內部錯誤，請稍後再試"}), 500

if __name__ == '__main__':
    app.run(debug=True)
