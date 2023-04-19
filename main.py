import customtkinter
from tkinter import *
from tkinter import messagebox
import time
import socket
import threading
from datetime import datetime
import os
import json

'''
data = [
    'Rifqi Firlian Pratama,18323070,13-04-2023',
    'Hanifah Nur Ismail,1923141,13-04-2023',
    'Rifqi Firlian Pratama,18323070,14-04-2023'
]

d = {}

for item in data:
    parts = item.split(',')
    date = parts[2]
    name = parts[0]
    nia = int(parts[1])
    if date not in d:
        d[date] = {'attendance': []}
    d[date]['attendance'].append({'name': name, 'nia': nia})

output = [{'date': date, 'attendance': d[date]['attendance']} for date in d]

print(output)
'''

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
        self.sendRequest('req:status')
        self.__timeout = time.time() + 2
        while time.time() < self.__timeout:
            try:
                self.__data = self.__s.recv(1080).decode('UTF-8').split(':')
                if self.__data[0]=='Status' and self.__data[1] == 'ok':
                    self.connected = True
                    threading.Thread(target=self.listenIncomingMessage).start()
                    return True
                    break
            except:
                pass       
        return False

    def disconnect(self):
        self.__s.close()
        self.connected=False

    def sendRequest(self,msg):
        _msg = bytes(msg,'UTF-8')
        self.__s.sendall(_msg)
    
    def download(self):
        _msg = 'req:log'
        self.sendRequest(_msg)

    def sendNama(self,**kwargs):
        try:
            _msg = f"save:{kwargs['nama']},{kwargs['nia']},{kwargs['uid']}"
            self.sendRequest(_msg)

        except Exception as e:
            print(e)

    def updateNama(self,names):
        _msg = f"update:{names}"
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

    def getNUID(self):
        self.sendRequest('req:NUID')

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
        self.optionMenuVar = customtkinter.StringVar(value="Select")
        self.__listNama = [
            {
                'Nama':'Select',
                'Nia':'',
                'NUID':''
            }
        ]

        self.__NUID = ''


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
                self.__coms.sendReboot()
                self.__coms.disconnect()
        self.destroy()

    def processLogData(self,logData):
        self.__logData = logData.split('\n')
        d = {}
        dataJson = None
        maindir = os.getcwd()
        if maindir.find('Absensi') < 0 :
            maindir = os.path.join(maindir,'Absensi')

        with open(f'{maindir}/data/log.json','r') as f:
            dataJson = json.loads(f.read())

        for data in self.__logData:
            data = data.split(',')
            if len(data)>1:
                if data[2] not in d:
                    d[data[2]] = {'attendance': []}
                d[data[2]]['attendance'].append({'name': data[0], 'nia': data[1]})

        for date in d:
            dataJson.append({'date': date, 'attendance': d[date]['attendance']})
        
        print(dataJson)
        
        with open(f'{maindir}/data/log.json','w') as f:
            json.dump(dataJson,f,indent=4)
    
    def processName(self,names):
        self._names = names.split('\n')
        self.__listNama = [
            {
                'Nama':'Select',
                'Nia':'',
                'NUID':''
            }
        ]
        for name in self._names:
            name = name.rstrip().split(',')
            print(name)
            if len(name) > 1:
                self.__listNama.append({
                'Nama':name[0],
                'Nia':name[1],
                'NUID':name[2]
            })

        self.optionNama.configure(values=[x['Nama'] for x in self.__listNama])

    def connectionRecv(self,_msg):
        print(_msg)
        if _msg.find(":")>0:
            _msg = _msg.split(':')

            if _msg[0] == 'UID':
                self.__NUID = _msg[1]
                try:
                    self.buttonNUID.configure(text = self.__NUID)
                except: pass
                try:
                    self.labelUNUID.configure(text=f'NUID:{self.__NUID}')
                except: pass
            
            elif _msg[0] == 'log':
                threading.Thread(target=self.processLogData,args=(_msg[1],)).start()

            elif _msg[0] == 'name':
                #self.processName(_msg[1])
                threading.Thread(target=self.processName,args=(_msg[1],)).start()

    def makeConnection(self):
        if self.__coms:
            if self.__coms.connected:
                self.__coms.disconnect()
                self.connectButton.configure(text='Connect')

            else:
                self.__coms = socketCon('192.168.4.1',80,self.connectionRecv)
                if self.__coms.connect():
                    self.connectButton.configure(text='Disconnect')
        
        else:
            self.__coms = socketCon('192.168.4.1',80,self.connectionRecv)
            if self.__coms.connect():
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
        self.buttonNUID = self.getNUID = customtkinter.CTkButton(self.__uploadpage,text='Get NUID ID Card',width=300,command=self.getUID)
        self.buttonNUID.place(anchor=W,relx=0.15,rely=0.6)
        customtkinter.CTkButton(self.__uploadpage,text='Send',width=80,command=self.uploadData).place(anchor=E,relx=0.49,rely=0.9)
        self.__uploadpage.tkraise()
        self.update()
    
    def uploadData(self):
        if self.__coms is not None:
            if self.__coms.connected:
                nama = self.entryName.get()
                nia = self.entryNIA.get()
                uid = self.__NUID
                self.__coms.sendNama(nama=nama,nia=nia,uid=uid)
                
                maindir = os.getcwd()
                if maindir.find('Absensi') < 0 :
                    maindir = os.path.join(maindir,'Absensi')

                with open(f'{maindir}/data/nama.txt','a') as f:
                    f.write(f'{nama},{nia},{uid}\n')
                
                self.__NUID = ''

                self.buttonNUID.configure(text='Get NUID ID Card')
                self.entryName.delete(0,END)
                self.entryNIA.delete(0,END)

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
        customtkinter.CTkLabel(self.__updatepage,text="Update Data",font=('arial',16)).place(anchor=W,relx=0.15,rely=0.115)
        
        self.optionNama = customtkinter.CTkOptionMenu(self.__updatepage,width=80, values=[x['Nama'] for x in self.__listNama],variable=self.optionMenuVar,command=self.optionNamaAction)
        self.optionNama.place(anchor=W,relx=0.5,rely=0.115)
        self.entryUName = customtkinter.CTkEntry(self.__updatepage,placeholder_text="Nama Lengkap", width=300)
        self.entryUName.place(anchor=W, relx=0.15, rely=0.3)
        self.entryUNIA = customtkinter.CTkEntry(self.__updatepage,placeholder_text="Nomor Induk Anggota", width=300)
        self.entryUNIA.place(anchor=W, relx=0.15, rely=0.45)
        self.labelUNUID = customtkinter.CTkLabel(self.__updatepage, text='NUID:')
        self.labelUNUID.place(anchor=W,relx=0.15,rely=0.6)
        self.getNUID = customtkinter.CTkButton(self.__updatepage,text='Get new NUID ID Card',width=20,command=self.getUID).place(anchor=W,relx=0.5,rely=0.6)

        customtkinter.CTkButton(self.__updatepage,text='Save',width=80,command=self.updatePageSave).place(anchor=E,relx=0.49,rely=0.9)
        customtkinter.CTkButton(self.__updatepage,text='return',width=80, command=self.homepage).place(anchor=W,relx=0.51,rely=0.9)

        if self.__coms is not None:
            if self.__coms.connected:
                self.__coms.getName()

        self.__updatepage.tkraise()
        self.update()

    def updatePageSave(self):
        nama = self.entryUName.get()
        nia = self.entryUNIA.get()
        uid = self.__NUID
        index = [x['Nama'] for x in self.__listNama].index(nama)
        self.__listNama[index]['Nama'] = nama
        self.__listNama[index]['Nia'] = nia
        self.__listNama[index]['NUID'] = uid

        print(self.__listNama)
        listNama = ''
        for i, value in enumerate(self.__listNama):
            if i == 0:
                continue
            listNama = listNama + f"{value['Nama']},{value['Nia']},{value['NUID']}\r\n"
        
        print(listNama)
        self.__coms.updateNama(listNama)
        maindir = os.getcwd()
        if maindir.find('Absensi') < 0 :
            maindir = os.path.join(maindir,'Absensi')

        with open(f'{maindir}/data/nama.txt','w') as f:
            f.write(listNama)


    def optionNamaAction(self,choice):
        self.__dict = self.__listNama[[x['Nama'] for x in self.__listNama].index(choice)]
        self.entryUName.delete(0,END)
        self.entryUNIA.delete(0,END)
        self.optionMenuVar.set(self.__dict['Nama'])
        self.entryUName.insert(0,self.__dict['Nama'])
        self.entryUNIA.insert(0,self.__dict['Nia'])
        self.labelUNUID.configure(text=f"NUID:{self.__dict['NUID']}")


    def getUID(self):
        if self.__coms is not None:
            if self.__coms.connected:
                self.__coms.getNUID()

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
            json.dump([],f,indent=4)
            pass
    
    main.mainloop()