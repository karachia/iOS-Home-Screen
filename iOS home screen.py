"""
    A simplified data model of iOS Home Screen
    
    General Design:
    This design utilizes a Doubly Linked List (implemented in this file as well) for holding apps and folders within pages or dock.
    Using doubly linked list allows storing the home screen data (apps, folders) in the same order as they will be represented to the user in the UI in pages, dock, and folders.
    It also enables moving the apps and folders around easily without any extra cleaning and re-ordering, or shifting items back and forth as one would do in an array list. 
    
    Pages are also stored in the doubly linked list to support adding and deleting pages in the middle of the list optimally, and to keep the same order as the pages are represented to the user in the UI.
    
    Assumptions:
    - App names are unique and are used as app ID's (or bundle ID's)
    - Folder names are also unique
"""

from collections import deque
import traceback
import uuid

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
    
class Item(Node):
    def __init__(self, name, parent=None):
        super().__init__(name)
        self.parent = parent
    
class App(Item):
    def __init__(self, name, parent=None):
        """Constructor for App

        Args:
            name (str): name of the App. It also acts as app's unique ID / bundle ID
            parent (Single_Page_Container, optional): The page/container in which the app resides). Defaults to None.
        """
        super().__init__(name, parent=parent)
                
    def run(self):
        print(f"{self.name} is running...")
        
        
class Single_Page_Container(Node):
    """A container class for Items"""
    
    _items = None
    def __init__(self, name, items, capacity):
        """Constructor

        Args:
            name (str): Name of the container
            items ([Items]): List of Items to hold
            capacity (int): Maximum capacity of the items the container can hold
        """
        super().__init__(name)
        self._items = DoublyLinkedList(capacity=capacity)
        
        if items:
            for item in items:
                self.add_item(item)
    @property
    def container_type(self):
        return "single_page_container"
        
    @property
    def size(self):
        return self._items.size
    
    @property
    def capacity(self):
        return self._items.capacity
            
    @property
    def items(self):
        return self._items
    
    def add_item(self, item):
        item.parent = self
        self._items.push(item)
        
    def add_item_at_index(self, item, index):
        item.parent = self
        self._items.add_at_index(index, item)
        
    def add_item_to_end(self, item):
        item.parent = self
        self._items.push(item)
        
    def remove_item(self, item):
        item = self._items.remove(item)
        item.parent = None
        return item
    
    def remove_last_item(self):
        app = self._items.pop()
        app.parent = None
        return app
    
        
class Dock(Single_Page_Container):
    """Represents the iOS Dock. It extends Single_Page_Container class and its name property is set to 'Dock'"""
    def __init__(self, capacity):
        super().__init__(name="Dock", items=None, capacity=capacity)
        
    @property
    def container_type(self):
        return "dock"
        
class Page(Single_Page_Container):   
    def __init__(self, items, capacity):
        self.id = str(uuid.uuid4())
        super().__init__(name=f"page_{self.id}", items=items, capacity=capacity) 
        
    @property
    def container_type(self):
        return "page"
        
class Multi_Page_Container:
    """A container class for Apps that supports organizing apps across multiple Pages"""
        
    def __init__(
        self, 
        apps=None,
        page_columns=3, 
        page_rows=4, 
        max_pages=3,
    ):
        self.page_columns = page_columns 
        self.page_rows = page_rows
        self.page_capacity = page_rows * page_columns
        self.max_pages = max_pages 
        
        self._pages = DoublyLinkedList(capacity=self.max_pages)
        
        if max_pages:
            self.max_apps = int(self.page_capacity * max_pages) 
        else:
            self.max_apps = None
        
        for app in apps:
            self.add_app(app) # add_app() abstracts adding an app into the correct page
            
    @property
    def pages(self):
        return self._pages
    
    def add_app(self, app_name):
        """Adds a new app to the home screen (similar to installing a new app)

        Args:
            app_name (str): name of the app to be added

        Returns:
            App: the instance of created app object
        """
        new_app = App(app_name)
                   
        # if there are no pages yet or the last page has reached capacity of apps and folders within it
        if self._pages.tail is None or self._pages.tail.size == self.page_capacity:
            # try creating a new page and adding the app to it, only if the max number of pages has not been reached yet 
            if self._pages.size != self.max_pages:
                self._pages.push(Page(items=[new_app], capacity=self.page_capacity))
                return new_app
            
            # Otherwise go from the last page to the first page and see if there is an opening to add the app to    
            else: 
                curr_page = self._pages.tail.prev # start the search from the page to the last 
                
                while curr_page is not None:
                    if curr_page.size() < curr_page.capacity:
                        curr_page.add_item(new_app)
                        return new_app
                    
                    curr_page = curr_page.prev  
                
                # If no open position is found for this new app, return non
                print(f"Error: Failed to add the new app '{new_app.name}'. Could not find an open position in any of the pages. ")
                return None 
        
        # Otherwise add the app to the last page
        else:
            self._pages.tail.add_item(new_app)
            return new_app
    
    def remove_item(self, item):
        if item is not None:
            page = item.page
            _item = page.remove_item(item)
            
            # remove the page if there is no other items on it
            if page.size == 0:
                self._pages.remove(page) 
            
            return _item
                
    def move_item(self, item, page, position=None):
        _item = item.parent.remove_item(item)            
        
        if page.size == page.capacity:
            # Move the last item on the page to a new page right after the specified page.
            last_item = page.remove_last_item()
            self._pages.add_after(page, Page(items=[last_item], capacity=self.page_capacity))

        if position is None:
            page.add_item_to_end(_item)
        else:
            page.add_item_at_index(_item, position)
        
        
                
                
class Folder(Multi_Page_Container, Item):
    def __init__(self, apps=None, page_columns=3, page_rows=3, max_pages=3, parent=None):
        super().__init__(apps, page_columns, page_rows, max_pages, parent=parent)
        
    
    
class Home(Multi_Page_Container):
    """
    Simplified data model for iOS Home Screen. Extends Multi_Page_App_Container and support folders, dock, and running apps.
    It also represents the same order of apps and folders in pages, folders, and dock as they will be presented to user in UI.
    """    
    # Override
    def __init__(
        self, 
        apps=["Phone", "Mail", "Safari", "Music", "Maps", "Clock", "Settings", "Camera", "Notes"],  
        page_columns=3, 
        page_rows=4, 
        max_pages=3,
        dock_capacity=4
    ):
        self._apps = dict()
        super().__init__(apps=apps, page_columns=page_columns, page_rows=page_rows, max_pages=max_pages)
        self._dock = Dock(capacity=dock_capacity)
        self._folders = dict()
        self._open_apps = deque()
        # self.dock_capacity = dock_capacity
        
        # By default, move the first <dock_capacity> apps to dock on initialization
        for idx in range(dock_capacity):
            self.move_app_to_dock(self._apps[apps[idx]])
     
    @property
    def dock(self):
        return self._dock.items
        
    @property
    def open_apps(self):
        return self._open_apps
    
    # Override
    def add_app(self, app_name):
        """Adds a new app to the home screen (similar to installing a new app)

        Args:
            app_name (str): name of the app to be added

        Returns:
            App: the instance of created app object
        """        
        if app_name in self._apps:
            print(f"{app_name} already exists")
            return None
        
        if self.max_apps:
            if len(self._apps) == self.max_apps:
                print(f"Max capacity reached. Cannot add {app_name}")
                return None
            
        new_app = super().add_app(app_name)
        if new_app:
            self._apps[app_name] = new_app
            
        return new_app
   
    def remove_app(self, app):
        if isinstance(app, str):
            _app = self._apps[app]
            if _app is None:
                print(f"{app} was not found.")
                return None
            
        if _app.name not in self._apps.keys:
            print(f"{_app.name} was not found.")
            return None
        
        self._apps.pop(_app.name)    
        return super().remove_item(_app)
    
    def remove_folder(self, folder):
        if isinstance(folder, str):
            _folder = self._apps[folder]
            if _folder is None:
                print(f"{folder} was not found.")
                return None
            
            if _folder.name not in self._folders.keys:
                print(f"{_folder.name} was not found.")
                return None
            
        # TODO: add all the apps in folder to them home page
        
        self._folders.pop(_folder.name)    
        return super().remove_item(_folder)
    
    
       
                   
    def open_app(self, app_name):
        app = self._apps.get(app_name, None)
        
        if app is not None:
            app.run()
            if app not in self._open_apps:
                self._open_apps.append(app)
        else:
            print(f"Could not find '{app_name}'")


    def terminate_app(self, app_name):
        if self._apps[app_name] in self._open_apps:
            self._open_apps.remove(self._apps[app_name])
    
    def delete_app(self, app):
        if isinstance(app, str):
            app = self._apps[app]
            
        # TODO: 
        # 1. terminate the app if it is running
        # 2. if app is in folder, remove the app from folder
        # 3. if the app is in dock, remove the app from dock
        
        self.remove_app(app)
 
    
    def move_item(self, item, origin, dest, position=None):
        """Move the app to the specified position in the specified page

        Args:
            item (Item): App or Folder to move
            origin (Single_Page_Container): The single page container (Page or Dock) that the item currently resides in 
            dest (Single_Page_Container): The single page container (Page or Dock) to move the item to
            position (int): index withing the single page container to place the item at
        """
        # dock to HS page
        # HS page to dock
        # HS -> HS
        # within HS
        # HS to folder
        # folder to HS
        
        if origin.container_type == "dock":
            pass
            
    def move_item_withing_page(self, item, position):
        self.move_item_from_page_to_page(item, item.parent, position=position)
        
    def move_item_from_page_to_page(self, item, page, position=None):
        _item = item.parent.remove_item(item)            
        
        if page.size == page.capacity:
            # Move the last item on the page to a new page right after the specified page.
            last_item = page.remove_last_item()
            self._pages.add_after(page, Page(items=[last_item], capacity=self.page_capacity))

        if position is None:
            page.add_item_to_end(_item)
        else:
            page.add_item_at_index(_item, position)
        
        
    def move_app_to_dock(self, new_app):
        app = new_app.parent.remove_item(new_app)
        app.parent = None
        self._dock.add_item(app)
        
    def move_item_from_dock_to_page(self, item, page, position=None):
        """Moves app from dock to a specific position in the specified page.
           If the page is full, the last app on the page will be moved to a new page right after the specified page. 
        
        Args:
            app (App): The app to remove from dock
            page (Page): The page to add the app to
            position (int): The position (or index) withing the page to place the app at. (0-based indexing)
        """
        _item = self._dock.remove_item(item)
        if page.size == page.capacity:
            # Move the last item on the page to a new page right after the specified page.
            last_item = page.remove_last_item()
            self._pages.add_after(page, Page(items=[last_item], capacity=self.page_capacity))
        
        # if no position specified, add the item as the last element 
        if position is None:
            page.add_item_to_end(_item)
        else:
            page.add_item_at_index(_item, position)
            
        
    
    def create_folder(self, folder_name, apps):
        pass
    
    def move_app_to_folder(self, app, folder, page=None, position=None):
        pass
    
    def move_app_from_folder_to_page(self, app, page, position=None):
        pass
    
    
    
    
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
                return False
        
        # if list is empty
        if self.size == 0 and self.head == None and self.tail is None:
            self.head = new_node
            self.tail = new_node
            new_node.next = None
            new_node.prev = None
            self.size +=  1
            return True
        
        new_node.prev = self.tail
        if new_node.prev is not None:
            new_node.prev.next = new_node
        self.tail = new_node
        # make sure the node is not linked to anything else
        new_node.next = None
        self.size +=  1
        return True
    
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
                return False
            
        if self.size == 0 and self.head == None and self.tail is None:
            return self.push(new_node)
            
            
        new_node.next = self.head
        if new_node.next is not None:
            new_node.next.prev = new_node
            
        self.head = new_node
        # make sure the node is not linked to anything else
        new_node.prev = None
        self.size +=  1
        return True
    
    def pop_front(self):
        if self.size == 0:
            return None
        
        return self.remove(self.head)
    
    def peak_front(self):
        return self.head
    
    def remove(self, node):
        # if there is only 1 or 0 nodes in the list 
        if self.size == 0:
            return None
        
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
    
    def find(self, name):
        curr_node = self.head
        
        while curr_node is not None:
            if curr_node.name == name:
                return curr_node
            curr_node = curr_node.next
        
        return None
    
    
    def at_index(self, index):
        """ Returns the node at index (0 based indexing)
        Args:
            index (int): the desired index for which to return the node at

        Returns:
            Node
        """
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
        """Returns the index for node in the list. None if it does not exit.

        Args:
            node (Node or str): node or node name to find the index for

        Raises:
            Exception: If node is not of type Node or str

        Returns:
            int: Index of the node in the list
        """
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
       

class Simulation:
    home = None
    def __init__(self) -> None:
        self.home = Home()
        
        self.home.add_app("app 1")
        self.home.add_app("app 2")
        self.home.add_app("app 3")
        self.home.add_app("app 4")
        self.home.add_app("app 5")
        self.home.add_app("app 6")
        self.home.add_app("app 7")
        self.home.add_app("app 8")
        self.home.add_app("app 1x")
        self.home.add_app("app 2x")
        self.home.add_app("app 3x")
        self.home.add_app("app 4x")
        self.home.add_app("app 5x")
        self.home.add_app("app 6x")
        self.home.add_app("app 7x")
        self.home.add_app("app 8x")
        self.home.add_app("app 1y")
        self.home.add_app("app 2y")
        self.home.add_app("app 3y")
        self.home.add_app("app 4ysdfsdfsdfsdfsdfsdf")
        self.home.add_app("app 5y")
        self.home.add_app("app 6y")
        self.home.add_app("app 7y")
        self.home.add_app("app 8y")
        self.home.add_app("app 9y")
        self.home.add_app("app 10y")
        self.home.add_app("app 11y")
        self.home.add_app("app 12y")
        self.home.add_app("app 13y")
        self.home.add_app("app 14y")
        self.home.add_app("app 15y")
        self.home.add_app("app 16y")
        
        
    def run(self):
        self.render_home_screen()
        # while(True):
        #     cmd = input("Enter a command (type in help to see the available options): \n")
                    
        #     if cmd.strip().lower() == "q" or cmd == "quit":
        #         print("Quitting...")
        #         break
            
        #     # parse_input(cmd)
        #     self.render_home_screen()
        

    def parse_input(self, cmd):
        cmd = cmd.strip()
        
        if cmd.lower() == "help":
            self.display_help()
            
            
    
    def render_home_screen(self):
        rows = self.home.page_rows
        cols = self.home.page_columns
        number_of_pages = self.home.pages.size
        
        grid = [[None for c in range(rows)] for r in range(number_of_pages * cols)]
        
        page_counter = 0
        for page in self.home.pages:
            idx = 0
            for curr_item in page.items:
                # col
                i = idx % 3 + (page_counter * cols)
                
                # row
                j = idx // 3
                
                grid[i][j] = curr_item.name
                
                idx += 1
            page_counter += 1
                
                
        ITEM_MAX_LEN = 12
        
        print("")
        page_counter = 0
        for page in self.home.pages:
            page_title = f"Page # {str(page_counter + 1)}"
            page_title = page_title.ljust((ITEM_MAX_LEN * cols) + 4)
            print(page_title, end="")
            page_counter += 1
            
        print("")
        line = "-".ljust(((ITEM_MAX_LEN * cols) + 4)*number_of_pages - 3, '-')
        print(line)
        
        for idx_j in range(rows):
            for idx_i in range(cols * number_of_pages):
                name = grid[idx_i][idx_j]
                if name is None:
                    name = " ".ljust(ITEM_MAX_LEN)
                else:  
                    if len(name) >= ITEM_MAX_LEN:
                        name = name[:ITEM_MAX_LEN - 3]
                    name = name.ljust(ITEM_MAX_LEN)
                    
                    
                print(name, end="")
                
                if idx_i % cols == (cols - 1):
                    print("|   ", end="")
                
            print("\n")
        print(line)
        
        # print dock
        double_line = "=".ljust(((ITEM_MAX_LEN * cols) + 4)*number_of_pages - 3, '=')
        print(double_line)
        print("DOCK:  ", end="")
        for item in self.home.dock:
            print(item.name, end="   ")
        print("")
        print(double_line)
        
                
                    
            

            
        
            
            
            

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
        print(traceback.format_exc())
        
    
    
    
    