import customtkinter
from tkinter import *
from tkinter import messagebox
import time
import socket
import threading
from datetime import datetime
import os
import json

class socketCon():
    def __init__(self, host, port,funcRecv):
        self.__host = host
        self.__port = port
        self.__funcRecv = funcRecv
        self.__s = socket.socket()
        self.connected = False

    def connect(self):
        print('a')
        self.__s.connect((self.__host,self.__port))
        self.connected = True
        threading.Thread(target=self.listenIncomingMessage).start()

    def disconnect(self):
        self.__s.close()
        self.connected=False

    def sendRequest(self,msg):
        _msg = bytes(msg,'UTF-8')
        self.__s.sendall(_msg)
    
    def download(self):
        _msg = 'req:log'
        self.sendRequest(_msg)

    def sendNetwork(self,data):
        _msg = f'setWifi:{data}'
        self.sendRequest(_msg)

    def sendTime(self,time):
        _msg = f'setTime:{time}'
        self.sendRequest(_msg)

    def sendReboot(self):
        self.sendRequest('req:ESPReboot')

    def sendReset(self):
        self.sendRequest('req:ESPEraseData')

    def getName(self):
        self.sendRequest('req:name')

    def listenIncomingMessage(self):
        while self.connected:
            try:
                self.__data = self.__s.recv(1080).decode('UTF-8')
                self.__funcRecv(self.__data)

            except:
                pass

class app(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title('Absensi')
        self.geometry('400x220')
        self.resizable(height=False,width=False)

        #socket con
        self.__coms = None

        #local Variable
        self.__time = None
        self.__radioWiFiMode = IntVar(0)
        self.__networkState={
            1:"disabled",
            2:"normal"
        }
        self.WiFiMode = 1
        self.__radioWiFiMode.set(self.WiFiMode)

        self.__listNama = [
            {
                'Nama':'Select',
                'Nia':'',
                'NUID':''
            }
        ]

        self.__homepage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__uploadpage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__networkpage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__timepage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__updatepage = customtkinter.CTkFrame(self,width=400, height=220)
        self.__downloadpage = customtkinter.CTkFrame(self,width=400, height=220)

        for frame in (self.__homepage,self.__uploadpage,self.__networkpage, self.__timepage,self.__updatepage,self.__downloadpage):
            frame.grid(row=0, column=0, sticky='nsew')

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.__coms is not None:
            if self.__coms.connected:
                self.__coms.disconnect()
        self.destroy()

    def connectionRecv(self,_msg):
        print(_msg)
        if _msg.find(":")>0:
            _msg = _msg.split(':')

    def makeConnection(self):
        if self.__coms:
            if self.__coms.connected:
                self.__coms.disconnect()
                self.connectButton.configure(text='Connect')

            else:
                self.__coms = socketCon('192.168.4.1',80,self.connectionRecv)
                self.__coms.connect()
                self.connectButton.configure(text='Disconnect')
        
        else:
            self.__coms = socketCon('192.168.4.1',80,self.connectionRecv)
            self.__coms.connect()
            self.connectButton.configure(text='Disconnect')

    def handleDownload(self):
        self.downloadPage()
        if self.__coms is not None:
            if self.__coms.connected:
                self.__coms.download()
        

    def downloadPage(self):
        customtkinter.CTkButton(self.__downloadpage,text='return',width=80, command=self.homepage).place(anchor=CENTER,relx=0.5,rely=0.9)
        self.__downloadpage.tkraise()
        self.update()

    def homepage(self):
        customtkinter.CTkLabel(self.__homepage,text="Absensi UKRO UNP",font=('arial',16)).place(anchor=CENTER,relx=0.5,rely=0.125)
        context = 'Connect'
        if self.__coms is not None:
            if self.__coms.connected:
                context = 'Disconnect'
        self.connectButton = customtkinter.CTkButton(self.__homepage,text=context ,width=80,command=self.makeConnection)
        self.connectButton.place(anchor=CENTER,relx=0.13,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='upload',width=80, command=self.uploadPage).place(anchor=CENTER,relx=0.13,rely=0.72)
        customtkinter.CTkButton(self.__homepage,text='download',width=80,command=self.handleDownload).place(anchor=W,relx=0.28,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='update',width=80,command=self.updatePage).place(anchor=W,relx=0.28,rely=0.72)
        customtkinter.CTkButton(self.__homepage,text='time',width=80, command=self.timePage).place(anchor=W,relx=0.53,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='network',width=80, command=self.networkPage).place(anchor=W,relx=0.53,rely=0.72)
        customtkinter.CTkButton(self.__homepage,text='reboot',width=80,command=self.handleReboot).place(anchor=W,relx=0.78,rely=0.5)
        customtkinter.CTkButton(self.__homepage,text='reset',width=80,command=self.handleFactoryReset).place(anchor=W,relx=0.78,rely=0.72)
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
        customtkinter.CTkRadioButton(self.__networkpage,text="AP Mode",command=self.radioEvent,variable=self.__radioWiFiMode,value=1).place(anchor=W,relx=0.2,rely=0.3)
        customtkinter.CTkRadioButton(self.__networkpage,text="AP+STA Mode",command=self.radioEvent,variable=self.__radioWiFiMode,value=2).place(anchor=W,relx=0.5,rely=0.3)
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
        customtkinter.CTkButton(self.__networkpage,text='Save',width=80,command=self.saveNetwork).place(anchor=E,relx=0.49,rely=0.9)
        customtkinter.CTkButton(self.__networkpage,text='return',width=80, command=self.homepage).place(anchor=W,relx=0.51,rely=0.9)
        self.__networkpage.tkraise()
        self.update()

    def saveNetwork(self):
        self.__data = {
            "wifiMode":self.WiFiMode,
            "AP":{
                "SSID":self.APSSIDEntry.get(),
                "psw":self.APPSWEntry.get(),
            },
            "STA":{
                "SSID":self.STASSIDEntry.get(),
                "psw":self.STAPSWEntry.get(),
            }
        }
        self.__jsonObject = json.dumps(self.__data)

        maindir = os.getcwd()
        if maindir.find('Absensi') < 0 :
            maindir = os.path.join(maindir,'Absensi')

        with open(f'{maindir}/data/network.txt','w') as f:
            f.write(self.__jsonObject)

        if self.__coms is not None:
            if self.__coms.connected:
                self.__coms.sendNetwork(self.__jsonObject)

        self.homepage()

    def radioEvent(self):
        self.WiFiMode = self.__radioWiFiMode.get()
        self.STASSIDEntry.configure(state=self.__networkState.get(self.WiFiMode),placeholder_text="SSID")
        self.STAPSWEntry.configure(state=self.__networkState.get(self.WiFiMode),placeholder_text="Password")

    def timePage(self):
        customtkinter.CTkLabel(self.__timepage,text="Current Time",font=('arial',16)).place(anchor=CENTER,relx=0.5,rely=0.115)
        self.__timeLabel = customtkinter.CTkLabel(self.__timepage,text='',font=('arial',16))
        self.__timeLabel.place(anchor=CENTER,relx=0.5,rely=0.22)
        customtkinter.CTkButton(self.__timepage,text='Save',width=80,command=self.setTime).place(anchor=E,relx=0.49,rely=0.9)
        customtkinter.CTkButton(self.__timepage,text='return',width=80, command=self.homepage).place(anchor=W,relx=0.51,rely=0.9)
        self.getTime()
        self.__timepage.tkraise()
        self.update()

    def setTime(self):
        if self.__coms is not None:
            if self.__coms.connected:
                self.__now = datetime.now()
                self.__coms.sendTime(self.__now.strftime('%Y,%m,%d,%H,%M,%S'))
                self.homepage()

    def getTime(self):
        self.__now = datetime.now()
        self.__time = self.__now.strftime("%m/%d/%Y, %H:%M:%S")
        self.__timeLabel.configure(text=self.__time)
        self.after(1000,self.getTime)

    def updatePage(self):
        if self.__coms is not None:
            if self.__coms.connected:
                self.__coms.getName()
                
        customtkinter.CTkLabel(self.__updatepage,text="Update Data",font=('arial',16)).place(anchor=W,relx=0.15,rely=0.115)

        self.optionNama = customtkinter.CTkOptionMenu(self.__updatepage,width=80, values=[x['Nama'] for x in self.__listNama]).place(anchor=W,relx=0.5,rely=0.115)

        self.entryUName = customtkinter.CTkEntry(self.__updatepage,placeholder_text="Nama Lengkap", width=300)
        self.entryUName.place(anchor=W, relx=0.15, rely=0.3)
        self.entryUNIA = customtkinter.CTkEntry(self.__updatepage,placeholder_text="Nomor Induk Anggota", width=300)
        self.entryUNIA.place(anchor=W, relx=0.15, rely=0.45)
        self.labelUNUID = customtkinter.CTkLabel(self.__updatepage, text='NUID:')
        self.labelUNUID.place(anchor=W,relx=0.15,rely=0.6)
        self.getNUID = customtkinter.CTkButton(self.__updatepage,text='Get new NUID ID Card',width=20).place(anchor=W,relx=0.5,rely=0.6)

        customtkinter.CTkButton(self.__updatepage,text='Save',width=80).place(anchor=E,relx=0.49,rely=0.9)
        customtkinter.CTkButton(self.__updatepage,text='return',width=80, command=self.homepage).place(anchor=W,relx=0.51,rely=0.9)

        self.__updatepage.tkraise()
        self.update()

    def handleReboot(self):
        cmd = messagebox.askquestion("Reboot", "Reboot Machine?",icon = 'warning')
        if cmd == 'yes':
            if self.__coms is not None:
                if self.__coms.connected:
                    self.__coms.sendReboot()
                    self.makeConnection()
            messagebox.showinfo('Reboot',"Rebooting...")      

    def handleFactoryReset(self):
        cmd = messagebox.askquestion("Factory Reset", "SERIUS ANGKU?",icon = 'warning')
        if cmd == 'yes':
            cmd = messagebox.askquestion("Factory Reset", "DOLAH DATA HILANG HA, SERIUS?",icon = 'warning')
            if cmd == 'yes':
                cmd = messagebox.askquestion("Factory Reset", "SERIUS LAH!?",icon = 'warning')
                if cmd == 'yes':
                    if self.__coms is not None:
                        if self.__coms.connected:
                            self.__coms.sendReset()
                    self.on_closing()
                

if __name__ == "__main__":
    main = app()
    main.homepage()
    maindir = os.getcwd()
    if maindir.find('Absensi') < 0 :
        maindir = os.path.join(maindir,'Absensi')
    if not os.path.isfile(f'{maindir}/data/nama.txt'):
        with open(f'{maindir}/data/nama.txt','w') as f:
            pass

    if not os.path.isfile(f'{maindir}/data/log.json'):
        with open(f'{maindir}/data/log.json','w') as f:
            pass
    
    main.mainloop()