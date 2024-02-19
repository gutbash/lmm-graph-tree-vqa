"""
The tree module contains classes and methods for random binary trees and binary search trees.
"""
import networkx as nx
import matplotlib.pyplot as plt
import random
from pathlib import Path
from typing import Optional, Literal, Any

Color = Literal['#88d7fe', '#feaf88', '#eeeeee']
Shape = Literal['o', 's', 'd']
Font = Literal['sans-serif', 'serif', 'monospace']
Thickness = Literal['0.5', '1.0', '1.5']

Traversal = Literal['preorder', 'inorder', 'postorder']

class Tree:
        
    def pre_order(self) -> list:
        
        def _pre_order(node: 'Tree.TreeNode') -> list:
            if node is None:
                return []
            return [node.value] + _pre_order(node.left) + _pre_order(node.right)
        
        return _pre_order(self.root)
    
    def in_order(self) -> list:
        
        def _in_order(node: 'Tree.TreeNode') -> list:
            if node is None:
                return []
            return _in_order(node.left) + [node.value] + _in_order(node.right)
        
        return _in_order(self.root)
    
    def post_order(self) -> list:
        
        def _post_order(node: 'Tree.TreeNode') -> list:
            if node is None:
                return []
            return _post_order(node.left) + _post_order(node.right) + [node.value]
        
        return _post_order(self.root)
    
    class TreeNode:
        """
        A class used to represent a tree node

        Attributes
        ----------
        value : int
            the value of the node
        left : Tree.TreeNode
            the left child of the node
        right : Tree.TreeNode
            the right child of the node
            
        Methods
        -------
        __init__(value: int)
            Constructs all the necessary attributes for the Tree.TreeNode object
        """
        
        value: Optional[int]
        left: Optional['Tree.TreeNode']
        right: Optional['Tree.TreeNode']
        
        def __init__(self, value: Optional[int] = None):
            """
            Parameters
            ----------
            value : int
                the value of the node (default is None)
            """
            self.value = value  # Node value
            self.left = None  # Left child
            self.right = None  # Right child

# Generate a random binary tree
class BinaryTree(Tree):
    """
    A class used to represent a binary tree

    Attributes
    ----------
    large : bool
        whether to generate a large tree or not
    root : TreeNode
        the root of the binary tree
    pos : dict
        a dictionary of positions of nodes
    skeleton : nx.Graph
        the skeleton of the tree
    filled : nx.Graph
        the filled tree
    default_file_name : str
        the default file name for the image
    yaml_structure_type : str
        the structure type for the YAML file
    formal_name : str
        the formal name of the structure

    Methods
    -------
    __init__(large: bool = False)
        Constructs all the necessary attributes for the BinaryTree object
    generate()
        Generates a random binary tree
    fill()
        Fills the graph nodes with the given values
    draw(save: bool = False, path: Path = None, show: bool = True)
        Draws the binary tree
    """
    large: bool = False
    root: Optional['Tree.TreeNode'] = None
    pos: dict = {}
    skeleton: Optional[nx.Graph] = nx.Graph()
    filled: Optional[nx.Graph] = nx.Graph()
    
    default_file_name: str = 'bt_test.png'
    yaml_structure_type: str = 'binary_tree'
    formal_name: str = 'Binary Tree'
    
    def __init__(self, large: bool = False) -> None:
        """
        Constructor for the BinaryTree class
        
        Parameters
        ----------
        large : bool
            whether to generate a large tree with 11-20 nodes instead of 1-10 nodes or not (default is False)
        """
        self.large = large
        self.root = None
        self.pos = {}
        self.skeleton = nx.Graph()
        self.filled = nx.Graph()

    def generate(self) -> None:
        """
        Generates a random binary tree
        
        Paramters
        ---------
        None
        
        Returns
        -------
        None
        
        Raises
        ------
        None
        
        Notes
        -----
        The number of nodes in the tree is randomly chosen between 1 and 10 for small trees and between 11 and 20 for large trees.
        
        The tree is not necessarily balanced.
        
        The tree is not necessarily complete.
        
        The tree is not necessarily full.
        """

        if self.large:
            num_nodes = random.randint(11, 20)
        else:
            num_nodes = random.randint(3, 10)

        if num_nodes <= 0:
            return None

        root_value = random.randint(1, 99)
        root = Tree.TreeNode(root_value)
        values_set = {root_value}
        nodes = [root]
        queue = [root]

        # Ensure root has two children
        for _ in range(2):
            child_value = random.randint(1, 99)
            while child_value in values_set:
                child_value = random.randint(1, 99)

            child_node = Tree.TreeNode(child_value)
            if queue[0].left is None:
                queue[0].left = child_node
            else:
                queue[0].right = child_node
            values_set.add(child_value)
            nodes.append(child_node)
            queue.append(child_node)

        # Continue with random tree generation
        while len(nodes) < num_nodes:
            current = queue.pop(0)

            if len(nodes) < num_nodes and current.left is None:
                left_child_value = random.randint(1, 99)
                while left_child_value in values_set:
                    left_child_value = random.randint(1, 99)

                left_child = Tree.TreeNode(left_child_value)
                current.left = left_child
                values_set.add(left_child_value)
                nodes.append(left_child)
                queue.append(left_child)

            if len(nodes) < num_nodes and current.right is None:
                right_child_value = random.randint(1, 99)
                while right_child_value in values_set:
                    right_child_value = random.randint(1, 99)

                right_child = Tree.TreeNode(right_child_value)
                current.right = right_child
                values_set.add(right_child_value)
                nodes.append(right_child)
                queue.append(right_child)

        self.root = root

        def graphize(T: nx.Graph, node: Tree.TreeNode, x: int = 0, y: int = 0, layer_height: Optional[int] = None, layer_width: Optional[int] = None) -> None:
            """
            Graphizes the binary tree

            Parameters
            ----------
            T : nx.Graph
                the graph to be drawn
            node : Tree.TreeNode
                the current node
            x : int
                the x coordinate of the current node (default is 0)
            y : int
                the y coordinate of the current node (default is 0)
            layer_height : Optional[int]
                the height of the current layer (default is None)
            layer_width : Optional[int]
                the width of the current layer (default is None)

            Returns
            -------
            None
            
            Raises
            ------
            ValueError
                if the node is None
            """
            
            if node:
                if layer_height is None:
                    layer_height = random.randint(3, 6)  # Random height for each layer
                if layer_width is None:
                    layer_width = 2

                current_pos = (x, y)
                self.pos[node.value] = current_pos

                if node.left:
                    T.add_edge(node.value, node.left.value)
                    graphize(T, node.left, x - layer_height, y - 1, layer_height / 2, layer_width / 2)
                if node.right:
                    T.add_edge(node.value, node.right.value)
                    graphize(T, node.right, x + layer_height, y - 1, layer_height / 2, layer_width / 2)
                else:
                    T.add_node(node.value)
            else:
                raise ValueError("The node is None")
            self.skeleton = T
            
        graphize(self.skeleton, self.root)

    def fill(self) -> None:
        """
        Fills the graph nodes with the given values

        Parameters
        ----------
        None

        Returns
        -------
        None
        
        Raises
        ------
        None
        
        Notes
        -----
        The value of each node is randomly chosen between 1 and 99.
        
        The left child of each node is randomly chosen between 1 and 99.
        
        The right child of each node is randomly chosen between 1 and 99.
        """
        
        self.filled = self.skeleton.copy()

        values = [random.randrange(1, 99, 1) for _ in range(len(self.filled))]
        #print("These are new node values:",values)
        for i, node in enumerate(self.filled.nodes):
            self.filled.nodes[node]['value'] = values[i]

    def draw(self, save: bool = False, path: Optional[Path] = None, show: bool = True, shape: Shape = 'o', color: Color = '#88d7fe', font: Font = 'sans-serif', thickness: Thickness = '1.0') -> None:
        """
        Draws the binary tree using matplotlib and networkx

        Parameters
        ----------
        save : bool
            whether to save the image or not (default is False)
        path : Optional[Path]
            the path to save the image (default is None)
        show : bool
            whether to show the image or not (default is True)
        shape : Shape
            the shape of the nodes (default is 'o')
        color : Color
            the color of the nodes (default is '#88d7fe' aka sky blue)
        font : Font
            the font of the labels (default is 'sans-serif')
        thickness : Thickness
            the thickness of the edges (default is '1.0')
            
        Returns
        -------
        None

        Raises
        ------
        ValueError
            if the root is None
            
        Notes
        -----
        The visualization is done using the networkx and matplotlib libraries.
        
        The nodes are labeled with their values.
        
        The graph is drawn using the spring layout.
        
        The image is not displayed if the show parameter is set to False.
        
        The image is not saved if the save parameter is set to False.
        
        The image is saved in the current directory if the path parameter is set to None.
        
        The image is saved with the default name if the path parameter is set to None.
        """
        
        if self.root is None:
            raise ValueError("The root is None")

        # DPI for the output
        dpi = 100

        # Calculate the figure size in inches for a 512x512 pixel image
        figure_size = 512 / dpi  # 5.12 when dpi is 100

        # Create a figure with the calculated size
        plt.figure(figsize=(figure_size, figure_size))
        #print(self.pos)

        # Draw nodes and edges
        nx.draw(self.filled, self.pos, with_labels=True, font_weight='bold', node_size=400, node_color=color, node_shape=shape, font_family=font, font_size=10, linewidths=float(thickness), width=1.0, alpha=1.0, edgecolors='black')

        if save:
            plt.savefig(fname=path if path else self.default_file_name, format='png', dpi=dpi)
        if show:
            plt.show()   
        
        plt.close()
        
class BinarySearchTree(Tree):
    
    large: bool = False
    root: Optional['Tree.TreeNode'] = None
    pos: dict = {}
    skeleton: Optional[nx.Graph] = nx.Graph()
    filled: Optional[nx.Graph] = nx.Graph()
    
    default_file_name: str = 'bst_test.png'
    yaml_structure_type: str = 'binary_search_tree'
    formal_name: str = 'Binary Search Tree'
    
    def __init__(self, large: bool = False) -> None:
        self.large = large
        self.root = None
        self.pos = {}
        self.skeleton = nx.Graph()
        self.filled = nx.Graph()

    def generate(self) -> None:
        used_values = set()

        num_nodes = random.randint(3, 10) if not self.large else random.randint(11, 20)
        self.root = self._insert_node(None, random.randint(1, 99), used_values)

        for _ in range(1, num_nodes):
            self._insert_node(self.root, random.randint(1, 99), used_values)

        self._graphize(self.skeleton, self.root)

    def _insert_node(self, current: Optional[Tree.TreeNode], value: int, used_values: set) -> Tree.TreeNode:
        if value in used_values:
            return current

        if current is None:
            used_values.add(value)
            return Tree.TreeNode(value)

        if value < current.value:
            current.left = self._insert_node(current.left, value, used_values)
        else:
            current.right = self._insert_node(current.right, value, used_values)
        
        return current

    def _graphize(self, T: nx.Graph, node: Optional[Tree.TreeNode], x: int = 0, y: int = 0) -> None:
        if node is None:
            return

        self.pos[node.value] = (x, y)
        if node.left:
            T.add_edge(node.value, node.left.value)
            self._graphize(T, node.left, x - 1, y - 1)
        if node.right:
            T.add_edge(node.value, node.right.value)
            self._graphize(T, node.right, x + 1, y - 1)

    def fill(self) -> None:
        if self.root is None:
            return

        used_values = set()
        self._fill_node(self.root, 1, 99, used_values)

    def _fill_node(self, node: Optional[Tree.TreeNode], min_val: int, max_val: int, used_values: set) -> None:
        if node is None or min_val > max_val:
            return

        new_value = random.randint(min_val, max_val)
        while new_value in used_values:
            new_value = random.randint(min_val, max_val)

        node.value = new_value
        used_values.add(new_value)

        self._fill_node(node.left, min_val, node.value - 1, used_values)
        self._fill_node(node.right, node.value + 1, max_val, used_values)

    def draw(self, save: bool = False, path: Optional[Any] = None, show: bool = True, shape: Shape = 'o', color: Color = '#88d7fe', font: Font = 'sans-serif', thickness: Thickness = '1.0') -> None:
        if self.root is None:
            raise ValueError("The root is None")

        # DPI for the output
        dpi = 100
        
        # Calculate the figure size in inches for a 512x512 pixel image
        figure_size = 512 / dpi  # 5.12 when dpi is 100
        
        # Create a figure with the calculated size
        plt.figure(figsize=(figure_size, figure_size))
        
        nx.draw(self.skeleton, self.pos, with_labels=True, node_size=400, node_color=color, font_weight='bold', node_shape=shape, font_family=font, font_size=10, linewidths=float(thickness), width=1.0, alpha=1.0, edgecolors='black')
        
        if save:
            plt.savefig(fname=path if path else self.default_file_name, format='png', dpi=dpi)
        if show:
            plt.show()
            
        plt.close()