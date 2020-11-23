import time
from concurrent.futures.process import ProcessPoolExecutor
from multiprocessing import Manager
import pywinauto.keyboard as kb
from pywinauto import Application
import pyperclip


app = Application(backend='uia')
app.connect(path=r'D:\Program Files (x86)\Tencent\WeChat\WeChat.exe')


def producer(msg, q):
    q.put(msg)


def consumer(q):
    while 1:
        if not q.empty():
            msg = q.get()
            pyperclip.copy(msg)
            kb.send_keys('^v')
        else:
            print(q.empty())
        time.sleep(1)


if __name__ == '__main__':
    q = Manager().Queue()
    executor = ProcessPoolExecutor(max_workers=6)
    executor.submit(producer, 'process_1 is \ncalling', q)
    executor.submit(producer, 'process_2 is \ncalling', q)
    executor.submit(producer, 'process_3 is \ncalling', q)
    executor.submit(producer, 'process_4 is \ncalling', q)
    executor.submit(producer, 'process_5 is \ncalling', q)

    executor.submit(consumer, q)