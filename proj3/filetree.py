class TreeNode(object):
    def __init__(self, folder, isFile):
        self.name = folder
        self.isFile = isFile
        self.parent = None
        self.child = {}

class FileTree(object):
    def __init__(self):
        self.root = TreeNode('', 0)
        self.cur_node = self.root

    def insert_node(self, path, isFile):
        path_ = self.get_whole_path_(path)
        path_folder = path_.split('/')
        isFound, cur, folder = self.find_node(path)
        if isFound == 2:
            print("Path doesn't exist!")
            return 2
        elif isFound == 1:
            print("File already exists")
            return 1
        else:
            if len(path_folder) is not 1:
                if cur.name != path_folder[-2]:
                    print("Path doesn't exist!")
                    return 2
            new = TreeNode(folder, isFile)
            new.parent = cur
            cur.child[folder] = new
            return 0


    def find_node(self, path):
        path_folder = path.split('/')
        cur = self.cur_node
        for folder in path_folder:
            if folder == '..':
                cur = cur.parent
                continue
            elif folder == '.':
                continue
            elif folder == '':
                print('Wrong path!')
                return 2, None, None
            parent = cur
            cur = cur.child.get(folder)
            if cur is None:
                return 0, parent, folder
        if cur.isFile is True:
            return 1, None, None
        else:
            return 0, parent, folder

    def listt(self, node, meta, path):
        chunkSize = 2 * 1024 * 1024
        path_cur = path
        for key in list(node.child.keys()):
            if key == []:
                return
            path_child = path_cur + '/' + key
            if meta.get(path_child) is not None:
                print(path_child + '\t' + str(meta[path_child][0]) + '\t' + str(int(meta[path_child][1] / chunkSize)))
            elif meta.get(path_child) is None and node.child[key].isFile == True:
                print('No data', path_child, 'in meta!')
                return
            self.listt(node.child[key], meta, path_child)

    def list_(self, meta):
        self.listt(self.root, meta, path='')

    def ls_(self):
        for key in list(self.cur_node.child.keys()):
            if key == []:
                return
            print(key, end='\t')
        print()

    def cd_(self, folder_path):
        path_split = folder_path.split('/')
        for folder in path_split:
            if folder == '..':
                if self.cur_node.parent == None:
                    print("Path doesn't exist!")
                    return 1
                self.cur_node = self.cur_node.parent
            elif folder == '.':
                self.cur_node = self.cur_node
            else:
                if self.cur_node.child.get(folder) is None:
                    print("Path doesn't exist!")
                    return 1
                self.cur_node = self.cur_node.child[folder]

    def get_whole_path_(self, filename):
        list = []
        temp = self.cur_node
        path = ''
        while temp.name != '':
            list.append(temp.name)
            temp = temp.parent
        list.reverse()
        for folder in list:
            path = path + '/'
            path = path + folder
        return path+'/'+filename

    def rm_(self, path):
        isFound, cur, folder = self.find_node_rm(path)
        if isFound == 1:
            print("Wrong path!")
            return
        elif isFound == 0:
            del cur.child[folder]
            return

    def find_node_rm(self, path):
        path_folder = path.split('/')
        cur = self.cur_node
        for folder in path_folder:
            if folder == '..':
                cur = cur.parent
                continue
            elif folder == '.':
                continue
            elif folder == '':
                print('Wrong path!')
                return 1, None, None
            parent = cur
            cur = cur.child.get(folder)
            if cur is None:
                return 1, None, None
            else:
                return 0, parent, folder
