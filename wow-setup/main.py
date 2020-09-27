import sys
import os
import ctypes


if __name__ == '__main__':
    print(ctypes.windll.shell32.IsUserAnAdmin() != 0)
    