import customtkinter
from CTkMessagebox import CTkMessagebox
from PIL import Image,ImageTk
import gspread
from google.oauth2.service_account import Credentials
import datetime
import time
import requests
import io
import threading
import tkinter


SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("newonew.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet_name = client.open("Attendance-ReyDatamind")
sheet = sheet_name.worksheet("user & pass")
sheet_attendance = sheet_name.worksheet("attendance")

class User:

    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.geometry("800x600")
        self.root.title("User Authentication")
        self.user_UI()
        # self.Home_button = customtkinter.CTkButton(self.root, text="Home", width=50, height=25, command=lambda: [self.login_page_frame.destroy(), self.login_page(), self.user_UI()])
        # self.Home_button.place(x=10, y=10)
        self.root.mainloop()
        
    def last_record(self):
        self.name_col = sheet_attendance.col_values(1)
        self.last_col_num = len(self.name_col)
        self.last_col_name = sheet_attendance.row_values(self.last_col_num)
        self.last_active_lb  = customtkinter.CTkLabel(self.login_page_frame, text=("Last Record:"+ self.last_col_name[0] + ":" + self.last_col_name[3]))
        self.last_active_lb.grid(row=5, column=0)


    def update_clock(self):
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        Formated_time_date = "Time: " + current_time  + "\n\nDate: " + current_date
        self.label_time_date.configure(text=Formated_time_date)
        self.root.after(1000, self.update_clock)
    def _create_image_from_response(self, response):
        image_data = response.content
        logo_pil_image = Image.open(io.BytesIO(image_data))
        logo = customtkinter.CTkImage(
            light_image=logo_pil_image,
            dark_image=logo_pil_image,
            size=(150, 150)
        )
        return logo

    def image_load(self, username):
        logo = None
        base_url = "https://raw.githubusercontent.com/Dharani-111/Reydatamind/main/Images/"
        try:
            user_image_url = f"{base_url}{username}.jpg"
            response = requests.get(user_image_url)
            response.raise_for_status() 
            logo = self._create_image_from_response(response)

        except requests.exceptions.RequestException as e:
            print(f"Failed to load user image for '{username}': {e}. Loading placeholder.")
            try:
                placeholder_url = f"{base_url}Placeholder_photo.jpg"
                response = requests.get(placeholder_url)
                response.raise_for_status() # Good practice to check this too
                logo = self._create_image_from_response(response)
            except requests.exceptions.RequestException as placeholder_e:
                print(f"CRITICAL: Failed to load placeholder image: {placeholder_e}")
                return 
        if logo:
            self.logo_image.configure(image=logo, corner_radius=60)

    
    def checking_login_status(self, username):
        try:
            all_data = sheet_attendance.get_all_values()[1:]
            last_found_status = None
            for row in all_data:
                if row[0] == username:
                    user_login = row[2] if len(row) > 2 else ""
                    user_logout = row[3] if len(row) > 3 else ""                    
                    last_found_status = {"login": user_login, "logout": user_logout}                        
            if last_found_status:
                if last_found_status["login"] and last_found_status["logout"]:
                    self.login_button.configure(state="normal")
                    self.logout_button.configure(state="disabled")
                else:
                    self.login_button.configure(state="disabled")
                    self.logout_button.configure(state="normal")
            else:                
                self.login_button.configure(state="normal")
                self.logout_button.configure(state="disabled")                
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")
            self.login_button.configure(state="normal")
            self.logout_button.configure(state="disabled")
            
    def login_time(self,username):
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        sheet_attendance.append_row([username, current_date, current_time, ""])
        self.login_button.configure(state="disabled")
        self.logout_button.configure(state="normal")
        CTkMessagebox(title="Login", message="Login successful!", icon="check")
        return True
    def logout_time(self, username):        
        try:
            current_time = datetime.datetime.now().strftime("%I:%M:%S %p")        
            found_cells = sheet_attendance.findall(username, in_column=1)            
            if not found_cells:
                CTkMessagebox(title="Warning", message=f"User '{username}' not found.", icon="warning")
                return False        
            for cell in reversed(found_cells):
                user_row = sheet_attendance.row_values(cell.row)
                user_login = user_row[2] if len(user_row) > 2 else ""
                user_logout = user_row[3] if len(user_row) > 3 else ""            
                if user_login and not user_logout:                    
                    sheet_attendance.update_cell(cell.row, 4, current_time)
                    self.login_button.configure(state="normal")
                    self.logout_button.configure(state="disabled")
                    CTkMessagebox(title="Logout", message="Logout successful!", icon="check")                    
                    return True            
            CTkMessagebox(title="Info", message=f"User '{username}' is not currently logged in.", icon="info")
            return False
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")
            return False
    def login_page(self,username):
        self.root.geometry("1200x800")
        self.login_page_frame = customtkinter.CTkFrame(self.root, width=1000, height=500, corner_radius=10)
        self.login_page_frame.pack(pady=(20,50))
        self.logo=Image.open("Images/REYDM_LOGO.png")
        self.logo=self.logo.resize((250,60))
        self.logo=ImageTk.PhotoImage(self.logo)
        self.logo_image=customtkinter.CTkLabel(self.login_page_frame,image="",text="")
        self.logo_image.grid(row=0,column=0,columnspan=4,pady=(20,10))
        self.image_load(username)
        self.name_label = customtkinter.CTkLabel(self.login_page_frame, text=( "Name: " + username), font=customtkinter.CTkFont(family="Arial", size=20, weight="bold"))
        self.name_label.grid(row=1, column=0,columnspan=4,pady=20)
        self.label_time_date = customtkinter.CTkLabel(self.login_page_frame, text=" ", font=customtkinter.CTkFont(family="Arial", size=20, weight="bold"))
        self.label_time_date.grid(row=2, column=0,columnspan=4)
        self.update_clock()
        self.login_button = customtkinter.CTkButton(self.login_page_frame, text="Login", width=100, height=30, command=lambda: self.login_time(username))
        self.login_button.grid(row=3, column=1, pady=20)
        self.logout_button = customtkinter.CTkButton(self.login_page_frame, text="Logout", width=100, height=30, command=lambda: self.logout_time(username))
        self.logout_button.grid(row=3, column=2,  pady=20)
        self.blank_space = customtkinter.CTkLabel(self.login_page_frame, text=" ", font=customtkinter.CTkFont(family="Arial", size=2, weight="bold"), width=500)
        self.blank_space.grid(row=4, column=0,columnspan=4)
        self.checking_login_status(username)
        self.last_record()

        # time.sleep(2)
    def pass_show_hide(self):
        self.show_img=Image.open("Images/Show.png")
        self.show_img=self.show_img.resize((10,10))
        self.show_img=ImageTk.PhotoImage(self.show_img)
        self.hide_img=Image.open("Images/Hide.png")
        self.hide_img=self.hide_img.resize((10,10))
        self.hide_img=ImageTk.PhotoImage(self.hide_img)
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.bt_show_hide.configure(image=self.hide_img)
        else:
            self.password_entry.configure(show="*")
            self.bt_show_hide.configure(image=self.show_img)
    def authenticate_user(self, username, password):
        try:
            all_records = sheet.get_all_values()
            user_data = all_records[1:] 
            for row in user_data:
                sheet_username = row[0]
                if sheet_username == username:
                    sheet_password = row[1]
                    if sheet_password == password:
                        CTkMessagebox(title="Success", message="Authentication successful! ✅", icon="check")
                        self.user_frame.destroy()
                        self.login_page(username)
                        return True  
                    else:
                        CTkMessagebox(title="Error", message="Authentication failed. ❌ Incorrect password.", icon="cancel")
                        return False 
            CTkMessagebox(title="Error", message="Authentication failed. ❌ Invalid username.", icon="cancel")
            return False
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")
            return False
    def user_UI(self):
        self.show_img=Image.open("Images/Show.png")
        self.show_img=self.show_img.resize((10,10))
        self.show_img=ImageTk.PhotoImage(self.show_img)
        self.user_frame = customtkinter.CTkFrame(self.root, width=700, height=500, corner_radius=10)
        self.user_frame.pack(pady=(50,0))
        self.logo=Image.open("Images/REYDM_LOGO.png")
        self.logo=self.logo.resize((250,60))
        self.logo=ImageTk.PhotoImage(self.logo)
        self.logo_image=customtkinter.CTkLabel(self.user_frame,image=self.logo,text="")
        self.logo_image.grid(row=0,column=0,columnspan=3,pady=(20,10))
        self.lb_username = customtkinter.CTkLabel(self.user_frame, text="Username:", font=("Arial", 20))
        self.lb_username.grid(row=1, column=0, padx=20, pady=20)
        self.username_entry = customtkinter.CTkEntry(self.user_frame, width=200, height=30)
        self.username_entry.grid(row=1, column=1, padx=20, pady=20)
        self.lb_password = customtkinter.CTkLabel(self.user_frame, text="Password:", font=("Arial", 20))
        self.lb_password.grid(row=2, column=0, padx=20, pady=20)
        self.password_entry = customtkinter.CTkEntry(self.user_frame, width=200, height=30, show="*")
        self.password_entry.grid(row=2, column=1, padx=20, pady=20, sticky="e")
        self.bt_show_hide = customtkinter.CTkButton(self.user_frame, text="", image=self.show_img, width=30, height=30, command=self.pass_show_hide)
        self.bt_show_hide.grid(row=2, column=2, padx=15, pady=15)
        self.btn_login = customtkinter.CTkButton(self.user_frame, text="Sign in", width=100, height=30, command=lambda: self.authenticate_user(self.username_entry.get(), self.password_entry.get()))
        self.btn_login.grid(row=3, column=0, columnspan=3, pady=20)
        time.sleep(3)
        
        
        
        


        

        
User()
