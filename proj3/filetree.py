class TreeNode(object):
    def __init__(self, folder, isFile):
        self.name = folder
        self.isFile = isFile
        self.parent = None
        self.child = {}

class FileTree(object):
    def __init__(self):
        self.root = TreeNode('', 0)

    def insert_node(self, path, isFile):
        isFound, cur, folder = self.find_node(path)
        path_folder = path.split('/')
        if isFound == 2:
            print("Wrong path!")
            return
        elif isFound == 1:
            print("File already exists")
        else:
            new = TreeNode(folder, 1)
            new.parent = cur
            cur.child[folder] = new


    def find_node(self, path):
        path_folder = path.split('/')
        if path_folder[0] != '':
            return 2, None, None
        cur = self.root
        for folder in path_folder[1::]:
            parent = cur
            cur = cur.child.get(folder)
            if cur is None:
                return 0, parent, folder
        if cur.isFile is True:
            return 1, None, None
        else:
            return 0, parent, folder

    def list(self, node, meta):
        chunkSize = 2 * 1024 * 1024
        if node == self.root:
            node.name = '/'
        print(node.name+'\t'+meta[node.name][0]+'\t'+int(meta[node.name][1]/chunkSize))
        for key in list(node.child.keys()):
            list(node.child[key], meta)

    def list(self, meta):
        self.list(self.root, meta)
