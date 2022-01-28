"""
    A simplified model of iOS Home Screen
    
    Assumptions:
    - App names are unique and are used as App ID's (or bundle ID's)
    - Folder names are also unique
    - An app and a folder cannot have the same name
    - Names are case insensitive 
"""

from ast import Pass
from collections import deque

# Enum for 
class Item_Types:
    APP = 1
    FOLDER = 2

class Node:
    next = None
    prev = None
    name = ""
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name
    
class DoublyLinkedList:
    def __init__(self, nodes=None, capacity=None):
        self.head = None
        self.tail = self.head
        self.size = 0
        self.capacity = capacity
        
        if nodes is not None:
            # curr_node = Node(name=nodes.pop(0))
            curr_node = nodes.pop(0)
            self.size += 1
            
            self.head = curr_node
            self.tail = curr_node
            
            for node in nodes:
                curr_node.next = node
                curr_node.next.prev = curr_node
                curr_node = curr_node.next
                self.size += 1
                
            self.tail = curr_node
                
    def __repr__(self):
        curr_node = self.head
        nodesLTR = []

        nodesLTR.append("None")
        while curr_node is not None:
            nodesLTR.append(curr_node.name)
            curr_node = curr_node.next
        nodesLTR.append("None")
        
        curr_node = self.tail
        nodesRTL = []

        nodesRTL.append("None")
        while curr_node is not None:
            nodesRTL.append(curr_node.name)
            curr_node = curr_node.prev
        nodesRTL.append("None") 
        
        nodesRTL.reverse()
        
        ltr = " -> ".join(nodesLTR)
        rtl = " <- ".join(nodesRTL)
        
        return f"{ltr}\n{rtl}"
    
    def __iter__(self):
        node = self.head
        while node is not None:
            yield node
            node = node.next
            
    def push(self, new_node):
        if self.capacity is not None:
            if self.size == self.capacity:
                print("Cannot add any more items. Capacity reached.")
                return
            
        if self.size == 0 and self.head == None and self.tail is None:
            self.head = new_node
            self.tail = new_node
            new_node.next = None
            new_node.prev = None
            self.size +=  1
            return 
        
        new_node.prev = self.tail
        if new_node.prev is not None:
            new_node.prev.next = new_node
        self.tail = new_node
        # make sure the node is not linked to anything else
        new_node.next = None
        self.size +=  1
    
    def pop(self):
        if self.size == 0:
            return None
        
        return self.remove(self.tail)
    
    def peak(self): 
        return self.tail
    
    def push_front(self, new_node):
        if self.capacity is not None:
            if self.size == self.capacity:
                print("Cannot add any more items. Capacity reached.")
                return
            
        if self.size == 0 and self.head == None and self.tail is None:
            self.push(new_node)
            return 
            
        new_node.next = self.head
        
        if new_node.next is not None:
            new_node.next.prev = new_node
            
        self.head = new_node
        # make sure the node is not linked to anything else
        new_node.prev = None
        self.size +=  1
    
    def pop_front(self):
        if self.size == 0:
            return None
        
        return self.remove(self.head)
    
    def peak_front(self):
        return self.head
    
    def remove(self, node):
        # if there is only 1 or 0 nodes in the list 
        if self.size <= 1 and node.next is None and node.prev is None:
            self.head = None
            self.tail = None
            self.size -= 1
            return
        
        if node.prev is not None:
            node.prev.next = node.next
        else: # then it must be the first node
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else: # then it must be the last node
            self.tail = node.prev
            
        node.next = None
        node.prev = None
        
        self.size -= 1
        
        return node
    
    def at_index(self, index):
        if index >= self.size or index < 0:
            return None
        
        curr_node = self.head
        i = 0
        
        while curr_node is not None:
            if i == index:
                return curr_node
            curr_node = curr_node.next
            i += 1
        return None
    
    def get_index(self, node):
        if node is None:
            return None
        
        curr_node = self.head
        i = 0
        
        while curr_node is not None:
            if type(node) is str:
                if curr_node.name == node:
                    return i
            elif issubclass(type(node), Node):
                if curr_node.name == node.name:
                    return i
            else:
                raise Exception("the input must be either str or Node")
            curr_node = curr_node.next
            i += 1
            
        return None
        
    
    def add_at_index(self, index, new_node):
        if self.capacity is not None:
            if self.size == self.capacity:
                print("Cannot add any more items. Capacity reached.")
                return
            
        if index < 0 or index > self.size:
            raise Exception("Invalid index")
        
        if self.size == 0 or index == self.size:
            self.push(new_node)
            
        elif index == 0:
            self.push_front(new_node)
            
        else:
            node = self.at_index(index)
            self.add_before(node, new_node) 
        
            
        
    def add_after(self, node, new_node):
        if self.capacity is not None:
            if self.size == self.capacity:
                print("Cannot add any more items. Capacity reached.")
                return
        
        if type(node) is str:
            node_name = node
            node = self.find(node)
            if node is None:
                raise Exception(f"'{node_name}' is not in the list")
            
        if self.size == 0 or node is None:
            raise Exception("Cannot add a new node after another node in an empty list")
        
        if node.next is None: # if adding after the last element
            self.tail = new_node
        new_node.next = node.next
        node.next = new_node
        new_node.prev = node
        if new_node.next is not None:
            new_node.next.prev = new_node
        self.size += 1
        
    def add_before(self, node, new_node):
        if self.capacity is not None:
            if self.size == self.capacity:
                print("Cannot add any more items. Capacity reached.")
                return
            
        if type(node) is str:
            node_name = node
            node = self.find(node)
            if node is None:
                raise Exception(f"'{node_name}' is not in the list")
            
        if self.size == 0 or node is None:
            raise Exception("Cannot add a new node after another node in an empty list")
        
        if node.prev is None: # if adding before the first node
            self.head = new_node
        new_node.next = node
        new_node.prev = node.prev
        node.prev = new_node
        if new_node.prev is not None:
            new_node.prev.next = new_node
        self.size += 1
         
    
    def find(self, name):
        curr_node = self.head
        
        while curr_node is not None:
            if curr_node.name == name:
                return curr_node
            curr_node = curr_node.next
        
        return None
    


class Home:
    # private variables
    _apps = dict() # dict[str, item] contains all the apps
    _folders = dict() # dict[str, item] contains all folders
    _dock = None
    _pages = None 
    _open_apps = deque()
    
    def __init__(
        self, 
        apps=["Phone", "Mail", "Safari", "Music", "Maps", "Clock", "Settings", "Camera", "Notes"], 
        page_columns=3, 
        page_rows=4, 
        max_pages=5, 
        dock_capacity=4
        ) -> None:
        
        self.page_columns = page_columns 
        self.page_rows = page_rows
        self.page_capacity = page_rows * page_columns
        self.max_pages = max_pages 
        self.max_apps = int(self.page_capacity * max_pages * 0.5) # to avoid issues, only account for half of the page would be filled with apps
        self.dock_capacity = dock_capacity
        
        self._dock = DoublyLinkedList(capacity=self.dock_capacity)
        self._pages = DoublyLinkedList(capacity=self.max_pages)
        
        
        for idx, app in enumerate(apps):
            if len(self._apps) == self.max_apps:
                break
            
            self.add_app(app) # add_app() abstracts adding an app into the correct page
            self._apps.add(app.name, app)
            
            # Move the first 3 items into the dock
            if idx < 3:
                self._dock.push(app)
     
     
    def add_app(self, app_name):
        if app_name in self._apps:
            print(f"{app_name} already exists")
            return
            
        if len(self._apps) == self.max_apps:
            print(f"Max capacity reached. Cannot add {app_name}")
            return 
        new_app = App(app_name)
        self._apps.add(app_name, new_app)
        
        if self._pages.tail.items.size != self.page_capacity:
            self._pages.tail.items.push(new_app)
            return
            
        else:
            if self._pages.size != self.max_pages:
                self._pages.push(Page(id=self._pages.size, items=[new_app]))
                
            else: # go from the last page to the first page and see if there is an opening to add the app to
                curr_page = self._pages.tail.prev # start the search from the page to the last 
                
                while curr_page is not None:
                    if curr_page.items.size != self.page_capacity:
                        curr_page.items.push(new_app)
                        return
                    
                    curr_page = curr_page.prev  
                
                
        
    
    def open_app(self, app_name):
        app = self._apps.get(app_name, None)
        
        if app is not None:
            app.run()
            if app not in self._open_apps:
                self._open_apps.append(app)
        else:
            print(f"Could not find '{app_name}'")
    
    # def close_app(self, app_name):
    #     pass
    
    def terminate_app(self, app_name):
        if self._apps[app_name] in self._open_apps:
            self._open_apps.remove(self._apps[app_name])
    
    def delete_app(self, app_name):
        app = self._apps.get(app_name, None)
        if app is not None:
            page = app.page
            page.items.remove(app)
            self._apps.pop(app_name)
            
            if page.items.size == 0:
                self._pages.remove(page)
            
        
    def get_open_apps(self):
        return self._open_apps
    
    def move_app(self, app, page_number, position_in_page):
        pass
    
    def create_folder(self, folder_name, apps):
        pass
    
    def move_apps_to_folder(self, folder, apps):
        pass
    
    def remove_apps_from_folder(self, folder, apps):
        pass
    
     
    # private methods   

        
#     currentPage: Page

#     pages: [Page]
#     dock: Dock

#     def addPage(page: Page)

#     def removePage(page: Page):
#         pass

#     def movePage(page: Page, position: int):
#         pass

#     def moveItemAcrossPages(item, page)


class Container:
    items = []

    def removeItem(Item) -> object:
        pass

    def addItem(Item):
        pass

    def moveItem(Item, position):
        pass


class Page(Container):
    pass
    # id: int
    # nextPage: Page?
    # previousPage

    # items



# class Item:
#     name: str
#     appBundleID: str
#     nextItem: Item
#     previousItem: Item




# class AppItem(Item):


# class FolderItem(Item, Container):
    

class Simulation:
    home = None
    def __init__(self) -> None:
        self.home = Home()
        
    def run(self):
        while(True):
            cmd = input("Enter a command (type in help to see the available options): \n")
                    
            if cmd.strip().lower() == "q" or cmd == "quit":
                print("Quitting...")
                break
            
            # parse_input(cmd)
            # render_home_screen()
        

    def parse_input(self, cmd):
        cmd = cmd.strip()
        
        if cmd.lower() == "help":
            self.display_help()
            

            
        
            
            
            

    def display_help(self):
        help = """
        Add App:                    add <app name>
        Remove App:                 remove <app name>
        Move App:
            - to another page:      move <app name> page <page number>
            - to folder:            move <app name> folder <folder name>
            - to new page:          move <app name> newpage
            - to dock               move <app name> dock
            
        Open App:                   open <app name>
        Open Folder:                open <folder name>
        Close App:                  close <app name>
        Close Folder:               close <folder name>
        Terminate App:              quit <app name>
        Show Open Apps:             
        
        
        """

if __name__ == "__main__":
    try:
        simulation = Simulation()
        simulation.run()
    except Exception as err:
        print(f"Exception occurred: {str(err)}")
        
    
    
    
    