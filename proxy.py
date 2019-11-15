# coding: utf-8
# @coderistan
# TCP Proxy - Python

import sys
import socket
import threading

def hexdump(metin,uzunluk = 16):
    sonuc = []

    for i in xrange(0,len(metin),uzunluk):

        parca = metin[i:i+uzunluk]

        karakterler = []
        for x in parca:
            karakterler.append("%02x"%(ord(x)))

        hexa = " ".join(karakterler)

        yazilar = []
        for x in parca:
            if(32 <= ord(x) < 127):
                yazilar.append(x)
            else:
                yazilar.append("?")

        text = "".join(yazilar)

        
        sonuc.append("%04X %-*s %s"%(i,uzunluk*(2+1),hexa,text))

    print("\n".join(sonuc))

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # sunucuya bağlanıyoruz
    remote_socket = socket.socket(socket.AF_INET,
    socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))
    # ilk cevabı bekliyorsak
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        # response_handler() fonksiyonuna gönderiyoruz
        remote_buffer = response_handler(remote_buffer)
        # Eğer herhangi bir veri varsa, bunu istemciye gönderiyoruz
        if len(remote_buffer):
            print "[<==] %d byte alındı" %len(remote_buffer)
            client_socket.send(remote_buffer)

    # Sorguları dinlemeye başlıyoruz
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print "[==>] %d byte gönderilecek" % len(local_buffer)
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print "[==>] Sunucuya gönderiliyor"
       
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print "[<==] %d byte alındı" % len(remote_buffer)
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print "[<==] İstemciye gönderiliyor"
       
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print "[*] Herhangi bir veri trafiği yok. Bağlantı kapatılıyor"

        break


def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except:
        print "[!!] Proxy başlatılamadı %s:%d" % (local_host,local_port)
        print "[!!] Lütfen Başka programların bu adresi dinlemediğinden ve gerekli izinlere sahip olduğunuzdan emin olun"
        sys.exit(0)
       
    print "[*] coderistan proxy server %s:%d" % (local_host,local_port)
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # Bağlantı bilgisini ekrana yazdırıyoruz
        print "[==>] proxy bağlantısı kuruldu: %s:%d" %(addr[0],addr[1])
        # Thread başlatarak istemci ile iletişim kuruyoruz
        proxy_thread = threading.Thread(target=proxy_handler,args=(client_socket,remote_host,remote_port,receive_first))
        proxy_thread.start()

def receive_from(connection):
    buffer = ""
    connection.settimeout(2)
    
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def response_handler(remote_buffer):
    return remote_buffer

def request_handler(local_buffer):
    return local_buffer


def main():
    # Eğer ki komut satırı argümanları eksik olarak gönderilmişse
    if len(sys.argv[1:]) != 5:
        print "Kullanım: ./proxy.py [localhost] [localport] [remotehost][remoteport] [receive_first]"
        print "Ornek: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)

    # gerekli ayarlamaları yapıyoruz
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host,local_port,remote_host,remote_port,receive_first)

main()
