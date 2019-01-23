class Joint:
    def __init__(self):
        self.name = None
        self.channels = []
        self.offset = []
        self.parent = None
        self.children = []
        self.idx = [0,0]




class bvhreader:
    def __init__(self,filename):
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
                vals = []
                for token in tokens:
                    vals.append(float(token))
                self.motions.append(vals)
        #self.printHierarchyJoint(self.__root)
        #print(self.channel_num)
        print(len(self.motions))

    def printHierarchyJoint(self, joint, indent = ''):
        print(indent, joint.name)
        for child in joint.children:
            self.printHierarchyJoint(child, indent+"  ")