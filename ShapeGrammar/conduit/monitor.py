import clr
import System
clr.AddReference('IronPython.Wpf')
import wpf
import Rhino
import System.Windows.Controls as ws

class ConduitMonitor(System.Windows.Window):
    def __init__(self, conduit, show=True):
        super(ConduitMonitor,self).__init__()
        self.Width=100
        self.Height=200
        self.conduit=conduit

        layout = ws.StackPanel()
        layout.Orientation = ws.Orientation.Vertical
        bt1 = ws.Button()
        bt1.Content = 'enable'
        bt1.Click += self.enable
        bt2 = ws.Button()
        bt2.Content = 'disable'
        bt2.Click += self.disable
        layout.AddChild(bt1)
        layout.AddChild(bt2)

        self.Content=layout
        self.Closed+=self.disable

        if show:
            self.conduit.Enabled = True
            Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

        System.Windows.Interop.WindowInteropHelper(self).Owner = Rhino.RhinoApp.MainWindowHandle()
        self.Show()


    def enable(self, sender, e):
        self.conduit.Enabled = True
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

    def disable(self, sender, e):
        self.conduit.Enabled = False
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()