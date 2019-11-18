# -*- coding: utf-8 -*-
#조도 센서 테스트 코드
import detect

try:
    while True:
        print(detect.light(4))
except KeyboardInterrupt:
    pass
finally:
    detect.clean()
