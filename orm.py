"""
定义字段
"""
from ORM.mysql_control import Mysql
class Field:
    def __init__(self,name,column_type,primary_key,default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

# varchar
class StringField(Field):
    def __init__(self,name,column_type="varchar(255)",primary_key=False,default=None):
        super().__init__(name,column_type,primary_key,default)

# int
class IntegerField(Field):
    def __init__(self,name,column_type="int",primary_key=False,default=0):
        super().__init__(name,column_type,primary_key,default)


# 元类控制表模型的创建

class OrmMetaClass(type):
    #类名，类的基类，类的名称空间
    def __new__(cls,class_name,class_bases,class_attr):
        print(class_name,class_bases,class_attr)
        # 过滤Models类
        if class_name == "Models":
            return type.__new__(cls,class_bases,class_name,class_attr)

        # 控制模型表中：表名，主建，表的字段
        # 如果模型表中没有定义table_name,把类名当作表名

        # 获取表名
        table_name = class_attr.get('table_name',class_name)

        # 判断是否只有一个主建
        primary_key = None

        # 用来存放所有表字段，存不是目的，目的是为了取出来

        mappings={}
        for key,value in class_attr.item():
            if isinstance(value,Field):
                # 把所有字段都添加到mappings中
                mappings[key] = value
                if value.primary_key:
                    if primary_key:
                        raise TypeError("主建只能只有一个")
                    # 获取主建
                    primary_key = value.name
        # 删除class_attr中与mappings重复的属性，节约资源
        for key in mappings.keys():
            class_attr.pop(key)

            if not primary_key:
                raise TypeError("必须要有一个主建")

            class_attr['table_name'] = table_name
            class_attr['primary_key'] = primary_key
            class_attr['mappings']  = mappings

            return type.__new__(cls,class_name,class_bases,class_attr)

# 继承字典类
class Models(dict,metaclass=OrmMetaClass): # 元类的继承关系
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # 在对象.属性没有的时候出发
    def __getattr__(self, item):
        return self.get(item,"没有这个key")

    # 在对象.属性 = 属性时触发

    def __setattr__(self, key, value):

        self[key] = value

        # 查
    @classmethod
    def select(cls,**kwargs):
        # 获取数据库连接对象
        ms = Mysql()

        if not kwargs:

            sql = "select * from %s" % cls.table_name
            res = ms.my_select(sql)

            # 若有kwargs代表有条件
        else:
            key = list(kwargs.keys())[0]
            value = kwargs.get(key)

            sql = "select * from %s where %s=?"%(
                cls.table_name,key
            )

            sql = sql.replace("?","%s")
            res = ms.my_select(sql,value)

        if res:
            return [cls(**result) for result in res ]
    # 插入方法

    def save(self):
        ms = Mysql()
        fields = []
        values = []
        args = []
        for k,v in self.mappings.items():
            if not v.primary_key:
                fields.append(
                    v.name
                )
                values.append(
                    getattr(self,v.name,v.default)
                )
                args.append("?")
        sql = "insert into %s(%s) value (%s)"%(self.table_name,','.join(fields),','.join(args))
        sql = sql.replace('?',"%s")
        ms.my_execute(sql,values)

    #更新
        # 更新
        def sql_update(self):
            ms = Mysql()

            fields = []
            primary_key = None
            values = []

            for k, v in self.mappings.items():
                # 获取主键的值
                if v.primary_key:
                    primary_key = getattr(self, v.name, v.default)

                else:

                    # 获取 字段名=?, 字段名=?,字段名=?
                    fields.append(
                        v.name + '=?'
                    )

                    # 获取所有字段的值
                    values.append(
                        getattr(self, v.name, v.default)
                    )

            # update table set %s=?,... where id=1;  把主键当做where条件
            sql = 'update %s set %s where %s=%s' % (
                self.table_name, ','.join(fields), self.primary_key, primary_key
            )

            # print(sql)  # update User set name=? where id=3

            sql = sql.replace('?', '%s')

            ms.my_execute(sql, values)


# 表模型的创建
class User(Models):
    #table_name = "user_info"
    id = IntegerField(name='id',primary_key=True)
    name = StringField(name='name')
    pwd = StringField(name='pwd')


class Movie(Models):
    pass

# User("出入任意个数的关键字参数")
user_obj = User()
user_obj.name = "xxxx"

if __name__ == '__main__':
    res = User.select(name="cozy")[0]

    # user_obj = User(name='egon')
    # user_obj.save()

'''
表:
    表名, 只有一个唯一的主键, 字段(必须是Field的字段)

元类:
    通过元类控制类的创建.
'''

# class Movie:
#     def __init__(self, movie_name, movie_type):
#         self.movie_name = movie_name
#         self.movie_type = movie_type
#
#
# class Notice:
#     def __init__(self, title, content):
#         self.title = title
#         self.content = content

'''
问题1: 所有表类都要写__init__, 继承一个父类
问题2: 可以接收任意个数以及任意名字的关键字参数. 继承python中的字典对象.
'''

# if __name__ == '__main__':
#     # d1 = dict({'name': 'tank'})
#     # d2 = dict(name='tank2')
#     # print(d1)
#     # print(d2)
#
#     d3 = Models(name='jason')
#     # print(d3)
#     # print(d3.get('name'))
#     # print(d3['name'])
#     # print(d3.name)
#     # d3.name = 'tank'
#     # d3.pwd = '123'
#     # print(d3.name)
#     # print(d3)
#     print(d3.name)  # None
#
#     d3.pwd = '123'
#     print(d3.pwd)
#     print(d3)































