import time
import random
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load danh sách tài khoản
def load_accounts():
    try:
        with open("accounts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Lưu tài khoản
def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file, indent=4)

# Đăng nhập Facebook và đợi nhập CAPTCHA & 2FA
def login_facebook(driver, email_or_phone, password):
    driver.get("https://www.facebook.com/")
    time.sleep(random.uniform(2, 5))

    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "pass")

    # Kiểm tra và sử dụng email, số điện thoại hoặc UID
    email_input.send_keys(email_or_phone)  # Dùng email, số điện thoại hoặc UID
    password_input.send_keys(password)
    time.sleep(random.uniform(1, 3))
    password_input.send_keys(Keys.RETURN)
    
    log(f"[🔐] {email_or_phone} đang chờ nhập CAPTCHA & 2FA...")

    # Chờ người dùng nhập CAPTCHA & 2FA rồi bấm "Lụm!"
    global waiting_for_login
    waiting_for_login = True
    while waiting_for_login:
        time.sleep(1)

    log(f"[✅] {email_or_phone} đăng nhập thành công!")

# Auto like & comment
def auto_interact(driver, email):
    start_time = time.time()
    duration = 300  # Chạy 5 phút

    while time.time() - start_time < duration:
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(random.uniform(2, 5))

        posts = driver.find_elements(By.XPATH, "//div[@role='article']")
        if posts:
            post = random.choice(posts)
            try:
                like_button = post.find_element(By.XPATH, ".//span[text()='Thích' or text()='Like']")
                like_button.click()
                log(f"[👍] {email} đã like bài viết")

                comment_box = post.find_element(By.XPATH, ".//div[@aria-label='Viết bình luận']")
                comment_box.click()
                comment_box.send_keys(random.choice(["Hay quá!", "Tuyệt vời!", "Đỉnh thật!"]))
                comment_box.send_keys(Keys.RETURN)
                log(f"[💬] {email} đã comment bài viết!")
            except:
                pass
        time.sleep(random.uniform(10, 20))

# Hàm chạy tool cho từng tài khoản
def run_account(email_or_phone, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        login_facebook(driver, email_or_phone, password)
        auto_interact(driver, email_or_phone)
        update_status(email_or_phone, "✅ Hoàn thành")
    except Exception as e:
        update_status(email_or_phone, f"❌ Lỗi: {e}")
    finally:
        driver.quit()  # Đảm bảo trình duyệt đóng sau khi hoàn thành

# Chạy tool đa luồng
def start_tool():
    global running
    running = True
    accounts = load_accounts()

    threads = []
    for account in accounts:
        if not running:
            break
        email_or_phone = account["email_or_phone"]  # Sử dụng đúng khóa "email_or_phone"
        password = account["password"]

        update_status(email_or_phone, "⏳ Đang chạy...")
        thread = threading.Thread(target=run_account, args=(email_or_phone, password))
        threads.append(thread)
        thread.start()
        time.sleep(5)

    for thread in threads:
        thread.join()

# Dừng tool
def stop_tool():
    global running
    running = False
    log("[🛑] Tool đã dừng!")

# Cập nhật trạng thái tài khoản trên GUI
def update_status(email, status):
    for item in tree.get_children():
        values = tree.item(item, "values")
        if values[0] == email:
            tree.item(item, values=(values[0], values[1], status))
            break

# Log hoạt động trên giao diện
def log(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

# Bấm "Lụm!" để tiếp tục sau khi nhập CAPTCHA & 2FA
def confirm_login():
    global waiting_for_login
    waiting_for_login = False
    log("[🚀] Bắt đầu auto nuôi Facebook!")

# Giao diện chính
def gui():
    global tree, log_text
    root = tk.Tk()
    root.title("🚀 Tool Auto Nuôi Acc Facebook 🚀")
    root.geometry("600x500")

    # Frame quản lý tài khoản
    frame_accounts = ttk.LabelFrame(root, text="Quản lý tài khoản")
    frame_accounts.pack(fill="both", padx=10, pady=5)

    tree = ttk.Treeview(frame_accounts, columns=("Email", "Mật khẩu", "Trạng thái"), show="headings")
    tree.heading("Email", text="Email")
    tree.heading("Mật khẩu", text="Mật khẩu")
    tree.heading("Trạng thái", text="Trạng thái")
    tree.column("Email", width=180)
    tree.column("Mật khẩu", width=120)
    tree.column("Trạng thái", width=180)
    tree.pack(fill="both", padx=5, pady=5)

    # Nút thêm/xóa tài khoản
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill="both", padx=10, pady=5)

    def add_account():
        email_or_phone = uid_var.get().strip()  # Đây có thể là email, số điện thoại, hoặc UID
        password = pass_var.get().strip()

        if not email_or_phone or not password:
            print("Lỗi: Thiếu thông tin đăng nhập")
            return

        accounts = load_accounts()

        # Đảm bảo lưu tài khoản với khóa đúng là "email_or_phone"
        new_account = {"email_or_phone": email_or_phone, "password": password}
        accounts.append(new_account)

        save_accounts(accounts)

        tree.insert("", "end", values=(email_or_phone, password, "🟢 Sẵn sàng"))
        uid_var.set("")
        pass_var.set("")



    def delete_account():
        selected_item = tree.selection()
        if selected_item:
            values = tree.item(selected_item, "values")
            email_to_delete = values[0]
            accounts = load_accounts()
            accounts = [acc for acc in accounts if acc["email"] != email_to_delete]
            save_accounts(accounts)
            tree.delete(selected_item)
            log(f"[🗑] Đã xóa tài khoản {email_to_delete}")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản cần xóa!")

    # Khởi tạo các biến cho UID và mật khẩu
    uid_var = tk.StringVar()
    pass_var = tk.StringVar()

    # Thêm vào GUI
    ttk.Label(btn_frame, text="Email/SĐT/UID:").grid(row=0, column=0, padx=5, pady=5)
    ttk.Entry(btn_frame, textvariable=uid_var, width=20).grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(btn_frame, text="Mật khẩu:").grid(row=0, column=2, padx=5, pady=5)
    ttk.Entry(btn_frame, textvariable=pass_var, width=20).grid(row=0, column=3, padx=5, pady=5)
    ttk.Entry(btn_frame, textvariable=pass_var, width=20).grid(row=0, column=3, padx=5, pady=5)
    ttk.Button(btn_frame, text="➕ Thêm", command=add_account).grid(row=0, column=4, padx=5, pady=5)  
    ttk.Button(btn_frame, text="❌ Xóa", command=delete_account).grid(row=0, column=5, padx=5, pady=5)
    # Nút điều khiển tool
    ttk.Button(root, text="▶ Bắt đầu", command=lambda: threading.Thread(target=start_tool).start()).pack(fill="both", padx=10, pady=5)
    ttk.Button(root, text="⏹ Dừng tool", command=stop_tool).pack(fill="both", padx=10, pady=5)

    # Nút "Lụm!" để xác nhận đã nhập CAPTCHA & 2FA
    ttk.Button(root, text="🎯 Lụm!", command=confirm_login).pack(fill="both", padx=10, pady=5)

    # Khung log
    frame_log = ttk.LabelFrame(root, text="Nhật ký hoạt động")
    frame_log.pack(fill="both", padx=10, pady=5)
    log_text = tk.Text(frame_log, height=8)
    log_text.pack(fill="both", padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    gui()