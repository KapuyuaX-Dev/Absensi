import customtkinter
from tkinter import * #pip install tkinter
import time
import socket
import threading

class app(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title('Absensi')
        self.geometry('400x220')
        self.resizable(height=False,width=False)

        #local Variable
        self.__radioWiFiMode = IntVar(0)
        self.__networkState={
            0:"disabled",
            1:"normal"
        }
        self.WiFiMode = 0

        self.__homepage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__uploadpage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__networkpage = customtkinter.CTkFrame(self,width=400, height=220)

        for frame in (self.__homepage,self.__uploadpage,self.__networkpage):
            frame.grid(row=0, column=0, sticky='nsew')

    def homepage(self):
        customtkinter.CTkLabel(self.__homepage,text="Absensi UKRO UNP",font=('arial',16)).place(anchor=CENTER,relx=0.5,rely=0.125)
        customtkinter.CTkButton(self.__homepage,text='Connect',width=80).place(anchor=CENTER,relx=0.13,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='upload',width=80, command=self.uploadPage).place(anchor=CENTER,relx=0.13,rely=0.72)
        customtkinter.CTkButton(self.__homepage,text='download',width=80).place(anchor=W,relx=0.28,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='update',width=80).place(anchor=W,relx=0.28,rely=0.72)
        customtkinter.CTkButton(self.__homepage,text='time',width=80).place(anchor=W,relx=0.53,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='network',width=80, command=self.networkPage).place(anchor=W,relx=0.53,rely=0.72)
        customtkinter.CTkButton(self.__homepage,text='reboot',width=80).place(anchor=W,relx=0.78,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='reset',width=80).place(anchor=W,relx=0.78,rely=0.72)
        self.__homepage.tkraise()
        self.update()

    def uploadPage(self):
        customtkinter.CTkLabel(self.__uploadpage,text="Upload ke Alat",font=('arial',20)).place(anchor=CENTER,relx=0.5,rely=0.115)
        customtkinter.CTkButton(self.__uploadpage,text='return',width=80, command=self.homepage).place(anchor=W,relx=0.51,rely=0.9)
        self.entryName = customtkinter.CTkEntry(self.__uploadpage,placeholder_text="Nama Lengkap", width=300)
        self.entryName.place(anchor=W, relx=0.15, rely=0.3)
        self.entryNIA = customtkinter.CTkEntry(self.__uploadpage,placeholder_text="Nomor Induk Anggota", width=300)
        self.entryNIA.place(anchor=W, relx=0.15, rely=0.45)
        self.getNUID = customtkinter.CTkButton(self.__uploadpage,text='Get NUID ID Card',width=300).place(anchor=W,relx=0.15,rely=0.6)
        customtkinter.CTkButton(self.__uploadpage,text='Send',width=80).place(anchor=E,relx=0.49,rely=0.9)
        self.__uploadpage.tkraise()
        self.update()

    def networkPage(self):
        customtkinter.CTkLabel(self.__networkpage,text="WiFi Setting",font=('arial',16)).place(anchor=CENTER,relx=0.5,rely=0.115)
        customtkinter.CTkRadioButton(self.__networkpage,text="AP Mode",command=self.radioEvent,variable=self.__radioWiFiMode,value=0).place(anchor=W,relx=0.2,rely=0.3)
        customtkinter.CTkRadioButton(self.__networkpage,text="AP+STA Mode",command=self.radioEvent,variable=self.__radioWiFiMode,value=1).place(anchor=W,relx=0.5,rely=0.3)
        customtkinter.CTkLabel(self.__networkpage,text="Access Point",font=('arial',12)).place(anchor=CENTER,relx=0.3,rely=0.45)
        customtkinter.CTkLabel(self.__networkpage,text="Station",font=('arial',12)).place(anchor=CENTER,relx=0.7,rely=0.45)
        self.APSSIDEntry = customtkinter.CTkEntry(self.__networkpage,width=150,placeholder_text="SSID")
        self.APSSIDEntry.place(anchor=CENTER,relx=0.3,rely=0.6)
        self.APPSWEntry = customtkinter.CTkEntry(self.__networkpage,width=150,placeholder_text="Password")
        self.APPSWEntry.place(anchor=CENTER,relx=0.3,rely=0.75)
        self.STASSIDEntry = customtkinter.CTkEntry(self.__networkpage,width=150,placeholder_text="SSID", state=self.__networkState.get(self.WiFiMode))
        self.STASSIDEntry.place(anchor=CENTER,relx=0.7,rely=0.6)
        self.STAPSWEntry = customtkinter.CTkEntry(self.__networkpage,width=150,placeholder_text="Password",state=self.__networkState.get(self.WiFiMode))
        self.STAPSWEntry.place(anchor=CENTER,relx=0.7,rely=0.75)
        customtkinter.CTkButton(self.__networkpage,text='Save',width=80).place(anchor=E,relx=0.49,rely=0.9)
        customtkinter.CTkButton(self.__networkpage,text='return',width=80, command=self.homepage).place(anchor=W,relx=0.51,rely=0.9)
        self.__networkpage.tkraise()
        self.update()

    def radioEvent(self):
        self.WiFiMode = self.__radioWiFiMode.get()
        self.STASSIDEntry.configure(state=self.__networkState.get(self.WiFiMode))
        self.STAPSWEntry.configure(state=self.__networkState.get(self.WiFiMode))

if __name__ == "__main__":
    main = app()
    main.homepage()
    main.mainloop()