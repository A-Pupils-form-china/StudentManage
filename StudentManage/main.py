from mytool import guipane as t
import mysql.connector
import PySimpleGUI as sg

mydb = mysql.connector.connect(
    host="192.168.0.10",  # 数据库主机地址
    user="root",  # 数据库用户名
    passwd="root",  # 数据库密码
    database="StudentManage",
    buffered=True
)
mycursor = mydb.cursor()


def load():
    mycursor.execute("SELECT value FROM configure where project=\"admin_is_signed\"")
    if not eval(mycursor.fetchone()[0]):
        register()
    else:
        login()


def register():
    data = t.rigester_pane()
    mysql_execute("INSERT INTO admin (account, password) values (\"%s\",\"%s\")" % data)
    mysql_execute('UPDATE configure SET value=\'True\' WHERE project=\'admin_is_signed\'')
    login()


def login():
    mycursor.execute("SELECT account,password FROM admin")
    data = mycursor.fetchone()
    if t.login_pane({"user": data[0], "password": data[1]}):
        menuPane()


def menuPane():
    str = ["1.查看学生信息", "2.新增学生信息", "3.修改学生信息", "4.删除学生信息"]
    menu_layout = [[sg.T("请选择你的操作")],
                   [sg.B(str[0])],
                   [sg.B(str[1])],
                   [sg.B(str[2])],
                   [sg.B(str[3])],
                   [sg.B('退出')]]
    window = sg.Window("学生管理系统", menu_layout)
    while True:
        student_amount, data = refresh()
        print(student_amount)
        event, value = window.read()
        print(event)
        if event == sg.WINDOW_CLOSED:
            break
        if event == str[0]:
            if student_amount != 0:
                window.hide()
                select_pane(data, tittle=str[0][2:], student_amount=student_amount)
                window.UnHide()
            else:
                sg.Popup("当前没有学生，无法查看")
        if event == str[1]:
            window.hide()
            new_information(data, student_amount)
            window.UnHide()
        if event == str[2]:
            window.hide()
            select_pane(data, str[2][2:], student_amount=student_amount, button='修改')
            window.UnHide()
        if event == str[3]:
            window.hide()
            select_pane(data, tittle=str[0][2:], student_amount=student_amount, button='删除')
            window.UnHide()

        if event == '退出':
            window.close()
            break


def select_pane(data, tittle, student_amount, button="查找"):
    layout = [[sg.Table(values=data, headings=['uid', '姓名', '学号', '二级学院', '所在班级'], col_widths=[4, 6, 14, 18, 9],
                        auto_size_columns=False, num_rows=min(len(data), 20), key='-table-')],
              [sg.T('请输入学号或uid查找学生')],
              [sg.R("学号", 'radio', default=True, key='ISNUMBER'), sg.I("", key="-NUMBER-", size=(15, 1)),
               sg.R("uid ", 'radio', default=False, key='ISUID'), sg.I("", key="-UID-", disabled=True, size=(15, 1))],
              [sg.B(button), sg.B('退出')]]
    window = sg.Window(tittle, layout)
    showAll = True
    while True:
        event, value = window.read(timeout=100)
        if event == "退出" or event == sg.WINDOW_CLOSED:
            window.close()
            break
        if event == "查找":
            if value['-NUMBER-'] == '' and value['-UID-'] == '':
                if showAll:
                    sg.Popup("请输入学号或uid!")
                else:
                    window['-table-'].update(data)
                    showAll = True
                continue
            temp = None
            if value['ISNUMBER']:
                for i in data:
                    if i[2] == value['-NUMBER-']:
                        temp = [i, ]
                        break
            if value['ISUID'] and eval(value['-UID-']) <= student_amount:
                temp = [data[eval(value['-UID-']) - 1], ]
                print("uid" + str(temp))
            if temp is None:
                sg.Popup('查无此人')
                continue
            window['-table-'].update(values=temp)
            showAll = False
        if event == '__TIMEOUT__':
            if value['ISNUMBER']:
                window['-UID-'].update('')
                window['-NUMBER-'](disabled=False)
                window['-UID-'](disabled=True)
            if value['ISUID']:
                window['-NUMBER-'].update('')
                window['-UID-'](disabled=False)
                window['-NUMBER-'](disabled=True)
        if event == '删除':
            i = 0
            found = False
            if value['ISNUMBER']:
                if value['-NUMBER-'] == '':
                    sg.Popup('请输入学号！')
                    continue
                while i < len(data):
                    if data[i][2] == value['-NUMBER-']:
                        found = True
                        break
                    i += 1
            if value['ISUID']:
                if value['-UID-'] == '':
                    sg.Popup("请输入uid！")
                    continue
                while i < len(data):
                    if data[i][0] == int(value['-UID-']):
                        found = True
                        break
                    i += 1
            if not found:
                sg.Popup('查无此人')
                continue
            if sg.PopupYesNo("确定删除此人信息吗" + str(data[i])) == 'Yes':
                mysql_execute("DELETE FROM students WHERE uid=%d" % (data[i][0],))
                sg.Popup("删除成功")
                for a in range(i, len(data)):
                    mycursor.execute("UPDATE students set uid=%d where uid=%d" % (a, a + 1))
                mycursor.execute("SELECT * FROM students")
                data = mycursor.fetchall()
                student_amount -= 1
                mysql_execute('UPDATE configure set value=%d where project=\'student_amount\'' % student_amount)
                window['-table-'].update(values=data)
        if event == '修改':
            i = 0
            found = False
            if value['ISNUMBER']:
                if value['-NUMBER-'] == '':
                    sg.Popup('请输入学号！')
                    continue
                while i < len(data):
                    if data[i][2] == value['-NUMBER-']:
                        found = True
                        break
                    i += 1
            if value['ISUID']:
                if value['-UID-'] == '':
                    sg.Popup("请输入uid！")
                    continue
                while i < len(data):
                    if data[i][0] == int(value['-UID-']):
                        found = True
                        break
                    i += 1
            if not found:
                sg.Popup("查无此人")
                continue
            layout = [[sg.T('姓名：'), sg.I(data[i][1], key='-NAME-')],
                      [sg.T('学号：'), sg.I(data[i][2], key='-NUMBER-')],
                      [sg.T('学院：'), sg.I(data[i][3], key='-COLLEGE-')],
                      [sg.T('班级：'), sg.I(data[i][4], key='-CLASS-')],
                      [sg.B('确定'), sg.B('退出')]]
            change = sg.Window('修改信息', layout)
            while True:
                event, values = change.read()
                if event in ('退出', sg.WINDOW_CLOSED):
                    change.close()
                    break
                if event == '确定':
                    b = False
                    if values['-NAME-'] == data[i][1] and values['-NUMBER-'] == data[i][2] and values['-COLLEGE-'] == \
                            data[i][3] and values['-CLASS-'] == data[i][4]:
                        sg.Popup("请修改信息！")
                        continue
                    for x in values.values():
                        if x == "":
                            sg.Popup('请检查是否有信息漏填!')
                            b = True
                    if b:
                        continue
                    conflict = False
                    for x in data:
                        if x[2] == values['-NUMBER-']:
                            sg.Popup('学号冲突，该学号已收录:' + str(x))
                            conflict = True
                            break
                    if conflict:
                        continue
                    temp = list(values.values())
                    print("temp=" + str(temp))

                    mysql_execute(
                        'UPDATE students SET name=\'%s\', number=\'%s\', college=\'%s\', class= \'%s\' WHERE uid=%d' % (
                            temp[0], temp[1], temp[2], temp[3], i + 1))
                    sg.Popup('修改成功')
                    change.close()
                    break
            student_amount, data = refresh()
            window['-table-'](values=data)


def new_information(data, student_amount):
    layout = [[sg.T('姓名：'), sg.I('', key='-NAME-')],
              [sg.T('学号：'), sg.I('', key='-NUMBER-')],
              [sg.T('学院：'), sg.I('', key='-COLLEGE-')],
              [sg.T('班级：'), sg.I('', key='-CLASS-')],
              [sg.B('确定'), sg.B('退出')]]
    window = sg.Window('新增信息', layout)
    while True:
        event, value = window.read()
        if event == sg.WINDOW_CLOSED or event == '退出':
            window.close()
            break
        if event == '确定':
            empty = False
            for i in value.values():
                if i == '':
                    sg.Popup('请检查信息是否有缺漏')
                    empty = True
                    break
            if empty:
                continue
            conflict = False
            for i in data:
                if i[2] == value['-NUMBER-']:
                    sg.Popup('学号冲突，该学号已收录:' + str(i))
                    conflict = True
                    break
            if conflict:
                continue
            temp = list(value.values())
            temp.insert(0, student_amount + 1)

            mysql_execute('INSERT INTO students (uid, name, number, college, class) values (%d, \'%s\', \'%s\', '
                          '\'%s\', \'%s\')' % (temp[0], temp[1], temp[2], temp[3], temp[4]))
            student_amount += 1
            mysql_execute('UPDATE configure set value=%d where project=\'student_amount\'' % student_amount)
            sg.Popup('收录成功')
            window.close()
            break


def mysql_execute(command):
    mycursor.execute(command)
    mydb.commit()


def refresh():
    mycursor.execute("SELECT value FROM configure WHERE project=\'student_amount\'")
    amount = eval(mycursor.fetchone()[0])
    mycursor.execute("SELECT * FROM students")
    students = mycursor.fetchall()
    return amount, students


menuPane()
