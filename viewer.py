import numpy as np
class Joint:
    def __init__(self):
        self.name = None
        self.channels = []
        self.offset = []
        self.parent = None
        self.frames = []
        self.children = []
        self.idx = [0, 0]
        self.rot_mat = np.identity(4)
        self.trans_mat = np.identity(4)
        self.strans_mat = np.identity(4)
        self.localtoworld = np.identity(4)
        self.trtr = np.identity(4)
        self.worldpos = np.array([0, 0, 0, 0])


    def update_frame(self, frame):
        pos = [0., 0., 0.]
        rot = [0., 0., 0.]

        rot_mat = np.identity(4)
        trans_mat = np.identity(4)

        for idx, channel in enumerate(self.channels):
            if channel == 'Xposition':
                pos[0] = self.frames[frame][idx]
                trans_mat[0, 3] = pos[0]
            elif channel == 'Yposition':
                pos[1] = self.frames[frame][idx]
                trans_mat[1, 3] = pos[1]
            elif channel == 'Zposition':
                pos[2] = self.frames[frame][idx]
                trans_mat[2, 3] = pos[2]
            elif channel == 'Xrotation':
                rot[0] = self.frames[frame][idx]
                cos = np.cos(np.radians(rot[0]))
                sin = np.sin(np.radians(rot[0]))
                rot_mat2 = np.identity(4)
                rot_mat2[1, 1] = cos
                rot_mat2[1, 2] = -sin
                rot_mat2[2, 1] = sin
                rot_mat2[2, 2] = cos
                rot_mat = np.dot(rot_mat, rot_mat2)
            elif channel == 'Yrotation':
                rot[0] = self.frames[frame][idx]
                cos = np.cos(np.radians(rot[0]))
                sin = np.sin(np.radians(rot[0]))
                rot_mat2 = np.identity(4)
                rot_mat2[0, 0] = cos
                rot_mat2[0, 2] = sin
                rot_mat2[2, 0] = -sin
                rot_mat2[2, 2] = cos
                rot_mat = np.dot(rot_mat, rot_mat2)
            elif channel == 'Zrotation':
                rot[0] = self.frames[frame][idx]
                cos = np.cos(np.radians(rot[0]))
                sin = np.sin(np.radians(rot[0]))
                rot_mat2 = np.identity(4)
                rot_mat2[0, 0] = cos
                rot_mat2[0, 1] = -sin
                rot_mat2[1, 0] = sin
                rot_mat2[1, 1] = cos
                rot_mat = np.dot(rot_mat, rot_mat2)

        self.rot_mat = rot_mat
        self.trans_mat = trans_mat

        if self.parent:
            self.localtoworld = np.dot(self.parent.trtr, self.strans_mat)
        else:
            self.localtoworld = np.dot(self.strans_mat, self.trans_mat)

        self.trtr = np.dot(self.localtoworld, self.rot_mat)

        self.worldpos = np.array([self.localtoworld[0, 3],
                                  self.localtoworld[1, 3],
                                  self.localtoworld[2, 3],
                                  self.localtoworld[3, 3]])

        for child in self.children:
            child.update_frame(frame)



class bvhreader:
    def __init__(self, filename):
        self.filename = filename

        self.__root = None
        self.__stack = []
        self.channel_num = 0
        self.frame_time = 0.3
        self.frames = 0
        self.motions = []
        self.loadbvh(self.filename)

    @property
    def root(self):
        return self.__root

    def loadbvh(self, filename):
        f = open(filename)
        lines = f.readlines()
        parent = None
        current = None
        motion = False

        for line in lines[1:len(lines)]:
            tokens = line.split()
            if len(tokens) == 0:
                continue
            if tokens[0] in ["ROOT", "JOINT", "End"]:
                if current is not None:
                    parent = current

                current = Joint()
                current.name = tokens[1]
                current.parent = parent
                if len(self.__stack) == 0:
                    self.__root = current

                if current.parent is not None:
                    current.parent.children.append(current)

                self.__stack.append(current)

            elif "{" in tokens[0]:
                ...
            elif "OFFSET" in tokens[0]:
                offset = []
                for i in range(1, len(tokens)):
                    offset.append(float(tokens[i]))
                current.offset = offset
                current.strans_mat[0, 3] = offset[0]
                current.strans_mat[1, 3] = offset[1]
                current.strans_mat[2, 3] = offset[2]
            elif "CHANNELS" in tokens[0]:
                current.channels = tokens[2:len(tokens)]
                current.idx = [self.channel_num,self.channel_num + len(current.channels)]
                self.channel_num += len(current.channels)

            elif "}" in tokens[0]:
                #print(current.name)
                current = current.parent
                if current:
                    parent = current.parent

            elif "MOTION" in tokens[0]:
                motion = True
            elif "Frames:" in tokens[0]:
                self.frames = int(tokens[1])
            elif "Frame" in tokens[0]:
                self.frame_time = float(tokens[2])
            elif motion:
                data = [float(token) for token in tokens]
                self.get_channel_data(self.__root,data)
                #지우기
                vals = []
                for token in tokens:
                    vals.append(float(token))
                self.motions.append(vals)
        #self.printHierarchyJoint(self.__root)
        #print(self.channel_num)
        #print(len(self.motions))

    def get_channel_data(self, joint, data):
        channels = len(joint.channels)
        joint.frames.append(data[0:channels])
        data = data[channels:]

        for child in joint.children:
            data = self.get_channel_data(child, data)

        return data

    def update_frame(self,frame):
        self.root.update_frame(frame)

    def printHierarchyJoint(self, joint, indent = ''):
        print(indent, joint.name , joint.idx, joint.offset, joint.frames[1])
        for child in joint.children:
            self.printHierarchyJoint(child, indent+"  ")