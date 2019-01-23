import sys

import wx
import wx.glcanvas as glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import viewer
import math


# ----------------------------------------------------------------------


class MyCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.context = glcanvas.GLContext(self)

        self.mouseDown = False
        self.rmouseDown = False

        self.count = 0
        self.zoom = 1
        self.lastx = self.x = 30
        self.lasty = self.y = 30
        self.size = None
        self.ratio = 1
        self.obj = viewer.bvhreader('dance.bvh')
        self.timer = wx.Timer(self)
        self.timer.Start(self.obj.frame_time*1000)

        self.w, self.u, self.v = np.array([0, 0, 0])
        self.at = np.array([0, 0, 0])
        self.up = np.array([0, 1, 0])
        self.leng = 100
        self.azimuth = np.radians(30)
        self.elevation = np.radians(30)
        self.cam = np.array(
            [self.leng * np.sin(self.azimuth), self.leng * np.sin(self.elevation), self.leng * np.cos(self.azimuth)])

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        #self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_TIMER, self.OnTime)

    def OnTime(self, evt):
        ...
        self.count += 1
        self.count = self.count % self.obj.frames
        print(self.count)
        self.obj.update_frame(self.count)
        self.Refresh()

    def OnMouseWheel(self, evt):
        print("mousewheel")
        self.getWUV()
        paramW = self.w * 10
        # wheel up -> zoom in
        if evt.GetWheelRotation() > 0:
            if np.sqrt(np.dot(self.cam - paramW - self.at, self.cam - paramW - self.at)) > 2:
                self.cam = self.cam - paramW
                self.Refresh(False)
            else:
                evt.Skip()
        # wheel down -> zoom out
        elif evt.GetWheelRotation() < 0:
            self.cam = self.cam + paramW
            self.Refresh(False)
        else:
            evt.Skip()

    def getWUV(self):
        self.w = (self.cam - self.at) / np.sqrt(np.dot((self.cam - self.at), (self.cam - self.at)))
        if np.dot(np.cross(self.up, self.w), np.cross(self.up, self.w)) != 0:
            self.u = np.cross(self.up, self.w) / np.sqrt(np.dot(np.cross(self.up, self.w), np.cross(self.up, self.w)))
        else:
            self.u = np.array([np.sin(self.azimuth), 0, np.cos(self.azimuth)])
        self.v = np.cross(self.w, self.u) / np.sqrt(np.dot(np.cross(self.w, self.u), np.cross(self.w, self.u)))

    '''def OnSize(self, event):
        print("onsize")
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)'''

    def OnPaint(self, event):
        #print("onpaint")
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnMouseDown(self, evt):
        if evt.LeftIsDown():
            self.mouseDown = True
            self.rmouseDown = False
        elif evt.RightIsDown():
            self.mouseDown = False
            self.rmouseDown = True
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

    def OnMouseUp(self, evt):
        self.rmouseDown = False
        self.mouseDown = False
        self.ReleaseMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and (evt.LeftIsDown() or evt.RightIsDown()):
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            normx = (self.x - self.lastx) * np.sqrt(np.dot((self.cam - self.at), (self.cam - self.at)))/ 300
            normy = (self.y - self.lasty) * np.sqrt(np.dot((self.cam - self.at), (self.cam - self.at))) / 300
            if self.mouseDown:
                param = self.u * normx + self.v * normy
                self.cam = self.cam + param
                self.at = self.at + param
                self.Refresh(False)
            elif self.rmouseDown:
                x_rotate = (self.x - self.lastx) / 100
                y_rotate = (self.y - self.lasty) / 100
                self.leng = np.sqrt(np.dot((self.cam - self.at), (self.cam - self.at)))
                if self.elevation + y_rotate >= np.radians(90):
                    self.elevation = np.radians(89)
                elif self.elevation + y_rotate <= np.radians(-90):
                    self.elevation = np.radians(-89)
                else:
                    self.elevation = self.elevation + y_rotate
                self.azimuth = self.azimuth + x_rotate

                self.cam = np.array([self.leng * np.cos(self.elevation) * np.sin(self.azimuth),
                                     self.leng * np.sin(self.elevation),
                                     self.leng * np.cos(self.elevation) * np.cos(self.azimuth)])
                self.cam = self.cam + self.at
                self.Refresh(False)
        else:
            evt.Skip()

    def InitGL(self):
        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size
        self.ratio = float(w/h)
        glMatrixMode(GL_PROJECTION)
        #glFrustum(-self.ratio, self.ratio, -0.5, 0.5, self.zoom, 25*self.zoom)
        #glViewport(0, 0, w, h)
        gluPerspective(45, float(w/h), 1, 1000)
        # position viewer
        '''glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -2.0)

        # position object
        glRotatef(self.y, 1.0, 0.0, 0.0)
        glRotatef(self.x, 0.0, 1.0, 0.0)'''
        #glScalef(self.zoom, self.zoom, self.zoom)

        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_LIGHTING)
        #glEnable(GL_LIGHT0)


    def OnDraw(self):
        print("Ondraw")
        # clear color and depth buffers

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glScalef(self.zoom, self.zoom, self.zoom)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(self.cam[0], self.cam[1], self.cam[2],
                  self.at[0], self.at[1], self.at[2],
                  self.up[0], self.up[1], self.up[2])

        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size

        '''if self.mouseDown:
            w = max(w, 1.0)
            h = max(h, 1.0)
            xScale = 180.0 / w
            yScale = 180.0 / h
            glRotatef((self.y - self.lasty) * yScale, 1.0, 0.0, 0.0)
            glRotatef((self.x - self.lastx) * xScale, 0.0, 1.0, 0.0)
        elif self.rmouseDown:
            h = max(h, 1.0)
            yScale = 10 / h
            zoomy = (self.y - self.lasty) * yScale
            glTranslatef(0, 0, zoomy)'''

        #glTranslatef(self.zoom, self.zoom, self.zoom)

        # draw six faces of a cube
        drawBox()
        glColor3ub(255, 255, 255)
        glBegin(GL_LINES)
        #glLineWidth(3)
        for i in range(-10, 10):
            glVertex3f(i, 0, 10)
            glVertex3f(i, 0, -10)
        glEnd()
        glBegin(GL_LINES)
        for i in range(-10, 10):
            glVertex3f(10, 0, i)
            glVertex3f(-10, 0, i)
        glEnd()
        drawJoint(self.obj.root)
        self.SwapBuffers()


# ----------------------------------------------------------------------
def drawBox():
    glBegin(GL_QUADS)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)

    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)

    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glEnd()

def getPosition(joint):
    return [joint.worldpos[0], joint.worldpos[1], joint.worldpos[2]]

def drawJoint(joint):
    pos = getPosition(joint)
    #print(joint.name,pos)
    #joint.update_frame(count)
    glPushMatrix()

    glTranslatef(pos[0], pos[1], pos[2])
    drawSphere(12, 12)
    glPopMatrix()
    if joint.parent:
        head = getPosition(joint.parent)
        tail = pos
        #glLineWidth(3)
        glBegin(GL_LINES)
        glVertex3f(head[0], head[1], head[2])
        glVertex3f(tail[0], tail[1], tail[2])
        glEnd();
    for child in joint.children:
        drawJoint(child)


    '''glPushMatrix()
    glTranslatef(float(offset[0]), float(offset[1]), float(offset[2]))
    for channel in joint.channels:
        for i in range(joint.idx[0], joint.idx[1]):
            if channel == "Xposition":
                pos[0] = skeleton.motions[count][i]
                #glTranslatef(pos[0],0,0)
            elif channel == "Yposition":
                pos[1] = skeleton.motions[count][i]
                #glTranslatef(0, pos[1], 0)
            elif channel == "Zposition":
                pos[2] = skeleton.motions[count][i]
                #glTranslatef(0, 0, pos[2])
            elif channel == "Xrotation":
                rot[0] = skeleton.motions[count][i]
                #glRotatef(rot[0], 1, 0, 0)
                x = math.radians(rot[0])
                cos = math.cos(x)
                sin = math.sin(x)
                rot_mat2 = np.array([[1., 0., 0., 0.], [0.,cos, -sin, 0.], [0., sin, cos, 0.], [0., 0., 0., 1.]])
                rot_mat = np.dot(rot_mat, rot_mat2)
            elif channel == "Yrotation":
                rot[1] = skeleton.motions[count][i]
                #glRotatef(rot[1], 0, 1, 0)
                x = math.radians(rot[1])
                cos = math.cos(x)
                sin = math.sin(x)
                rot_mat2 = np.array([[cos, 0., sin, 0.], [0., 1., 0, 0.], [-sin, 0, cos, 0.], [0., 0., 0., 1.]])
                rot_mat = np.dot(rot_mat, rot_mat2)
            elif channel == "Zrotation":
                rot[2] = skeleton.motions[count][i]
                #glRotatef(math.radians(rot[2]), 0, 0, 1)
                #glRotatef(rot[2], 0, 0, 1)
                x = math.radians(rot[2])
                cos = math.cos(x)
                sin = math.sin(x)
                rot_mat2 = np.array([[cos, -sin, 0., 0.], [sin, cos, 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])
                rot_mat = np.dot(rot_mat, rot_mat2)
    #glTranslatef(offset[0], offset[1], offset[2])

    glTranslatef(pos[0], pos[1], pos[2])
    glMultMatrixf(rot_mat.T)
    drawSphere(12, 12)
    for child in joint.children:
        glBegin(GL_LINES)
        glVertex3f(0,0,0)
        glVertex3fv(child.offset)
        glEnd()
        drawJoint(child,skeleton,count)'''


    #glRotatef(0, rot[0], rot[1], rot[2])
    #glMultMatrixf(rot_mat.T)
    #drawSphere(12, 12)
    #drawCube()

    #glPopMatrix()


def drawSphere(numLats, numLongs):
    for i in range(0, numLats + 1):
        lat0 = np.pi * (-0.5 + float(float(i - 1) / float(numLats)))
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)
        lat1 = np.pi * (-0.5 + float(float(i) / float(numLats)))
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)
        # Use Quad strips to draw the sphere
        glBegin(GL_QUAD_STRIP)
        for j in range(0, numLongs + 1):
            lng = 2 * np.pi * float(float(j - 1) / float(numLongs))
            x = np.cos(lng)
            y = np.sin(lng)
            glVertex3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr1, y * zr1, z1)
        glEnd()


if __name__ == '__main__':
    app = wx.App(False)
    frm = wx.Frame(None, title='GLCanvas Sample',size = (640,640))
    canvas = MyCanvasBase(frm)
    #canvas.SetSize((640,640))
    frm.Show()
    app.MainLoop()



# ----------------------------------------------------------------------
