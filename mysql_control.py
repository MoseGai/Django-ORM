import pymysql

class Mysql:
    _instance = None
    # 单例模型
    def __new__(cls, *args, **kwargs):
        # 如果没有_instance就调用object.__new()__来实例化
        if not cls._instance:
            cls._instance = object.__new__(cls,*args,**kwargs)
        return cls._instance

    def __init__(self):
        # 建立连接
        self.conn = pymysql.connect(
        host = "127.0.0.1",
        port = 3306,
        password = "123",
        database = "orm_test",
        charset = "utf8",
        autocommit=True
        )
        # 获取游标
        self.cursor = self.conn.cursor(
            pymysql.cursors.DictCursor
        )
    # 关闭游标、连接方式
    def close_db(self):
        self.cursor.close()
        self.conn.close()
    # 查看
    def my_select(self,sql,args=None):
        self.cursor.execute(sql,args)
        res = self.cursor.fetchall()
        return res
    def my_execute(self,sql,args):
        try:
            self.cursor.execute(sql,args)
        except Exception as e:
            print(e)







