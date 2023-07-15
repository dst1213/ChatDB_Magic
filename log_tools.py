"""
日志单例

version:202303220818

version:202106072200



》》》参考：
Python logging模块切分和轮转日志_Python碎片的博客-CSDN博客_python日志轮转
https://blog.csdn.net/weixin_43790276/article/details/101944628

Python 实现的 日志logging 单例_comedate的专栏-CSDN博客
https://blog.csdn.net/comedate/article/details/109279743

》》》并发日志
python logging模块“另一个程序正在使用此文件，进程无法访问。”问题解决办法..._weixin_30678821的博客-CSDN博客
https://blog.csdn.net/weixin_30678821/article/details/100005490

python logging模块的分文件存放详析_python_脚本之家
https://www.jb51.net/article/255619.htm

》》》logging 中常用的日志处理方法和类

1. StreamHandler：logging.StreamHandler，日志输出到流，可以是sys.stderr，sys.stdout或者文件，这个方法通常用来将日志信息输出到控制台

2. FileHandler：logging.FileHandler，日志输出到文件，指定文件，将日志信息写入到文件中

3. BaseRotatingHandler：logging.handlers.BaseRotatingHandler，基本的日志轮转方式，这个类是日志轮转的基类，后面日志按时间轮转，按大小轮转的类都继承于此。轮转的意思就是保留一定数量的日志量，如设置保持7天日志，则会自动删除旧的日志，只保留最近7天

4. RotatingHandler：logging.handlers.RotatingHandler，继承BaseRotatingHandler，支持日志文件按大小轮转

5. TimeRotatingHandler：logging.handlers.TimeRotatingHandler，继承BaseRotatingHandler，支持日志文件按时间轮转

6. SocketHandler：logging.handlers.SocketHandler，远程输出日志到TCP/IP sockets

7. DatagramHandler：logging.handlers.DatagramHandler，远程输出日志到UDP sockets

8. SMTPHandler：logging.handlers.SMTPHandler，远程输出日志到邮件地址

9. MemoryHandler：logging.handlers.MemoryHandler，日志输出到内存中的指定buffer

10. HTTPHandler：logging.handlers.HTTPHandler，通过"GET"或者"POST"远程输出到HTTP服务器



》》》RotatingFileHandler 的主要参数：

1. filename： 指定日志文件的名字，会在指定的位置创建一个 filename 文件，然后会按照轮转数量创建对应数量的日志文件，每个轮转文件的文件名为 filename 拼接编号，编号从1开始。

2. maxBytes： 设置日志文件的大小，单位是字节，如 1kb 是1024，1M 是 1024*1024 ，1G 是 1024*1024*1024 。

3. mode： 设置文件的写入模式，默认 mode='a' ，即追加写入。

4. backupCount： 指定日志文件保留的数量，指定一个整数，日志文件只保留这么多个，自动删除旧的文件。


》》》TimedRotatingFileHandler 的主要参数：

1. filename： 指定日志文件的名字，会在指定的位置创建一个 filename 文件，然后会按照轮转数量创建对应数量的日志文件，每个轮转文件的文件名为 filename 拼接时间，默认YY-mm-DD_HH-MM-SS，可以自定义。

2. when： 指定日志文件轮转的时间单位

    S - Seconds
    M - Minutes
    H - Hours
    D - Days
    midnight - roll over at midnight
    W{0-6} - roll over on a certain day; 0 - Monday

3. interval： 指定日志文件轮转的周期，如 when='S', interval=10，表示每10秒轮转一次，when='D', interval=7，表示每周轮转一次。

4. backupCount： 指定日志文件保留的数量，指定一个整数，则日志文件只保留这么多个，自动删除旧的文件。



》》》简化配置：
import logging
# 日志配置
LOG_LEVEL = qt_config.Config.LOG_LEVEL # logging.INFO
logging.basicConfig(filemode="a", level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.root.setLevel(level=LOG_LEVEL)

》》》技巧
- 程序报错退出，但是日志文件无错误打印，说明没有try捕获，增加try，traceback
- 错误堆栈的字符串可写入日志形式：print(traceback.format_exc())
- 主要函数都增加try exception


"""
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from threading import Lock
from concurrent_log_handler import ConcurrentRotatingFileHandler

# 日志级别
BASE_DIR = os.path.dirname(__file__)
LOG_LEVEL = logging.DEBUG  # 日志级别 logging.INFO,logging.DEBUG
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_FILE_PATH, "run.log")
LOG_PARAM_WHEN = "M"  # S second, M minute, H hour, D day ...
LOG_PARAM_INTERVAL = 30  # 间隔，单位是when的配置
LOG_PARAM_BACKUPCOUNT = 5  # 备份文件数量
LOG_PARAM_MAXBYTES = 30 * 1024 * 1024  # 默认30M，1kb 是1024，1M 是 1024*1024 ，1G 是 1024*1024*1024


class LoggerTool:

    def __init__(self):
        self.mutex = Lock()
        self.formatter = '%(asctime)s - %(filename)s - [line]:%(lineno)d - %(levelname)s - %(message)s'
        self.logger = self._create_logger()
        if not os.path.exists(LOG_FILE_PATH):
            print("log path {} not exists".format(LOG_FILE_PATH))
            os.makedirs(LOG_FILE)

    def _create_logger(self):
        _logger = logging.getLogger(__name__)
        _logger.propagate = False
        _logger.setLevel(level=LOG_LEVEL)
        return _logger

    def _file_logger(self):
        size_rotate_file_handler = RotatingFileHandler(filename=LOG_FILE, maxBytes=LOG_PARAM_MAXBYTES,
                                                       backupCount=LOG_PARAM_BACKUPCOUNT, encoding='utf8')  # 还是有报错
        size_rotate_file_handler.setFormatter(logging.Formatter(self.formatter))
        size_rotate_file_handler.setLevel(level=LOG_LEVEL)
        return size_rotate_file_handler

    def _concurrent_file_logger(self):
        size_rotate_file_handler = handler = ConcurrentRotatingFileHandler(filename=LOG_FILE,
                                                                           maxBytes=LOG_PARAM_MAXBYTES,
                                                                           backupCount=LOG_PARAM_BACKUPCOUNT,
                                                                           encoding='utf8')
        size_rotate_file_handler.setFormatter(logging.Formatter(self.formatter))
        size_rotate_file_handler.setLevel(level=LOG_LEVEL)
        return size_rotate_file_handler

    def _time_logger(self):
        time_rotate_file_handler = TimedRotatingFileHandler(filename=LOG_FILE, when=LOG_PARAM_WHEN,
                                                            interval=LOG_PARAM_INTERVAL,
                                                            backupCount=LOG_PARAM_BACKUPCOUNT)
        # time_rotate_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
        # time_rotate_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
        time_rotate_file_handler.setFormatter(logging.Formatter(self.formatter))
        time_rotate_file_handler.setLevel(level=LOG_LEVEL)
        return time_rotate_file_handler

    def _console_logger(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=LOG_LEVEL)
        console_handler.setFormatter(logging.Formatter(self.formatter))
        return console_handler

    def size_logger(self):
        self.mutex.acquire()
        self.logger.addHandler(self._file_logger())
        self.logger.addHandler(self._console_logger())
        self.mutex.release()
        return self.logger

    def concurrent_size_logger(self):
        self.mutex.acquire()
        self.logger.addHandler(self._concurrent_file_logger())
        self.logger.addHandler(self._console_logger())
        self.mutex.release()
        return self.logger

    def time_logger(self):
        self.mutex.acquire()
        self.logger.addHandler(self._time_logger())
        self.logger.addHandler(self._console_logger())
        self.mutex.release()
        return self.logger


# 使用直接调slogger或者tlogger
_logger = LoggerTool()

# slogger = _logger.size_logger()
slogger = _logger.concurrent_size_logger()  # 并发日志
# tlogger = _logger.time_logger()

if __name__ == "__main__":
    slogger.info("aaa")
    # tlogger.debug("bbb")
    # log_pro1 = LoggerTool()
    # log_pro2 = LoggerTool()
    # logger1 = log_pro1.size_logger()
    # logger2 = log_pro2.size_logger()
    # logger1.info('aaa')
    # logger2.info('aaa')
    # print('logger1: ', id(logger1))
    # print('logger2: ', id(logger2))
    # print('log_pro1: ', id(log_pro1))
    # print('log_pro2: ', id(log_pro2))
