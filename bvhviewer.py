import glfw
from OpenGL.GL import *
import numpy as np
from viewer import bvhreader
import math
from OpenGL.GLU import *
number = 1
count = 0
global gComposedM
angle = np.radians(0)
def render(camAng,count,skeleton):
    a = 0
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glClear(GL_COLOR_BUFFER_BIT |GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glOrtho(-1,1, -1,1, -1,1)
    #gluLookAt(.1*np.sin(camAng),.1,.1*np.cos(camAng), 0,0,0, 0,1,0)
    myLookAt(np.array([.1*np.sin(camAng),.1,.1*np.cos(camAng)]),np.array([0,0,0]),np.array([0,1,0]))
    '''th = np.radians(-60)
    R = np.array([[1,0,0,0],
                  [0,np.cos(th),-np.sin(th),0],
                  [0., np.sin(th), np.cos(th),0.],
                  [0.,0.,0.,1.]])
    T = np.array([[1.,0.,0.,.4],
                  [0.,1.,0.,0.],
                  [0.,0.,1.,.2],
                  [0.,0.,0.,1.]])
    drawFrame()
'''
    glScalef(.003, .003, .003)
    glPushMatrix()
    drawJoint(skeleton.root,skeleton,count)
    glPopMatrix()

angle

def drawJoint(joint,skeleton,count):
    offset = joint.offset
    rot = [0,0,0]
    pos = [0,0,0]
    #print(joint.name,pos)
    rot_mat = np.array([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])

    glPushMatrix()
    glTranslatef(float(offset[0]), float(offset[1]), float(offset[2]))
    for channel in joint.channels:
        for i in range(joint.idx[0], joint.idx[1]):
            if channel == "Xposition":
                pos[0] = skeleton.motions[count][i]
                glTranslatef(pos[0],0,0)
            elif channel == "Yposition":
                pos[1] = skeleton.motions[count][i]
                glTranslatef(0, pos[1], 0)
            elif channel == "Zposition":
                pos[2] = skeleton.motions[count][i]
                glTranslatef(0, 0, pos[2])
            if channel == "Xrotation":
                rot[0] = skeleton.motions[count][i]
                #glRotatef(rot[0], 1, 0, 0)
                x = math.radians(rot[0])
                cos = math.cos(x)
                sin = math.sin(x)
                rot_mat2 = np.array([[1., 0., 0., 0.], [0.,cos, -sin, 0.], [0., sin, cos, 0.], [0., 0., 0., 1.]])
                rot_mat = np.dot(rot_mat,rot_mat2)
            elif channel == "Yrotation":
                rot[1] = skeleton.motions[count][i]
                #glRotatef(rot[1], 0, 1, 0)
                x = math.radians(rot[1])
                cos = math.cos(x)
                sin = math.sin(x)
                rot_mat2 = np.array([[cos, 0., -sin, 0.], [0., 1., 0, 0.], [sin, 0, cos, 0.], [0., 0., 0., 1.]])
                rot_mat = np.dot(rot_mat, rot_mat2)
            elif channel == "Zrotation":
                rot[2] = skeleton.motions[count][i]
                glRotatef(rot[2], 0, 0, 1)
                x = math.radians(rot[2])
                cos = math.cos(x)
                sin = math.sin(x)
                rot_mat2 = np.array([[cos, -sin, 0., 0.], [sin, cos, 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])
                rot_mat = np.dot(rot_mat, rot_mat2)
    glMultMatrixf(rot_mat.T)
    drawSphere(12, 12)


    #glRotatef(0, rot[0], rot[1], rot[2])
    #glMultMatrixf(rot_mat.T)
    #drawSphere(12, 12)
    #drawCube()
    for child in joint.children:
        glBegin(GL_LINES)
        glVertex3f(0,0,0)
        glVertex3fv(child.offset)
        glEnd()
        drawJoint(child,skeleton,count)
    glPopMatrix()



def drawBox():
    glBegin(GL_QUADS)
    glVertex3fv(np.array([1, 1, 0.]))
    glVertex3fv(np.array([-1, 1, 0.]))
    glVertex3fv(np.array([-1, -1, 0.]))
    glVertex3fv(np.array([1, -1, 0.]))
    glEnd()


def myLookAt(eye,at,up) : # eye, at, up are 1D numpy array of length 3
    w = (eye-at)
    w = w/ np.sqrt(np.dot(w,w))
    u = np.cross(up,w)
    u = u / np.sqrt(np.dot(u,u))
    v = np.cross(w,u)
    m = np.identity(4)
    m[:3,0] = u
    m[:3,1] = v
    m[:3,2] = w
    m[:3,3] = eye
    m = np.linalg.inv(m)
    glMultMatrixf(m.T)


def drawtower() :
    global count
    glPushMatrix()
    #glTranslatef(0, -.4, 0)
    # glTranslatef(.6*np.cos(np.radians(count)), 0,.6*  np.sin(np.radians(count)))
    # 가운데 기둥 그리기
    glPushMatrix()
    glScalef(.1, .3, .1)
    drawCube()
    glPopMatrix()

    glPushMatrix()
    # glRotatef(count, 1, 0, 0)    # y축기준으로 원뿔형태로 돌리고싶어
    glTranslatef(0, .3, 0)
    glRotatef(count%360, 0, 0, 1)
    glPushMatrix()
    # glRotatef(60, 0, 0, 1)
    glScalef(.05, .5, .05)
    # glTranslatef(0,-.5,0)
    drawCube()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -.5, 0)
    glTranslatef(0, 1 / 360 * (count % 360), 0)
    glPushMatrix()
    # glTranslatef(.0, -.5, 0)
    glScalef(.1, .1, .1)
    drawSphere(15, 15)
    glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    glPopMatrix()


def drawCube():
    glBegin(GL_QUADS)
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(1.0, 1.0, -1.0)
    glVertex3f(1.0, 1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glEnd()

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

def key_callback(window, key, scancode, action, mods):
    global gComposedM
    global angle
    if action == glfw.PRESS or action ==glfw.REPEAT:
        if key == glfw.KEY_Q: # trans by -0.1 in x direction , global
            T= np.array([[1,0,0,-0.1],
                         [0,1,0,0],
                         [0,0,1,0],
                         [0,0,0,1]])
            gComposedM = T @ gComposedM
        elif key == glfw.KEY_E: # trans by 0.1 in x direction , global
            T= np.array([[1,0,0,0.1],
                         [0,1,0,0],
                         [0,0,1,0],
                         [0,0,0,1]])
            gComposedM = T @ gComposedM
        elif key == glfw.KEY_A : #rotate y axis by 10 clockwise,local
            T = np.array([[np.cos(np.radians(-10)),0,np.sin(np.radians(-10)),0],
                          [0,1,0,0],                            
                          [-np.sin(np.radians(-10)),0,np.cos(np.radians(-10)),0],
                          [0,0,0,1]])
            gComposedM = gComposedM @ T
        elif key == glfw.KEY_D: # rotate y by 10 counterclock ,local
            T = np.array([[np.cos(np.radians(10)),0,np.sin(np.radians(10)),0],
                          [0,1,0,0],                            
                          [-np.sin(np.radians(10)),0,np.cos(np.radians(10)),0],
                          [0,0,0,1]])
            gComposedM = gComposedM @ T
        elif key == glfw.KEY_W : # rotate x axis by 10 clock , local
            T = np.array([[1,0,0,0],
                          [0,np.cos(np.radians(-10)),-np.sin(np.radians(-10)),0],
                          [0,np.sin(np.radians(-10)),np.cos(np.radians(-10)),0],
                          [0,0,0,1]])
            gComposedM = gComposedM @ T
        elif key == glfw.KEY_S:  # rotate x axis by 10 counterclock , local
            T = np.array([[1,0,0,0],
                          [0,np.cos(np.radians(10)),-np.sin(np.radians(10)),0],
                          [0,np.sin(np.radians(10)),np.cos(np.radians(10)),0],
                          [0,0,0,1]])
            gComposedM = gComposedM @ T
        if key == glfw.KEY_1: #rotate camera 10 clockwise
            angle +=np.radians(-10)
        elif key == glfw.KEY_3: #rotate camera 10 counterclockwise
             angle +=np.radians(10)

'''def cursor_callback(window, xpos, ypos):
    print('mouse cursor moving: (%d, %d)'%(xpos, ypos))

def button_callback(window, button, action, mod):
    if button==glfw.MOUSE_BUTTON_LEFT:
        if action==glfw.PRESS:
            print('press left btn: (%d, %d)'%glfw.get_cursor_pos(window))
        elif action==glfw.RELEASE:
            print('release left btn: (%d, %d)'%glfw.get_cursor_pos(window))
            
def scroll(window,xoffset,yoffset):
    print("mouse wheel scroll : %d, %d" %(xoffset,yoffset))'''
    
def main():
    global count
    a = 0
    global gComposedM
    global angle
    gComposedM = np.array([[1,0,0,0],
                           [0,1,0,0],
                           [0,0,1,0],
                           [0,0,0,1]])
    skeleton = bvhreader('test_mocapbank.bvh')
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2014004675",None,None)
    if not window:
        glfw.terminate()
        return
    glfw.set_key_callback(window,key_callback)
    '''glfw.set_cursor_pos_callback(window,cursor_callback)
    glfw.set_mouse_button_callback(window,button_callback)
    glfw.set_scroll_callback(window,scroll)'''
    # Make the window's context current
    glfw.make_context_current(window)
# Loop until the user closes the window
    glfw.swap_interval(int(skeleton.frame_time))
    count = 0
    while not glfw.window_should_close(window):
        # Poll events
        glfw.poll_events()

        #camAng = angle
        render(angle,count%skeleton.frames,skeleton)
# Render here, e.g. using pyOpenGL
        #render(T)
        #render(R)
        #render(gComposedM)
# Swap front and back buffers
        glfw.swap_buffers(window)
        count += 1
    glfw.terminate()

if __name__ == "__main__":
    main()








