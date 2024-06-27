import tkinter as tk
from tkinter import ttk


class NotificationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightgray", height=50)
        self.pack(side=tk.BOTTOM, fill=tk.X)
        self.notifications = []

    def add_notification(self, message):
        notification_label = ttk.Label(self, text=message, background="lightgreen", anchor="center", padding=(5, 2))
        notification_label.pack(fill=tk.X)
        self.notifications.append(notification_label)

        # Automatically remove the notification after 3 seconds
        self.after(3000, lambda: self.remove_notification(notification_label))

    def remove_notification(self, notification_label):
        notification_label.destroy()
        self.notifications.remove(notification_label)