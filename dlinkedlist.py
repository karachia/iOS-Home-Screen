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
        self.size = 0
        
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
    
