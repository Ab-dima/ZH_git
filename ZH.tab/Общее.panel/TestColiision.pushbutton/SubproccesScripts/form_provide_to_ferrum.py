# -*- coding: utf8 -*-

import clr, sys, os

clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import Color, Pen, ContentAlignment, Point, Font, Size
from System.Windows.Forms import *



class MainForm(Form):
    def __init__(self):
        self.controlsIgnor = []

        self.fColor = Color.White
        self.sColor = Color.Gray
        self.TextColor = Color.Black

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(550, 700)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('Arial', 12)

        self.data_dict = {
            "1": {"IMAGE_URL": "url1", "DESCRIPTION": "Плагин 'Менеджер коллизий' переезжает из 'ZH' в 'Ferrum'\n(буден активен на вкладке ZH в течении 7 дней)"},
            "2": {"IMAGE_URL": "url2", "DESCRIPTION": "Чтобы плагин 'Менеджер коллизий' появился на вкладке 'Ferrum' - необходимо обновиться через FerrumUpdater\nЕсли он уже имеется, то дополнительно обновляться не нужно"},
            "3": {"IMAGE_URL": "url3", "DESCRIPTION": "Для знакомства с новой версией плагина, можно перейти в режим 'Инструкция', нажав на <<?>>"},
            "4": {"IMAGE_URL": "url4", "DESCRIPTION": "Принцип работы остается прежним.\nПроизведена оптимизация работы, а также решена часть проблем из старой версии плагина"}
        }
        self.selectedIndexImage = 1

        self.controlPanel()
        self.middlePanel()

        self.update_btn_color_style(self.controlsIgnor)


    def controlPanel(self):
        from System.Drawing import Image
        def mouseMove(sender, event):
            from System.Windows.Forms import Cursor
            from System.Drawing import Point
            from System.Drawing import Size

            if self.dragging:
                dif = Point.Subtract(Cursor.Position, Size(self.cursorLocation))
                self.Location = Point.Add(self.formLocation, Size(dif))

        def mouseDown(sender, event):
            from System.Windows.Forms import Cursor
            self.dragging = True
            self.cursorLocation = Cursor.Position
            self.formLocation = self.Location

        def mouseUp(sender, event):
            self.dragging = False

        def minimizeForm(sender, event):
            self.WindowState = FormWindowState.Minimized

        separator = Panel(Dock=DockStyle.Top,
                          Height=1)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)
        self.controlsIgnor.append(self.panelTop)

        self.panelTop.MouseUp += mouseUp
        self.panelTop.MouseDown += mouseDown
        self.panelTop.MouseMove += mouseMove

        labelForm = Label(Text='важная информация'.upper(),
                          Size = Size(300, 30))
        labelForm.Location = Point(self.Width / 2 - labelForm.Width / 2, 3)
        labelForm.TextAlign = ContentAlignment.MiddleCenter
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        separator = Panel(Dock = DockStyle.Bottom,
                          Height = 0.5)
        self.panelTop.Controls.Add(separator)

        btnMinimize = Button(Name='ControlButton',
                             Text='_',
                             Dock=DockStyle.Right,
                             Width=30)
        btnMinimize.Click += self.minimizeForm
        self.panelTop.Controls.Add(btnMinimize)

        btnClose = Button(Name='ControlButton',
                          Text='❌',
                          Dock=DockStyle.Right,
                          Width=30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

        """Сепараторы необходимы для добавления границ формы слева и справа"""
        sepTop = Panel(Name='SideBorders',
                       Height=1,
                       Dock=DockStyle.Top,
                       BackColor=Color.Red)
        self.panelTop.Controls.Add(sepTop)

        sepLeft = Panel(Name='SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        self.panelTop.Controls.Add(sepLeft)

        sepRight = Panel(Name='SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        self.panelTop.Controls.Add(sepRight)
        # self.panelTop.Controls.SetChildIndex(sepRight, 0)
        """--------------------------------------------------------------"""


    def middlePanel(self):
        from System.Windows.Forms import ImageLayout
        from System.Drawing import ContentAlignment, Image
        def createSep(x , y, width = self.Width -40, height = 1):
            sep = Panel(Location = Point(x,y),
                        Size = Size(width, height))
            mainPanel.Controls.Add(sep)

        mainPanel = Panel(Dock=DockStyle.Fill,
                          BackColor=Color.White)
        self.controlsIgnor.append(mainPanel)
        self.Controls.Add(mainPanel)
        self.Controls.SetChildIndex(mainPanel, 0)

        self.pictureBox = PictureBox(Size = Size(450, 450),
                                     SizeMode = PictureBoxSizeMode.StretchImage)
        self.pictureBox.Location = Point(self.Width / 2 - self.pictureBox.Width / 2, 0)
        mainPanel.Controls.Add(self.pictureBox)



        self.controlsPanel = Panel(Size = Size(250, 40))
        self.controlsPanel.Location = Point( mainPanel.Width / 2 - self.controlsPanel.Width / 2 + 10 , mainPanel.Height - 80)
        self.controlsIgnor.append(self.controlsPanel)
        mainPanel.Controls.Add(self.controlsPanel)

        self.labelInformation = Label(Size = Size(500, 120))
        self.labelInformation.Location = Point(mainPanel.Width / 2 - self.labelInformation.Width / 2 + 10 , mainPanel.Height - 200)
        self.labelInformation.TextAlign = ContentAlignment.MiddleCenter
        self.labelInformation.Font = Font("Arial", 13)
        mainPanel.Controls.Add(self.labelInformation)


        self.startPos = 0
        self.part = self.controlsPanel.Width / (len(self.data_dict)+2)

        self.btn_left = Button(Text='<',
                               Size = Size(30, 30),
                               Location=Point(self.startPos-5, 5),
                               Font = Font("Arial", 15),
                               TextAlign = ContentAlignment.MiddleCenter)
        self.btn_left.Click += self.to_left
        self.controlsPanel.Controls.Add(self.btn_left)
        self.startPos += self.part


        for i in range(len(self.data_dict)):
            emptyControl = RadioButton(Name = str(i+1),
                                       Location = Point(self.startPos, 5),
                                       Size =Size(30, 30))
            emptyControl.CheckedChanged += self.chageChecked_radiobox
            self.controlsPanel.Controls.Add(emptyControl)
            self.startPos += self.part

        self.btn_right = Button(Text='>',
                                Size=Size(30, 30),
                                Location=Point(self.startPos, 5),
                                Font = Font("Arial", 15),
                                TextAlign = ContentAlignment.MiddleCenter)
        self.btn_right.Click += self.to_right
        self.controlsPanel.Controls.Add(self.btn_right)
        self.checkedRadioBox(self.selectedIndexImage)

        self.close_form = Button(Text='Закончить обзор',
                                 Size=Size(180, 30),
                                 Font=Font("Arial", 13),
                                 TextAlign=ContentAlignment.MiddleCenter,
                                 Visible=False)
        self.close_form.Location = Point(self.Width / 2 - self.close_form.Width / 2, mainPanel.Height-30)
        self.close_form.Click += self.closeForm
        mainPanel.Controls.Add(self.close_form)


        """Сепараторы необходимы для добавления гранис формы слева и справа"""
        sepTop = Panel(Name='SideBorders',
                       Height=1,
                       Dock=DockStyle.Bottom,
                       BackColor=Color.Red)
        mainPanel.Controls.Add(sepTop)

        sepLeft = Panel(Name='SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        mainPanel.Controls.Add(sepLeft)

        sepRight = Panel(Name='SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        mainPanel.Controls.Add(sepRight)
    """--------------------------------------------------------------"""

    def checkedRadioBox(self, i):
        try:
            self.change_image(i)

            for control in self.controlsPanel.Controls:
                if isinstance(control, RadioButton) and control.Name == str(i):
                    control.Checked = True
        except Exception as e:
            print(e)


    def change_image(self, i):
        from System.Drawing import Image
        try:
            pathToImage = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Recources_Form_Provider", "image{}.png".format(i))
            self.pictureBox.Image = Image.FromFile(pathToImage)

            self.labelInformation.Text = self.data_dict[str(i)]["DESCRIPTION"]
        except Exception as e:
            print(e)



    def to_right(self, sender, event):
        if self.selectedIndexImage + 1 > len(self.data_dict):
            self.selectedIndexImage = 1
            self.close_form.Visible = True
        else:
            self.selectedIndexImage += 1

        self.checkedRadioBox(self.selectedIndexImage)

    def to_left(self, sender, event):
        if self.selectedIndexImage - 1 == 0:
            self.selectedIndexImage = len(self.data_dict)
        else:
            self.selectedIndexImage -= 1

        self.checkedRadioBox(self.selectedIndexImage)

    def chageChecked_radiobox(self, sender,event):
        self.selectedIndexImage = int(sender.Name)
        self.change_image(self.selectedIndexImage)







    def get_all_controls(self):
        all_controls = []

        def recurci_controls(control):
            for contr in control:
                all_controls.append(contr)
                if contr.Controls:
                    recurci_controls(contr.Controls)

        recurci_controls(self.Controls)
        return all_controls

    def showLineError(self, error):
        import traceback
        import sys
        print('-------------- ERROR ---------------------')
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)
        filename, line, func, text = tb[-1]
        print(line)
        print("Ошибка: {}".format(error))
        print('-------------- ERROR ---------------------')

    def eventChangeBorderBtn_MouseEnter(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def eventChangeBorderBtn_MouseLeave(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def update_btn_color_style(self, lstControlsIgnor=[]):
        from System.Windows.Forms import Panel, Button, FlatStyle, TextBox, ComboBox, Label, CheckBox, TreeView
        from System.Drawing import Color
        def newRGBColor(color,coeffColor = 1.9):
            newColor = Color.FromArgb((color.R) * coeffColor,
                                      (color.G) * coeffColor,
                                      (color.B) * coeffColor)
            return newColor


        for control in self.get_all_controls():
            str_type = str(type(control)).lower()
            if control in lstControlsIgnor:
                if isinstance(control, Panel):
                    control.BackColor = self.fColor
            else:
                if isinstance(control, Button):
                    control.MouseEnter -= self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave -= self.eventChangeBorderBtn_MouseLeave

                    if control.Name == 'ControlButton':
                        control.BackColor = self.fColor
                        control.ForeColor = self.TextColor

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.BorderSize = 0
                    else:
                        control.BackColor = self.fColor
                        control.ForeColor = self.TextColor

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.MouseDownBackColor = Color.FromArgb(150, self.sColor)
                        flatApearance.MouseOverBackColor = Color.FromArgb(50, self.sColor)
                        flatApearance.BorderSize = 0

                    control.MouseEnter += self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave += self.eventChangeBorderBtn_MouseLeave

                elif isinstance(control, Panel):
                    if control.Name == "UniqePanel":
                        control.BackColor = Color.WhiteSmoke
                    else:
                        control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, ComboBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.TextColor
                elif isinstance(control, Label):
                    if control.Name == 'ControlInfo':
                        control.ForeColor = newRGBColor(self.sColor)
                    else:
                        control.ForeColor = newRGBColor(Color.DimGray, 0.5)
                elif isinstance(control, CheckBox):
                    control.ForeColor = newRGBColor(Color.DimGray, 0.5)
                elif isinstance(control, TreeView):
                    control.BackColor = self.fColor
                    # for node in control.Nodes:
                    #     node.ForeColor = self.TextColor

    def minimizeForm(self,sender, event):
        from System.Windows.Forms import FormWindowState
        self.WindowState = FormWindowState.Minimized

    def closeForm(self, sender, event):
        self.Close()


def start():
    form = MainForm()
    form.ShowDialog()

