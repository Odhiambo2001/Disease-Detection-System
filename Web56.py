import numpy
import sys
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os.path
import subprocess
from tkinter import messagebox


class Util:
    @staticmethod
    def get_button(window, text, color, command, fg='white'):
        button = tk.Button(window, text=text, command=command, bg=color, fg=fg)
        return button

    @staticmethod
    def get_img_label(window):
        label = tk.Label(window)
        return label

    @staticmethod
    def get_text_label(window, text):
        label = tk.Label(window, text=text)
        label.config(font=("sans-serif", 21), justify="left")
        return label

    @staticmethod
    def msg_box(title, message, icon=None, buttons=None):
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        if buttons:
            result = messagebox.askquestion(title, message, icon=icon, type=messagebox.YESNO)
        else:
            result = messagebox.showinfo(title, message, icon=icon)

        root.destroy()
        return result

    @staticmethod
    def unknown_user_please_register_new_user_or_try_again():
        unknown_user_window = tk.Toplevel()
        unknown_user_window.geometry('400x200+470+250')

        success_label = tk.Label(unknown_user_window, text='Unknown User! Please register new user or try again',
                                 font=("sans-serif", 16))
        success_label.pack(pady=20)

        accept_button = tk.Button(unknown_user_window, text='Accept', command=unknown_user_window.destroy, bg='green',
                                  fg='white')
        accept_button.pack()

        unknown_user_window.mainloop()


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry('1200x520+350+100')

        self.most_recent_capture_pil = None
        self.captured_image_path = None
        self.logged_in_users = set()

        # Use an absolute path for the db directory
        self.db_folder = './db'  # Change this folder name to your preference
        self.db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.db_folder)
        self.create_db_directory()  # Ensure the db directory is created

        self.login_button = Util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button.place(x=750, y=300)

        self.register_new_user_button = Util.get_button(
            self.main_window, 'register new user', 'gray', self.register_new_user, fg='black')
        self.register_new_user_button.place(x=750, y=400)
        self.register_new_user_capture = None

        self.webcam_label = Util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)
        self.add_webcam(self.webcam_label)

        self.log_path = './log.txt'

    def create_db_directory(self):
        if not os.path.exists(self.db_dir):
            try:
                os.mkdir(self.db_dir)
                print(f"Successfully created the directory {self.db_dir}")
            except OSError:
                print(f"Creation of the directory {self.db_dir} failed")

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)
        self._label.after(20, self.process_webcam)


    def login(self):
        unknown_img_path = './.tap.jpg'
        cv2.imwrite(unknown_img_path, numpy.array(self.most_recent_capture_pil))
        self.captured_image_path = unknown_img_path

        process = subprocess.Popen(['face_recognition', self.db_dir, unknown_img_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        if process.returncode == 0:
            print("Face recognition output:", output)
            name = output.split(' ')[1][:-3]
        else:
            print("Face recognition failed with error:", error)
            name = "unknown_person"  # Default value if face recognition fails

        if name in ['unknown_person', 'no_person_found']:
            self.display_unknown_user_window(name)
        else:
            user_image_path = os.path.join(self.db_dir, '{}.jpg'.format(name))
            if os.path.exists(user_image_path):
                self.display_welcome_window(name)
            else:
                self.display_unknown_user_window(name)
        os.remove(unknown_img_path)

    def display_unknown_user_window(self, username):
        unknown_user_window = tk.Toplevel(self.main_window)
        unknown_user_window.geometry('400x200+470+250')

        unknown_user_label = tk.Label(unknown_user_window, text=f'Unknown User! Please register or try again.',
                                      font=("sans-serif", 16))
        unknown_user_label.pack(pady=20)

        accept_button = Util.get_button(unknown_user_window, 'Accept', 'green', unknown_user_window.destroy)
        accept_button.pack()

    def display_welcome_window(self, username):
        welcome_window = tk.Toplevel(self.main_window)
        welcome_window.geometry('400x200+470+250')

        welcome_label = tk.Label(welcome_window, text=f'Welcome, {username}!', font=("sans-serif", 16))
        welcome_label.pack(pady=20)

        accept_button = Util.get_button(welcome_window, 'Accept', 'green', welcome_window.destroy)
        accept_button.pack()

    def register_new_user(self):
        
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry('1200x520+370+120')
        self.accept_button_register_new_user_window = Util.get_button(
            self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = Util.get_button(
            self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = Util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = tk.Entry(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = Util.get_text_label(
            self.register_new_user_window, "Please, \nInput Username:")
        self.text_label_register_new_user.place(x=750, y=70)


    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        if self.most_recent_capture_pil is not None:
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            self.register_new_user_capture = numpy.array(
                self.most_recent_capture_pil)

    def user_was_registered_successfully(self):
        self.user_was_registered_successfully_window = tk.Toplevel(
            self.main_window)
        self.user_was_registered_successfully_window.geometry('400x200+470+250')

        success_label = tk.Label(
            self.user_was_registered_successfully_window, text='User was registered successfully!', font=("sans-serif", 16))
        success_label.pack(pady=20)

        accept_button = Util.get_button(
            self.user_was_registered_successfully_window, 'Accept', 'green', self.user_was_registered_successfully_window.destroy)
        accept_button.pack()

    def accept_register_new_user(self):
        #Check if a face is detected before proceeding
        if self.most_recent_capture_pil is None:
            Util.msg_box('No Face Detected','No face detected. Please try again.')
            return
        self.create_db_directory()
        name = self.entry_text_register_new_user.get()

        if name:
            user_image_path = os.path.join(
                self.db_dir, '{}.jpg'.format(name))

            if os.path.exists(user_image_path):
                Util.msg_box('Error!', 'User {} is already registered.'.format(name))

            else:
                if self.register_new_user_capture is not None:
                    # Convert PIL Image back to Numpy array
                    register_new_user_capture_np = numpy.array(self.register_new_user_capture)
                    cv2.imwrite(user_image_path, cv2.cvtColor(register_new_user_capture_np, cv2.COLOR_RGB2BGR))
                    self.user_was_registered_successfully()
                else:
                    Util.msg_box(
                        'Error!', 'Capture is empty. Please try again.')

            self.register_new_user_window.destroy()
        else:
            Util.msg_box('Error!', 'Username cannot be empty. Please enter a username.')

    def accept_unknown_user(self):
        result = Util.msg_box('Registration Required', 'Unknown user. Would you like to register?', buttons=['Yes', 'No'])
        if result == 'Yes':
            self.register_new_user()
        else:
            print("Unknown user not registered.")

    def start(self):
        self.main_window.mainloop()


if __name__ == '__main__':
    app = App()
    app.start()
