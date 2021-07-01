import PySimpleGUI as sg


def login_pane(data, tittle="登录", oneshot=False):
    """
    登录界面
    :param oneshot: 单次输入，如果为真，则用户只能试一次，错误则不让继续登录
    :param data:由账户密码构成的字典
    :param tittle: 界面标题
    :return: 与用户输入的账号密码比较，匹配返回真
    """
    col_layout =[[sg.Text("用户名："), sg.Input(key="-user-")],
                    [sg.T("密码："), sg.I(key="-password-")]]
    login_layout = [[sg.Col(col_layout)],
                    [sg.B("login")]]
    window = sg.Window(tittle, login_layout)
    while True:
        event, value = window.read()
        if event == sg.WINDOW_CLOSED:
            return False
        if event == 'login':
            if value["-user-"] == data['user'] and value['-password-'] == data['password']:
                sg.Popup("登陆成功")
                window.close()
                return True
            elif oneshot:
                sg.Popup("账户或密码错误")
                return False


def rigester_pane(tittle="注册"):
    """
    :注册界面
    :param tittle:窗体标题
    :return: 返回账号与密码组成的元组
    """
    col_layout = [[sg.T("请输入账号"), sg.I(key="-account-")],
                       [sg.T("请输入密码"), sg.I(key="-password1-")],
                       [sg.T("请再次输入密码"), sg.I(key="-password2-")]]
    register_layout = [[sg.Col(col_layout)],
                       [sg.B("注册")]]
    window = sg.Window(tittle, register_layout)
    while True:
        event, value = window.read()
        if event == sg.WINDOW_CLOSED:
            return False
        if event == "注册":
            if value['-password1-'] == value['-password2-'] and value['-account-'] != '' and value['-password1-'] !='':
                sg.Popup("注册成功")
                window.close()
                return value['-account-'], value['-password1-']
            elif value['-password1-'] != value['-password2-']:
                sg.Popup("两次密码不匹配，重新输入")
            elif value['-account-'] == '':
                sg.Popup("请输入用户名！")
            elif value['-password1-'] == "" or value ['-password2-'] == '':
                sg.Popup("请输入密码！")
