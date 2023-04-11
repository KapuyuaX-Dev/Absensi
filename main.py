import customtkinter
from tkinter import * #pip install tkinter
import time
import socket
    
class app(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title('Absensi')
        self.geometry('400x200')
        self.resizable(height=False,width=False)
        customtkinter.CTkLabel(self,text="Absensi UKRO UNP",font=('arial',16)).place(anchor=CENTER,relx=0.5,rely=0.125)
        self.connect = customtkinter.CTkButton(self,text='Connect',width=80).place(anchor=CENTER,relx=0.5,rely=0.25)
        self.menu_upload = customtkinter.CTkButton(self,text='upload',width=80, command=self.upload).place(anchor=CENTER,relx=0.15,rely=0.42)
        self.menu_download = customtkinter.CTkButton(self,text='download',width=80).place(anchor=CENTER,relx=0.15,rely=0.62)

    def upload(self):
        self.uploadWindow = customtkinter.CTkToplevel(self)
        self.uploadwindow.geometry('400x200')
        customtkinter.CTkLabel(self.uploadWindow,text="asd",font=('arial',16)).place(anchor=CENTER,relx=0.5,rely=0.125)


if __name__ == "__main__":
    main = app()
    main.mainloop()