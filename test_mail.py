import smtplib
from email.mime.text import MIMEText

# === 请填入你的信息进行测试 ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
GMAIL_USER = "junxie01@gmail.com"  # 填入 MAIL_USERNAME
GMAIL_PASSWORD = "qvbstypxtbdjnzrf" # 填入 MAIL_PASSWORD (无空格)
RECEIVER = "junxie01@gmail.com"         # 填入 MAIL_TO
# ===========================

def test_login():
    try:
        print(f"正在尝试连接 {SMTP_SERVER}...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        print("正在尝试登录...")
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        print("✅ 登录成功！你的账号和应用专用密码是正确的。")
        
        # 尝试发送一封测试邮件
        msg = MIMEText("这是一封来自冰川地震学论文系统的验证邮件。")
        msg['Subject'] = "邮箱验证测试"
        msg['From'] = GMAIL_USER
        msg['To'] = RECEIVER
        
        server.sendmail(GMAIL_USER, [RECEIVER], msg.as_string())
        print(f"✅ 测试邮件已发送至 {RECEIVER}，请查收。")
        
        server.quit()
    except Exception as e:
        print(f"❌ 验证失败！错误详情:\n{e}")

if __name__ == "__main__":
    test_login()
