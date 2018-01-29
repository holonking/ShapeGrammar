import clr
import System
import rhinoscriptsyntax as rs


clr.AddReference('IronPython.Wpf')
import wpf
import Rhino
import System.Windows.Controls as ws
from ShapeGrammar.conduit.displayEngine import DisplayEngine
from ShapeGrammar.core.geometries import ExtrBlock

import linecache


class Inspector(System.Windows.Window):
    def __init__(self):
        super(Inspector, self).__init__()
        System.Windows.Interop.WindowInteropHelper(self).Owner = Rhino.RhinoApp.MainWindowHandle()
        self.conduit = DisplayEngine()
        self.conduit.Enabled = True
        self.Closed += self.disable_conduit

    def set_size(self, w, h):
        self.Width = w
        self.Height = h

    def enable_conduit(self, sender, e):
        if self.conduit is None:
            return
        self.conduit.Enabled = True
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

    def disable_conduit(self, sender, e):
        if self.conduit is None:
            return
        self.conduit.Enabled = False
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()


class InspectTransform(Inspector):
    def __init__(self):
        super(InspectTransform, self).__init__()
        self.set_size(300, 400)
        # subject is the form being examined
        self.subject = None
        self.engine = None
        layout = ws.StackPanel()
        layout.Orientation = ws.Orientation.Vertical
        self.Content = layout

        self.bt_add = ws.Button()
        self.bt_add.Content = 'select a brep'
        self.bt_add.Click += self.addObject
        layout.AddChild(self.bt_add)
        self.bt_enable_conduit = ws.Button()
        self.bt_enable_conduit.Content = 'enable conduit'
        self.bt_enable_conduit.Click += self.enable_conduit
        layout.AddChild(self.bt_enable_conduit)
        self.bt_disable_conduit = ws.Button()
        self.bt_disable_conduit.Content = 'disable conduit'
        self.bt_disable_conduit.Click += self.disable_conduit
        layout.AddChild(self.bt_disable_conduit)

        self.rot_value = 0
        self.slice_value = 0
        self.temp_display_objects = []

        # create UI
        slider_names = ['rotate', 'slice', 'tx', 'ty', 'tz', 'sx', 'sy', 'sz']
        self.sliders = {}
        for n in slider_names:
            layH = ws.StackPanel()
            layH.Orientation = ws.Orientation.Horizontal
            layH.Height = 20
            sld = ws.Slider()
            sld.Width = 200
            lb = ws.Label()
            lb.Content = n
            lb.Width = 60
            lb.Height = 20
            layH.AddChild(lb)
            layH.AddChild(sld)
            layout.AddChild(layH)
            self.sliders[n] = sld

        self.sliders['rotate'].ValueChanged += self.rotate
        self.sliders['slice'].ValueChanged += self.slice

    def set_subject(self, subject):
        self.subject = subject

    def turn(self, sender, e):
        if self.subject:
            self.subject.turn(1)

    def rotate(self, sender, e):
        # https://msdn.microsoft.com/en-us/library/system.windows.controls.slider(v=vs.110).aspx
        # connect to "ValueChanged"
        # e: ValueChangedEvent
        try:
            value = self.sliders['rotate'].Value * 10
            degree = value - self.rot_value
            if self.subject:
                self.subject.rotate(degree)
                Rhino.RhinoDoc.ActiveDoc.Views.Redraw()
            self.rot_value = value
        except Exception as e:
            print(e)
            pass

    def slice(self, sender, e):
        try:
            if len(self.temp_display_objects) > 0:
                for o in self.temp_display_objects:
                    self.conduit.pop(o)
            self.temp_display_objects=[]
            #Rhino.RhinoDoc.ActiveDoc.Views.Redraw()
        except Exception as e:
            print('Exception while removing temp disp objs',e)

        try:
            if self.subject:
                value = self.sliders['slice'].Value
                ratio = value / 10
                amp = ratio * self.subject.scope.size[0]
                print('slice amp:',amp)
                close, far = self.subject._split_dir_amp(0, amp)

                if close:
                    self.temp_display_objects.append(close)
                if far:
                    self.temp_display_objects.append(far)
                for o in self.temp_display_objects:
                    self.conduit.add(o)
                if value == 0:
                    self.subject.visible_topo = False
                else:
                    self.subject.visible_topo = True
                Rhino.RhinoDoc.ActiveDoc.Views.Redraw()
        except Exception as e:
            print('Exception while spliting', e)

    def addObject(self, sender, e):
        try:
            sel = rs.GetObject('sel brep')
            print(sel)
            form = ExtrBlock.create_from_brepid(sel)
            if form:
                print('form created')
                self.subject = form
                self.conduit.add(form)
                Rhino.RhinoDoc.ActiveDoc.Views.Redraw()
        except Exception as e:
            print('Exception from addObject:',e)
            #PrintException()
            pass


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
