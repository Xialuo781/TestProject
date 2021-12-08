from jinja2 import PackageLoader,Environment
env = Environment(loader=PackageLoader('python_project','templates'))    # 创建一个包加载器对象

template = env.get_template('children.html')    # 获取一个模板文件
content = template.render()   # 渲染

print(content)