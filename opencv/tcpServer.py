#tcp 서버 코드
#안드로이드로부터 동기화 요청을 받으면 수면 데이터 전송
import socket
import time

def tcpSend():
    global s
    print('수면 데이터 전송을 위한 통신 시작')
    HOST = ""
    PORT = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #소켓 생성
    print ('서버 소켓 생성')
    s.bind((HOST, PORT)) #소켓 주소 정보 할당
    print ('서버 소켓 bind complete')
    s.listen(1) # 연결 수신 대기 상태
    print ('서버 소켓 대기중(now listening)')
    
    while True:
        #접속 승인
        print('접속 승인')
        conn, addr = s.accept()
        print("Connected by ", addr)

        #데이터 수신
        data = conn.recv(1024)
        data = data.decode("utf8").strip()
        if not data: 
            tcpEnd()
        print("받은 데이터: " + data)
        #클라이언트에게 답을 보냄
        if data == '1':
            print('동기화 시작')
            f = open("json.txt", 'r')
            while True:
                time.sleep(0.1) #딜레이를 주어 통신이 원활하게 동작하도록 한다.
                line = f.readline()
                if not line: 
                    break
                print("데이터 전송: "+line)
                conn.send(line.encode("utf-8"))
            conn.close()
            s.close()
            print('서버 종료')
            break
        elif data == '2':
            conn.close()
            s.close()
            print('서버 종료')
            break
        else:
            print('동기화 실패')
        #연결 닫기
        conn.close()
        print("연결 종료")

if __name__ == "__main__":
    tcpSend()
    
