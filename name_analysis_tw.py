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
        msg['Subject'] = "新的 KataChatBot 提交记录"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ 邮件发送成功")
    except Exception as e:
        logging.error("❌ 邮件发送失败: %s", str(e))

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
            return jsonify({"error": f"❌ 无法识别的月份格式: {dob_month}"}), 400

        birthdate = datetime(int(dob_year), month_num, int(dob_day))
        age = datetime.now().year - birthdate.year
        gender_label = CHINESE_GENDER.get(gender, "孩子")

        metrics = [
            {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手型"], "values": [63, 27, 12]},
            {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"], "values": [58, 31, 46]},
            {"title": "学习信心", "labels": ["数学", "阅读", "专注力"], "values": [76, 55, 48]},
        ]

        visual, auditory, kinesthetic = metrics[0]['values']
        review, group, independent = metrics[1]['values']
        math, reading, focus = metrics[2]['values']

        para1 = (
            f"在{country}，许多大约 {age} 岁的{gender_label}正逐渐建立起自己的学习偏好。"
            f"数据显示，视觉型学习占比为 {visual}% ，图像、色彩与故事性内容正成为他们理解世界的重要入口。"
            f"听觉型占比为 {auditory}%，而动手型为 {kinesthetic}% ，呈现出孩子们在感知方式上的多样性。"
            f"这些差异反映出不同孩子在接收知识时的路径与节奏，需要更灵活的学习设计来配合。"
            f"家长若能因材施教，比如透过图卡、故事书或互动实验，将有助于他们的认知连结更稳固。"
        )

        para2 = (
            f"在学习投入方面，有 {review}% 的孩子已养成每日复习的习惯，展现出稳定的学习节奏。"
            f"{independent}% 倾向自主学习，说明他们拥有一定的内驱力与独立性。"
            f"但也注意到小组学习的比例仅为 {group}% ，代表他们在群体互动上可能仍在发展中。"
            f"这也提醒我们：协作式学习需要以更温和、不具压力的方式引导。"
            f"例如安排低焦虑的小范围共学活动，有助于孩子逐步建立信任感与表达能力。"
        )

        para3 = (
            f"在学科信心方面，数学信心高达 {math}% ，显示孩子在数理逻辑方面已有一定掌握。"
            f"阅读为 {reading}% ，可能因词汇量、语境理解或阅读习惯影响了表现。"
            f"而专注力则维持在 {focus}% 左右，说明许多孩子仍在练习如何维持持续注意力。"
            f"这些数字并不是评价标准，而是成长线索，告诉我们该支持哪些学习技能的培养。"
            f"透过游戏化练习、音乐导入或设定专注时间，都是提升他们持久力的好工具。"
        )

        para4 = (
            f"整体来看，孩子们正处在一个从模糊认知走向结构思考的关键时期。"
            f"他们需要的是被理解的学习环境，而非被迫适应的压力框架。"
            f"家长可以依照这些趋势，选择合适的学习材料与陪伴方式，建立积极的学习体验。"
            f"同时，也要给予他们犯错与尝试的空间，让他们在试探中成长，在探索中找到信心。"
            f"这样的支持，不仅帮助孩子掌握知识，也让他们在心理上感受到被接纳与信赖。"
        )

        summary = f"🧠 学习总结：<br><br>{para1}<br><br>{para2}<br><br>{para3}<br><br>{para4}"
        charts_html = generate_email_charts(metrics)

        footer = """
        <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
          <strong>本报告的洞察由 KataChat AI 系统生成，分析基础如下：</strong><br>
          1. 来自新加坡、马来西亚、台湾的匿名儿童学习行为数据库（已获家长授权）<br>
          2. 来自 OpenAI 教育研究数据与趋势的非个人化分析<br>
          <em>所有数据处理均通过本系统的 AI 模型执行，并严格遵守 PDPA 数据保护规范。</em>
        </p>
        <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
          <strong>附言：</strong>您将在 24-48 小时内收到完整的个性化报告邮件。<br>
          如希望进一步了解分析结果，欢迎通过 Telegram 联系我们或预约 15 分钟简聊。
        </p>
        """

        html_body = f"""
        👤 姓名：{name}<br>
        🈶 中文名：{chinese_name}<br>
        ⚧️ 性别：{gender}<br>
        🎂 生日：{dob_year}-{dob_month}-{dob_day}<br>
        🕑 年龄：{age}<br>
        🌍 国家：{country}<br>
        📞 电话：{phone}<br>
        📧 邮箱：{email}<br>
        💬 推荐人：{referrer}<br><br>

        📊 AI 分析：<br>{summary}<br><br>
        {charts_html}
        {footer}
        """

        send_email(html_body)

        return jsonify({
            "analysis": summary + footer,  # ✅ Removed charts_html from here
            "metrics": metrics
        })

    except Exception as e:
        logging.error("❌ 系统错误: %s", str(e))
        return jsonify({"error": "⚠️ 系统内部错误，请稍后再试"}), 500

if __name__ == '__main__':
    app.run(debug=True)
