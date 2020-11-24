import time
import win32api
import win32con
import win32gui
import pyperclip

hwnd_title = dict()


def get_all_hwnd(hwnd, mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


def test_0():
    win32gui.EnumWindows(get_all_hwnd, 0)

    for h, t in hwnd_title.items():
        if t != '':
            print(h, t)


def test_1():
    handle = win32gui.FindWindow(None, '信鸽国际有限公司')
    print(handle)
    win32gui.SetForegroundWindow(handle)
    msg = 'abc\n' \
          '123\n' \
          'zxc'
    pyperclip.copy(msg)

    win32api.keybd_event(17, 0, 0, 0)  # ctrl
    win32api.keybd_event(86, 0, 0, 0)  # v
    win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)

    win32api.keybd_event(18, 0, 0, 0)  # Alt
    win32api.keybd_event(83, 0, 0, 0)  # s
    win32api.keybd_event(18, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(83, 0, win32con.KEYEVENTF_KEYUP, 0)


if __name__ == '__main__':
    test_1()
