"""
    A simplified model of iOS Home Screen
    
    Assumptions:
    - App names are unique and are used as App ID's (or bundle ID's)
    - Folder names are also unique
    - An app and a folder cannot have the same name
    - Names are case insensitive 
"""
class Node:
    next = None
    prev = None
    name = ""
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name


    
class DoublyLinkedList:
    def __init__(self, nodes=None):
        self.head = None
        self.tail = self.head
        
        if nodes is not None:
            curr_node = Node(name=nodes.pop(0))
            
            self.head = curr_node
            self.tail = curr_node
            
            for elem in nodes:
                curr_node.next = Node(name=elem)
                curr_node.next.prev = curr_node
                curr_node = curr_node.next
                
    def __repr__(self):
        curr_node = self.head
        nodesLTR = []

        while curr_node is not None:
            nodesLTR.append(curr_node.name)
            curr_node = curr_node.next
        nodesLTR.append("None")
        
        curr_node = self.tail
        nodesRTL = []

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


class Home:
    items = dict() # dict[str, item] contains all the apps and folders
    dock = None
    pages = None # 
    
    def __init__(self, page_columns=3, page_rows=4, max_pages=5, dock_capacity=4) -> None:
        self.page_columns = page_columns 
        self.page_rows = page_rows
        self.max_pages = max_pages 
        self.dock_capacity = dock_capacity
        
        self.page = Page()
        
        self.add_app("Phone")
        self.add_app("Music")
        self.add_app("Maps")
        self.add_app("Mail")
        self.add_app("Safari")
        self.add_app("Clock")
        self.add_app("Settings")
        self.add_app("Camera")
        self.add_app("Notes")
        
        # Move a few of the apps to dock
        self.move_app_to_dock("Phone")
        self.move_app_to_dock("Mail")
        self.move_app_to_dock("Safari")
        
        self.dock = Dock()
        pass
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
        
    
    
    
    