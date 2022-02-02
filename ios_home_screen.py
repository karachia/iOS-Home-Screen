"""
    A simplified data model of iOS Home Screen
    
    General Design:
    This design utilizes a Doubly Linked List (implemented in this file as well) for holding apps and folders within pages or dock, as well as pages within the Home Screen.
    Using doubly linked list allows storing the home screen data (apps, folders) in the same order as they will be presented to the user in the UI in pages, dock, and folders.
    It also enables moving the apps and folders around easily without any extra cleaning and re-ordering, or shifting items back and forth as one would do in an array list. 
    
    Pages are also stored in the doubly linked list to support adding and deleting pages in the middle of the list optimally, and to keep the same order as the pages are represented to the user in the UI.
    
    Assumptions:
    - App names are unique and are used as app ID's (or bundle ID's)
    - Folder names are also unique
"""

from collections import deque
from pydoc import render_doc
import traceback
import uuid
from abc import ABC, abstractmethod

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
    def __init__(self, name, parent=None, can_delete=True):
        """Constructor for App

        Args:
            name (str): name of the App. It also acts as app's unique ID / bundle ID
            parent (Single_Page_Container, optional): The page/container in which the app resides). Defaults to None.
        """
        super().__init__(name, parent=parent)
        
        self.can_delete= can_delete
                
    def run(self):
        print("\n----------------------\n.\n.\n.\n")
        print(f"{self.name} is running...")
        print(".\n.\n.\n----------------------\n")
        
    
# Abstract method
class Container(ABC):
    def __init__(self, container_type) -> None:
        super().__init__()
        self._container_type = container_type
        
    @property
    def container_type(self):
        return self._container_type

    # Protected methods:
    @abstractmethod
    def _add_item(self, item):
        pass
    
    @abstractmethod
    def _remove_item(self, item):
        pass
    
    @abstractmethod
    def _move_item(self, item, position):
        pass
    

class Single_Page_Container(Container):
    """A container class for Items"""
    
    def __init__(self, items, capacity, parent_container=None, container_type=None):
        """Constructor

        Args:
            name (str): Name of the container
            items ([Items]): List of Items to hold
            capacity (int): Maximum capacity of the items the container can hold
        """
        super().__init__(container_type="single_page_container" if container_type is None else container_type)
        self._items = DoublyLinkedList(capacity=capacity)
        self.parent_container = parent_container
        
        if items:
            for item in items:
                self._add_item(item)
        
        
    @property
    def size(self):
        return self._items.size
    
    @property
    def capacity(self):
        return self._items.capacity
            
    @property
    def items(self):
        return self._items
    
    def _remove_item(self, item):
        item = self._items.remove(item)
        item.parent = None
        return item
    
    def _add_item(self, item):
        item.parent = self
        self._items.push(item)
        
    def _move_item(self, item, position=None):
        _item = self._items.remove(item)
        if position is None:
            self._items.push(_item)
        else:
            self._items.add_at_index(position, _item)
    
    def add_item(self, item, position=None):
        if position is None:
            self._add_item(item)
        else:
            self.add_item_at_index(item, position)
        
    def add_item_at_index(self, item, index):
        item.parent = self
        self._items.add_at_index(index, item)
        
    def add_item_to_end(self, item):
        item.parent = self
        self._items.push(item)
    
    def remove_item(self, item):
        return self._remove_item(item)
    
    def remove_last_item(self):
        app = self._items.pop()
        app.parent = None
        return app
    
    def move_item(self, item, position=None):
        self._move_item(item, position=position)
     
     
class Multi_Page_Container(Container):
    """A container class for Apps that supports organizing apps across multiple Pages"""
      
    def __init__(
        self, 
        page_columns=3, 
        page_rows=4, 
        max_pages=4,
        container_type = None,
        
    ):
        super().__init__(container_type="multi_page_container" if container_type is None else container_type)
        
        self.page_columns = page_columns 
        self.page_rows = page_rows
        self.page_capacity = page_rows * page_columns
        self.max_pages = max_pages 
        
        self._pages = DoublyLinkedList(capacity=self.max_pages)
        
        if max_pages:
            self.max_apps = int(self.page_capacity * max_pages) 
        else:
            self.max_apps = None
            
            
    @property
    def pages(self):
        return self._pages
    
    def get_paget_at_index(self, idx):
        return self._pages.at_index(idx)
    
    def _add_item(self, item, page=None, position_within_page=None):                        
        if page is None:
            position_within_page = None
            # then push to the last page or create one if one does not exit
            # if there are no pages yet or the last page has reached capacity of apps and folders within it
            if self._pages.tail is None or self._pages.tail.size == self.page_capacity:
                # try creating a new page and adding the app to it, only if the max number of pages has not been reached yet 
                if self.max_pages is None or self._pages.size < self.max_pages:
                    self._pages.push(Page(items=[item], capacity=self.page_capacity, parent_container=self))
                    return item
                
                # Otherwise go from the last page to the first page and see if there is an opening to add the app to    
                else: 
                    curr_page = self._pages.tail.prev # start the search from the page to the last 
                    
                    while curr_page is not None:
                        if curr_page.size() < curr_page.capacity:
                            curr_page.add_item(item)
                            return item
                        
                        curr_page = curr_page.prev  
                    
                    # If no open position is found for this new app, return non
                    print(f"Error: Failed to add the new app '{item.name}'. Could not find an open position in any of the pages. ")
                    return None 
            else:
                # add to the last page
                page = self._pages.tail
                page.add_item(item)
        else:
            self.add_item_at_page(item, page, position_within_page=position_within_page)
                            
                
    def add_item_at_page(self, item, page, position_within_page=None):
        if page.parent_container != self:
                print("Invalid request. The page does not belong to this container")
                return
            
        if page.size == page.capacity and (self.max_pages is None or self.pages.size < self.max_pages):
            # Move the last item on the page to a new page right after the specified page.            
            last_item = page.remove_last_item()
            self._pages.add_after(page, Page(items=[last_item], capacity=self.page_capacity, parent_container=self))

        page.add_item(item, position=position_within_page)
        
    def remove_page(self, page):
        if page.parent_container != self:
            return 
        
        if page.size > 0:
            return None
        page = self._pages.remove(page)
                
    
    def _remove_item(self, item):
        items_origianl_parent = item.parent
        try:
            if item is not None:
                page = item.parent
                item = page.remove_item(item)
                
                # remove the page if there is no other items on it
                if page.size == 0:
                    self._pages.remove(page) 
                
                return item
            return None
        finally: # if page is empty after remove, remove the page
            # if items_origianl_parent:
            #     if items_origianl_parent.size == 0:
            #         if items_origianl_parent.parent_container is not None:
            #             items_origianl_parent.parent_container.remove_page(items_origianl_parent)
            pass
            
                
    def _move_item(self, item, page, position=None):
        if item.parent.parent_container != self or page.parent_container != self:
            print(f"Invalid request. '{item.name} and/or the specified page do not belong to the same container")
            return 
            
        # Then the move is contained within the same page. No need to worry about page being full.
        if item.parent.id == page.id:
            page.move_item(item, position=position)
            
        else:
            _item = item.parent.remove_item(item)            
            
            # if the specified page is full see if we can open up room by pushing the last item to a new page right after
            if page.size == page.capacity:
                # Move the last item on the page to a new page right after the specified page.
                if self._pages.size == self.max_pages:
                    print(f"The specified page is full and the folder has reach its max capacity for pages. Cannot move {_item.name}")
                    return 
                
                last_item = page.remove_last_item()
                self._pages.add_after(page, Page(items=[last_item], capacity=self.page_capacity, parent_container=self))

            if position is None:
                page.add_item_to_end(_item)
            else:
                page.add_item_at_index(_item, position)
                

    def get_page_at_index(self, page_idx):
        return self._pages.at_index(page_idx)
    
        
class Dock(Single_Page_Container):
    """Represents the iOS Dock. It extends Single_Page_Container class and its name property is set to 'Dock'"""
    def __init__(self, capacity, parent_container=None):
        super().__init__(container_type="dock", items=None, capacity=capacity, parent_container=parent_container)
        
        
class Page(Node, Single_Page_Container):   
    def __init__(self, items, capacity, parent_container=None):
        self.id = str(uuid.uuid4())
        Node.__init__(self, name=f"page_{self.id}")
        Single_Page_Container.__init__(self, items=items, capacity=capacity, parent_container=parent_container, container_type="page",) 
         
                
class Folder(Item, Multi_Page_Container):
    def __init__(self, name, apps, page_columns=3, page_rows=3, max_pages=3, parent=None):
        Item.__init__(self, name=name, parent=parent)
        Multi_Page_Container.__init__(self, page_columns, page_rows, max_pages, container_type="folder")
        if apps:
            for app in apps:
                self.add_item(app)
            
        
    def add_item(self, item, page=None, position_within_page=None):
        self._add_item(item, page=page, position_within_page=position_within_page)
        
    def remove_item(self, item):
        self._remove_item(item)
        
    def move_item(self, item, page_idx, position=None):
        if item.parent.parent_container != self:
            print(f"{item.name} does is not in the current folder")
            return
        items_origianl_parent = item.parent
        try:
            if page_idx < self._pages.size and page_idx >= 0:
                page = self.get_page_at_index(page_idx)
                
                
            elif page_idx == self._pages.size:
                item = item.parent.remove_item(item)
                page = Page(items=[item], capacity=self.page_capacity, parent_container=self)
                self._pages.push(page)
                return 
            
            else:
                print("Invalid Index")
                return

            
            self._move_item(item, page, position=position)
        finally:
            if items_origianl_parent:
                if items_origianl_parent.size == 0:
                    if items_origianl_parent.parent_container is not None:
                        items_origianl_parent.parent_container.remove_page(items_origianl_parent)
            
    
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
        max_pages=5,
        dock_capacity=4
    ):
        self._apps = dict()
       
        super().__init__(page_columns=page_columns, page_rows=page_rows, max_pages=max_pages, container_type="home")
        
        self._dock = Dock(capacity=dock_capacity, parent_container=self)
        self._folders = dict()
        self._open_apps = deque()
        
        for app in apps:
            self.add_app(app) # add_app() abstracts adding an app into the correct page
            
        a = self._apps
        
        # By default, move the first <dock_capacity> apps to dock on initialization
        for idx in range(dock_capacity):
            self.move_item_to_dock(self._apps[apps[idx]])
            
        for app in ["Phone", "Settings", "Clock", "Camera"]:
            if app in self._apps.keys():
                self._apps[app].can_delete = False
     
    @property
    def dock_items(self):
        return self._dock.items
        
    @property
    def running_apps(self):
        return self._open_apps
    
    def get_app(self, app_name):
        if app_name in self._apps:
            return self._apps[app_name]
        
        print(f"App: {app_name} was not found")
        return None
        
    
    def get_folder(self, folder_name):
        if folder_name in self._folders:
            return self._folders[folder_name]
        
        print(f"Folder: {folder_name} was not found")
        return None
    
    
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
        
        if app_name in self._folders:
            print(f"A folder with the name {app_name} already exists. Try a different app")
            return None
        
        if self.max_apps:
            if len(self._apps) == self.max_apps:
                print(f"Max capacity reached. Cannot add {app_name}")
                return None
        
        new_app = App(app_name)
        self._apps[app_name] = new_app
        
        self._add_item(new_app)
   
    def __verify_app(self, app):
        if isinstance(app, str):
            return self.get_app(app)
           
        
        elif isinstance(app, App):
            if app.name not in self._apps.keys:
                print(f"{app.name} was not found.")
                return None
            return app
        print("Invalid request. 'app' must be either App or str")
        return None
       

    def __find_item(self, item_name):
        """finds the desired item object corresponding to item_name

        Args:
            item_name (str): name of the app or folder to be found

        Returns:
            Item: App or Folder 
        """
        if item_name in self._apps:
            return self._apps[item_name]
        
        if item_name in self._folders:
            return self._folders[item_name]
        
        print(f"{item_name} was not found")
        
        return None
    
        
    
    def _move_item(self, item, dest, page_idx=None, position_within_page=None):
        if isinstance(item, str): 
            item = self.__find_item(item)
        
        items_origianl_parent = item.parent
        
        try:
            # if the item is moving in the same page 
            if items_origianl_parent == dest:
                dest.move_item(item, position=position_within_page)
                return 
            
            item = items_origianl_parent.remove_item(item)
                        
            if dest.container_type == "folder":
                if dest.pages.size > 0:
                    page = None
                    if page_idx is not None: 
                        page=dest.get_paget_at_index(page_idx)
                    dest.add_item(item, page=page, position_within_page=position_within_page)
                else:
                    dest.add_item(item)
                return
                
            
            container = dest.parent_container
            if container.container_type == "home":
                if dest.container_type == "dock":
                    self._dock.add_item(item, position_within_page)
                else: # if it is a page
                    self._add_item(item, page=dest, position_within_page=position_within_page)
                    
            elif container.container_type == "folder": 
                if page_idx:
                    page = container.get_page_at_index(page_idx)
                    container.add_item_at_page(item, page, position_within_page=position_within_page)
                
                else:
                    container.add_item(item, position_within_page=position_within_page)
        finally: # if the item's original page is empty after move, remove the page
            if items_origianl_parent:
                if items_origianl_parent.size == 0:
                    if items_origianl_parent.parent_container is not None:
                        items_origianl_parent.parent_container.remove_page(items_origianl_parent)
            
    
    def delete_app(self, app):
        if isinstance(app, str):
            app = self.get_app(app)
            
        if not app.can_delete:
            print(f"{app.name} app is not allowed to be deleted and must stay on iPhone")
            return 
    
        # terminate the app if it is running
        self.terminate_app(app.name)
        
        # if app is in folder, remove the app from folder
        if app.parent.parent_container.container_type == "folder":
            app.parent.parent_container.remove_item(app)
            
        else: # app is not in a folder 
            # if the app is in dock, remove the app from dock
            if app.parent.container_type == "dock":
                self._dock.remove_item(app)
                
            else: # app is in the home screen
                app = self._remove_item(app)

        self._apps.pop(app.name)
    
        
    def run_app(self, app_name):
        app = self._apps.get(app_name, None)
        
        if app is not None:
            app.run()
            if app not in self._open_apps:
                self._open_apps.append(app)
                return True
        else:
            print(f"Could not find '{app_name}'")
            return False

    def terminate_app(self, app_name):
        if self._apps[app_name] in self._open_apps:
            self._open_apps.remove(self._apps[app_name])
            
    def create_folder(self, folder_name, apps, page=None, position_within_page=None):
        if folder_name in self._apps.keys() or folder_name in self._folders.keys():
            print(f"Cannot create a folder with name {folder_name}. Name already exists.")
            return None
        
        _apps = []
        for app in apps:
            if isinstance(app, str):
                _app = self.get_app(app)
                if _app:
                    _apps.append(_app)
                else:
                    print(f"Invalid app {app}. Operation Failed.")
                    return None
            elif isinstance(app, App): 
                _app = self.__verify_app(app)               
                _apps.append(_app)
            else:
                print(f"Invalid request. Operation Failed.")
                return None
                
        new_folder = Folder(folder_name, apps=None, parent=page)
        
        if page:
            page.add_item(new_folder, position_within_page)
        else: 
            self._add_item(new_folder, position_within_page=position_within_page)
        
        for application in _apps:
            self._move_item(application, new_folder)
            
        self._folders[folder_name] = new_folder
        return new_folder
    
    def remove_folder(self, folder):
        if isinstance(folder, str):
            folder = self.get_folder(folder)
            
            
        if folder.pages.size > 0:
            print("Cannot remove a folder that contains app(s).")
            return None
        
        self._folders.pop(folder.name)    
        return self._remove_item(folder)
            
        
    def move_item_between_pages(self, item, page_idx, position=None):
        if isinstance(item, str): 
            item = self.__find_item(item)
        
        if page_idx < self._pages.size and page_idx >= 0:
            page = self.get_page_at_index(page_idx)
            
        elif page_idx == self._pages.size:
            item = item.parent.remove_item(item)
            page = Page(items=[item], capacity=self.page_capacity, parent_container=self)
            self._pages.push(page)
            return 
        
        else:
            print("Invalid Index")
            return
        
        self._move_item(item, page, position_within_page=position)
    
    def move_item_to_dock(self, item, position=None):
        if isinstance(item, str): 
            item = self.__find_item(item)
        if self._dock.size == self._dock.capacity:
            print(f"Dock is full (Capacity: {self._dock.capacity}). Cannot add any more items.")
            return 
        item = item.parent.remove_item(item)
        self._dock.add_item(item, position)
        
        
    def move_item_to_folder(self, app, folder, page_idx=None, position=None):
        if isinstance(app, str): 
            _app = self.get_app(app)
        if _app is None:
            return 
        
        if isinstance(folder, str): 
            _folder = self.get_folder(folder)
        if _folder is None:
            return 
        
        self._move_item(_app, _folder, page_idx=page_idx, position_within_page=position)
        

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
    curr_container = None
    app_is_open = False
    folder_is_open = False
    debug = False
    
    def __init__(self) -> None:
        self.home = Home()
        self.curr_container = self.home
        self.ITEM_MAX_LEN = 12
        
    def run(self):
        self.render_home_screen()
        while(True):
            if self.app_is_open or self.folder_is_open: 
                print("Type 'close' to close the open app/folder and see the Home Screen")
            cmd = input("\n\nEnter a command (type in 'help' to see the available options): \n")
                    
            if cmd.strip().lower() == "q" or cmd == "quit":
                print("Quitting...")
                break
            try: 
                if self.parse_input(cmd):
                    self.render_home_screen()
            except Exception as err:
                if self.debug:
                    print("\n\nFor Debugging:")
                    print(traceback.format_exc())
                    print(f"Exception occurred: {str(err)}")
                print("\n\nInvalid request. Try again...")

    def parse_input(self, cmd):
        cmd = cmd.strip()
        
        if cmd.lower() == "help":
            self.display_help()
            return False
        
        keywords = cmd.split()
        
        if keywords[0].lower() == "debug":
            if keywords[0].lower() == "on":
                self.debug = True
            elif keywords[0].lower() == "off":
                self.debug = False
            print(f"set debug to {self.debug}")
            return False
        
        if keywords[0].lower() == "add":
            if len(keywords) < 2:
                print("Missing app name")
                return False
            
            app_name = keywords[1]
            self.home.add_app(app_name)
            return True
        
        if keywords[0].lower() == "delete":
            if len(keywords) < 2:
                print("Missing app name")
                return False
            app_name = keywords[1]
            self.home.delete_app(app_name)
            return True
        
        if keywords[0].lower() == "remove":
            if len(keywords) < 2:
                print("Missing app name")
                return False
            folder_name = keywords[1]
            self.home.remove_folder(folder_name)
            return True
        
        if keywords[0].lower() == "run":
            if len(keywords) < 2:
                print("Missing app name")
                return False
            app_name = keywords[1]
            if self.home.run_app(app_name):
                self.app_is_open = True
                self.render_dock()
                return False
            return True
        
        if keywords[0].lower() == "close":
            if self.app_is_open:
                self.app_is_open = False
                return True
            elif self.folder_is_open:
                self.folder_is_open = False
                self.curr_container = self.home
                return True
            return False
        
        if keywords[0].lower() == "quit":
            if len(keywords) < 2:
                print("Missing app name")
                return False
            
            app_name = keywords[1]
            self.home.terminate_app(app_name)
            return True
        
        if keywords[0].lower() == "running":
            apps = self.home.running_apps
            print("Apps running in the background:")
            print("-------------------------------")
            for app in apps:
                print("-", app.name)
            print("-------------------------------")
            return False
        
        if keywords[0].lower() == "make":
            if len(keywords) < 3:
                print("Missing folder name and/or app(s)")
                return False
            
            folder_name = keywords[1]
            
            apps = []
            
            for i in range(2, len(keywords)):
                apps.append(keywords[i])
                
            if self.home.create_folder(folder_name, apps=apps):
                return True
            return False
        
        if keywords[0].lower() == "open":
            if len(keywords) < 2:
                print("Missing folder name")
                return False
            folder_name = keywords[1]
            folder = self.home.get_folder(folder_name)
            if folder:
                self.curr_container = folder
                self.folder_is_open = True
                return True
        
        if keywords[0].lower() == "move":
            if len(keywords) < 3:
                print("Missing destination")
                return False
            
            app_name = keywords[1]
            dest_type = keywords[2]
            
            if dest_type == "dock":
                position = None
                if len(keywords) >= 4:
                    position = int(keywords[3]) - 1
            
                self.curr_container.move_item_to_dock(app_name, position=position)
                return True
            
            if dest_type == "page":
                page_number = int(keywords[3]) - 1
                position = None
                if len(keywords) >= 5:
                    position = int(keywords[4]) - 1
                if self.folder_is_open:
                    app = self.home.get_app(app_name)
                    self.curr_container.move_item(app, page_number, position=position)
                else:
                    self.home.move_item_between_pages(app_name, page_number, position=position)
                return True
            
            if dest_type == "folder":
                if len(keywords) < 4:
                    print("Missing destination")
                    return False
                
                folder_name = keywords[3]
                
                page_idx = None
                if len(keywords) >= 6:
                    page_idx = int(keywords[5]) - 1
                
                position = None
                if len(keywords) >= 8:
                    position = int(keywords[7]) - 1
                    
                self.home.move_item_to_folder(app_name, folder_name, page_idx=page_idx, position=position)
                return True
            
            return False

    def display_help(self):
        help = """
        Action:                     Command:
        -----------------------------------------------------------------------
        Add App:                    add <app name>
        Delete App:                 delete <app name>
        Run App:                    run <app name>
        Open Folder:                open <folder name>
        Close the current app:      close 
        Close the current folder:   close 
        Terminate App:              quit <app name>
        Show all running Apps:      running      
        
        Create a folder             make <folder name> <app1 name> [<app2 name> <app2 name> etc]
        Remove folder               remove <folder name>
        
        Move App/Folder:
            - to dock               move <app/folder name> dock [position_within_dock]
            - to another page:      move <app/folder name> [page <page number> [position_within page]]
            - to new page:          move <app/folder name> newpage
        
        Move app to Folder:         move <app name> folder <folder name> [page <page #>  [position <index within page>]]
            
        
        """        
        print(help)
            
    def render_home_screen(self):
        rows = self.curr_container.page_rows
        cols = self.curr_container.page_columns
        number_of_pages = self.curr_container.pages.size
        
        grid = [[None for c in range(rows)] for r in range(number_of_pages * cols)]
        
        page_counter = 0
        for page in self.curr_container.pages:
            idx = 0
            for curr_item in page.items:
                # col
                i = idx % 3 + (page_counter * cols)
                
                # row
                j = idx // 3
                
                grid[i][j] = curr_item.name
                
                idx += 1
            page_counter += 1
        
        print("")
        if self.folder_is_open:
            print(f"Folder: {self.curr_container.name}")
        else:
            print("Home Screen")
        page_counter = 0
        for page in self.curr_container.pages:
            page_title = f"Page # {str(page_counter + 1)}"
            page_title = page_title.ljust((self.ITEM_MAX_LEN * cols) + 4)
            print(page_title, end="")
            page_counter += 1
            
        print("")
        line = "-".ljust(((self.ITEM_MAX_LEN * cols) + 4)*number_of_pages - 3, '-')
        print(line)
        
        for idx_j in range(rows):
            for idx_i in range(cols * number_of_pages):
                name = grid[idx_i][idx_j]
                if name is None:
                    name = " ".ljust(self.ITEM_MAX_LEN)
                else:  
                    if len(name) >= self.ITEM_MAX_LEN:
                        name = name[:self.ITEM_MAX_LEN - 3]
                    name = name.ljust(self.ITEM_MAX_LEN)
                    
                    
                print(name, end="")
                
                if idx_i % cols == (cols - 1):
                    print("|   ", end="")
                
            print("\n")
        print(line)
        
        # print dock
        if self.folder_is_open is False:
            self.render_dock()        
                
    def render_dock(self):
        rows = self.home.page_rows
        cols = self.home.page_columns
        number_of_pages = self.home.pages.size
        double_line = "=".ljust(((self.ITEM_MAX_LEN * cols) + 4) * number_of_pages - 3, '=')
        print(double_line)
        print("DOCK:  ", end="")
        for item in self.home.dock_items:
            print(item.name, end="   ")
        print("")
        print(double_line)
            

if __name__ == "__main__":
    try:
        simulation = Simulation()
        simulation.run()
    except Exception as err:
        print(traceback.format_exc())
        print(f"Exception occurred: {str(err)}")
        
    
    
    
    