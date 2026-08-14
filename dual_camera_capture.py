import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import datetime
import time
import threading
import re

class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Dual Camera Application with Live Preview")
        self.master.geometry("1000x700")

        self.available_cams = []
        self.cam1_index = None
        self.cam2_index = None

        self.cap1 = None
        self.cap2 = None
        self.running_preview = False

        self.selected_cam1_var = tk.StringVar(master)
        self.selected_cam2_var = tk.StringVar(master)

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.folder_name_label = tk.Label(self.main_frame, text="Folder Name:", font=("Arial", 12))
        self.folder_name_label.pack(pady=5)
        self.folder_name_entry = tk.Entry(self.main_frame, width=30)
        self.folder_name_entry.insert(0, "photos")
        self.folder_name_entry.pack(pady=5)

        self.camera1_label = tk.Label(self.main_frame, text="Camera Position 1:")
        self.camera1_label.pack()
        self.camera1_menu = tk.OptionMenu(self.main_frame, self.selected_cam1_var, "Select Camera")
        self.camera1_menu.pack(pady=5)

        self.camera2_label = tk.Label(self.main_frame, text="Camera Position 2:")
        self.camera2_label.pack()
        self.camera2_menu = tk.OptionMenu(self.main_frame, self.selected_cam2_var, "Select Camera")
        self.camera2_menu.pack(pady=5)

        self.refresh_cam_button = tk.Button(self.main_frame, text="Refresh Cam View", command=self.restart_preview)
        self.refresh_cam_button.pack(pady=5)

        self.preview_frame = tk.Frame(self.main_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_box1 = tk.Frame(self.preview_frame)
        self.preview_box1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.label_title1 = tk.Label(self.preview_box1, text="Preview 1", font=("Arial", 10))
        self.label_title1.pack()
        self.video_label1 = tk.Label(self.preview_box1)
        self.video_label1.pack(fill=tk.BOTH, expand=True)

        self.preview_box2 = tk.Frame(self.preview_frame)
        self.preview_box2.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.label_title2 = tk.Label(self.preview_box2, text="Preview 2", font=("Arial", 10))
        self.label_title2.pack()
        self.video_label2 = tk.Label(self.preview_box2)
        self.video_label2.pack(fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(self.main_frame, text="Start Taking Pictures", command=self.start_picture_thread)
        self.start_button.pack(pady=10)

        self.restart_button = tk.Button(self.main_frame, text="Restart App", command=self.restart_process)
        self.restart_button.pack(pady=10)

        self.refresh_cameras()

    def refresh_cameras(self):
        self.available_cams = self.detect_cameras()
        cam_names = [f"Camera {i}" for i, _ in self.available_cams]

        def populate_menu(menu_widget, var):
            menu = menu_widget["menu"]
            menu.delete(0, "end")
            if cam_names:
                for name in cam_names:
                    menu.add_command(label=name, command=lambda val=name: var.set(val))
                var.set(cam_names[0])
            else:
                menu.add_command(label="No cameras found", command=lambda: var.set("No cameras found"))
                var.set("No cameras found")

        populate_menu(self.camera1_menu, self.selected_cam1_var)
        populate_menu(self.camera2_menu, self.selected_cam2_var)
        self.update_preview_labels()

    def detect_cameras(self, max_tested=5):
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append((i, f"Camera {i}"))
                cap.release()
        return available

    def update_preview_labels(self):
        self.label_title1.config(text=f"Preview: {self.selected_cam1_var.get()}")
        self.label_title2.config(text=f"Preview: {self.selected_cam2_var.get()}")

    def restart_preview(self):
        # Store current camera indices to check for changes
        new_cam1_index = next((i for i, name in self.available_cams if name == self.selected_cam1_var.get()), None)
        new_cam2_index = next((i for i, name in self.available_cams if name == self.selected_cam2_var.get()), None)

        # Prevent same camera selection
        if new_cam1_index == new_cam2_index and new_cam1_index is not None:
            messagebox.showwarning("Invalid Selection", "Please select different cameras for each position.")
            return

        # Update only if camera indices have changed
        if new_cam1_index != self.cam1_index:
            if self.cap1:
                self.cap1.release()
                self.cap1 = None
            if new_cam1_index is not None:
                self.cap1 = cv2.VideoCapture(new_cam1_index, cv2.CAP_AVFOUNDATION)
                if not self.cap1.isOpened():
                    messagebox.showerror("Error", f"Failed to open Camera {new_cam1_index}")
                    self.cap1 = None
            self.cam1_index = new_cam1_index

        if new_cam2_index != self.cam2_index:
            if self.cap2:
                self.cap2.release()
                self.cap2 = None
            if new_cam2_index is not None:
                self.cap2 = cv2.VideoCapture(new_cam2_index, cv2.CAP_AVFOUNDATION)
                if not self.cap2.isOpened():
                    messagebox.showerror("Error", f"Failed to open Camera {new_cam2_index}")
                    self.cap2 = None
            self.cam2_index = new_cam2_index

        # Update preview labels
        self.update_preview_labels()

        # Start preview if not already running
        if not self.running_preview:
            self.running_preview = True
            self.update_preview()

    def update_preview(self):
        if not self.running_preview:
            return

        def update_label(cap, label):
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img.thumbnail((480, 360), Image.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    label.imgtk = imgtk
                    label.configure(image=imgtk)
                else:
                    label.configure(image='')  # Clear image if frame read fails
            else:
                label.configure(image='')  # Clear image if capture is not available

        update_label(self.cap1, self.video_label1)
        update_label(self.cap2, self.video_label2)

        self.master.after(30, self.update_preview)

    def start_picture_thread(self):
        threading.Thread(target=self.take_pictures_from_both).start()

    def take_pictures_from_both(self):
        folder_name = self.folder_name_entry.get().strip()
        folder_name = re.sub(r'[^\w\-]', '', folder_name)
        if not folder_name:
            folder_name = "photos"
            self.folder_name_entry.delete(0, tk.END)
            self.folder_name_entry.insert(0, folder_name)
            messagebox.showwarning("Invalid Folder Name", "Invalid characters removed. Using 'photos'.")

        downloads_path = os.path.expanduser("~/Downloads")
        photos_folder = os.path.join(downloads_path, folder_name)
        os.makedirs(photos_folder, exist_ok=True)

        for i in range(20):
            ret1, frame1 = self.cap1.read() if self.cap1 and self.cap1.isOpened() else (False, None)
            ret2, frame2 = self.cap2.read() if self.cap2 and self.cap2.isOpened() else (False, None)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            if ret1:
                filename1 = os.path.join(photos_folder, f"pos1_photo_{i+1}_{timestamp}.png")
                cv2.imwrite(filename1, frame1)
                print(f"Saved: {filename1}")
            else:
                print(f"Camera 1 failed at photo {i+1}")

            if ret2:
                filename2 = os.path.join(photos_folder, f"pos2_photo_{i+1}_{timestamp}.png")
                cv2.imwrite(filename2, frame2)
                print(f"Saved: {filename2}")
            else:
                print(f"Camera 2 failed at photo {i+1}")

            time.sleep(5)

        messagebox.showinfo("Done", "Finished taking pictures from both cameras.")

    def restart_process(self):
        self.running_preview = False
        if self.cap1:
            self.cap1.release()
            self.cap1 = None
        if self.cap2:
            self.cap2.release()
            self.cap2 = None
        self.selected_cam1_var.set("Select Camera")
        self.selected_cam2_var.set("Select Camera")
        self.folder_name_entry.delete(0, tk.END)
        self.folder_name_entry.insert(0, "photos")
        self.refresh_cameras()
        self.video_label1.config(image='')
        self.video_label2.config(image='')

    def on_close(self):
        self.running_preview = False
        if self.cap1:
            self.cap1.release()
        if self.cap2:
            self.cap2.release()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
