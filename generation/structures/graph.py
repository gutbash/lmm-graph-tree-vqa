"""
The graph module contains the classes and methods for random directed and undirected graphs.
"""

import networkx as nx
import matplotlib.pyplot as plt
import random
from pathlib import Path
from typing import Optional, Literal

Color = Literal['#88d7fe', '#feaf88', '#eeeeee']
Shape = Literal['o', 's', 'd']
Font = Literal['sans-serif', 'serif', 'monospace']
Thickness = Literal['0.5', '1.0', '1.5']

class Graph:
    
    def adjacency_list(self) -> dict:
        """
        Returns the adjacency list of the graph with node values as keys
        
        Parameters
        ----------
        None
        
        Returns
        -------
        dict
            the adjacency list of the graph
        """
        
        adj_list = {}
        for node in self.filled.nodes:
            # Get the value of the node
            node_value = self.filled.nodes[node]['value']
            # Get the values of the neighbors
            neighbor_values = [self.filled.nodes[neighbor]['value'] for neighbor in self.filled.neighbors(node)]
            # Store in the dictionary
            adj_list[node_value] = neighbor_values

        return adj_list
    
    def breadth_first_search(self) -> list:
        """
        Returns the BFS traversal of the graph
        
        Parameters
        ----------
        None
        
        Returns
        -------
        list
            the BFS traversal of the graph
        """
        if not self.filled:
            raise ValueError("The graph is empty.")
        start_node = next(iter(self.filled))
        bfs_nodes = list(nx.bfs_tree(self.filled, source=start_node).nodes)
        bfs_values = [self.filled.nodes[node]['value'] for node in bfs_nodes]
        return bfs_values
    
    def depth_first_search(self) -> list:
        """
        Returns the DFS traversal of the graph
        
        Parameters
        ----------
        None
        
        Returns
        -------
        list
            the DFS traversal of the graph
        """
        if not self.filled:
            raise ValueError("The graph is empty.")
        start_node = next(iter(self.filled))
        dfs_nodes = list(nx.dfs_tree(self.filled, source=start_node).nodes)
        dfs_values = [self.filled.nodes[node]['value'] for node in dfs_nodes]
        return dfs_values

class UndirectedGraph(Graph):
    """
    An undirected graph
    
    Attributes
    ----------
    large : bool
        whether the graph should be large or not
    skeleton : nx.Graph
        the basic structure of the undirected graph
    filled : nx.Graph
        the filled undirected graph
    default_file_name : str
        the default file name for the image
    yaml_structure_type : str
        the YAML structure type
    formal_name : str
        the formal name of the structure
        
    Methods
    -------
    __init__(large: bool = False)
        Constructs all the necessary attributes for the UndirectedGraph object
    generate()
        Generates a random undirected graph
    fill()
        Fills the graph nodes with the given values
    draw(save: bool = False, path: Optional[Path] = None, show: bool = True)
        Visualizes the generated undirected graph
    """
    large: bool = False
    skeleton: nx.DiGraph = nx.DiGraph()
    filled: nx.DiGraph = nx.DiGraph()
    
    default_file_name: str = 'ug_test.png'
    yaml_structure_type: str = 'undirected_graph'
    formal_name: str = 'Undirected Graph'
    
    def __init__(self, large: bool = False) -> None:
        """
        Constructs all the necessary attributes for an UndirectedGraph object
        
        Parameters
        ----------
        large : bool
            whether the graph should be large or not
        """
        self.large = large
        self.skeleton = nx.Graph()
        self.filled = nx.Graph()
        
    def generate(self) -> None:
        """
        Generates a random undirected graph with basic structure
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        G = nx.Graph()

        num_nodes = random.randint(11, 20) if self.large else random.randint(3, 10)
        if num_nodes <= 0:
            return

        for i in range(1, num_nodes):
            G.add_edge(i - 1, i)

        additional_edges = random.randint(1, num_nodes * (num_nodes - 1) // 4)

        while additional_edges > 0:
            source, target = random.randint(0, num_nodes - 1), random.randint(0, num_nodes - 1)
            if source != target and not G.has_edge(source, target):
                G.add_edge(source, target)
                additional_edges -= 1

        self.skeleton = G

    def fill(self) -> None:
        """
        Fills the graph nodes with the given values

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        self.filled = self.skeleton.copy()
        
        values = [i for i in range(1, len(self.filled)+1)]

        for i, node in enumerate(self.filled.nodes):
            self.filled.nodes[node]['value'] = values[i]
        
    def draw(self, save: bool = False, path: Optional[Path] = None, show: bool = True, shape: Shape = 'o', color: Color = '#88d7fe', font: Font = 'sans-serif', thickness: Thickness = '1.0') -> None:
        """
        Visualizes the generated undirected graph
        
        Parameters
        ----------
        save : bool
            whether or not to save the image
        path : Optional[Path]
            the path to the image
        show : bool
            whether or not to show the image
        shape : Shape
            the shape of the nodes (default is 'o')
        color : Color
            the color of the nodes (default is '#88d7fe' aka sky blue)
        font : Font
            the font of the node labels (default is 'sans-serif')
        thickness : Thickness
            the thickness of the edges (default is '1.0')

        Returns
        -------
        None
        
        Notes
        -----
        The visualization is done using the networkx and matplotlib libraries.
        
        The nodes are labeled with their values.

        The graph is drawn using the spring layout.
        
        The graph is displayed using matplotlib.
        """
        
        # DPI for the output
        dpi = 100
        
        # Calculate the figure size in inches for a 512x512 pixel image
        figure_size = 512 / dpi  # 5.12 when dpi is 100
        
        pos = nx.spring_layout(self.skeleton, seed=42)  # Set seed for reproducibility
    
        # Create a figure with the calculated size
        plt.figure(figsize=(figure_size, figure_size))
        
        labels = {node: self.skeleton.nodes[node].get('value', node) for node in self.skeleton.nodes}
        nx.draw(self.skeleton, pos, with_labels=True, font_weight='bold', node_size=400, node_color=color, node_shape=shape, font_family=font, labels=labels, font_size=10, linewidths=float(thickness), width=1.0, alpha=1.0, edgecolors='black')

        if save:
            plt.savefig(fname=path if path else self.default_file_name, format='png', dpi=dpi)
        if show:
            plt.show()
            
        plt.close()

class DirectedGraph(Graph):
    """
    A directed graph
    
    Attributes
    ----------
    large : bool
        whether the graph should be large or not
    default_file_name : str
        the default file name for the image
    yaml_structure_type : str
        the YAML structure type
    formal_name : str
        the formal name of the structure
        
    Methods
    -------
    __init__(large: bool = False)
        Constructs all the necessary attributes for the DirectedGraph object
    generate()
        Generates a random directed graph
    fill()
        Fills the graph nodes with the given values
    draw(save: bool = False, path: Optional[Path] = None, show: bool = True)
        Visualizes the generated directed graph
    """
    large: bool = False
    skeleton: nx.DiGraph = nx.DiGraph()
    filled: nx.DiGraph = nx.DiGraph()
    
    default_file_name: str = 'dg_test.png'
    yaml_structure_type: str = 'directed_graph'
    formal_name: str = 'Directed Graph'
    
    def __init__(self, large: bool = False) -> None:
        """
        Constructs all the necessary attributes for a DirectedGraph object
        
        Parameters
        ----------
        large : bool
            whether the graph should be large or not
        """
        self.large = large
        self.skeleton = nx.DiGraph()
        self.filled = nx.DiGraph()

    def generate(self) -> None:
        """
        Generates a random directed graph with basic structure
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        G = nx.DiGraph()

        # Determine the number of nodes
        num_nodes = random.randint(11, 20) if self.large else random.randint(3, 10)
        if num_nodes <= 0:
            return

        # Create a connected graph (spanning tree)
        for i in range(1, num_nodes):
            G.add_edge(i - 1, i)

        # Randomize additional edges with control to avoid clutter
        additional_edges = random.randint(1, num_nodes * (num_nodes - 1) // 4)
        while additional_edges > 0:
            source, target = random.randint(0, num_nodes - 1), random.randint(0, num_nodes - 1)
            if source != target and not G.has_edge(source, target):
                G.add_edge(source, target)
                additional_edges -= 1

        self.skeleton = G
        
    def fill(self) -> None:
        """
        Fills the graph nodes with the given values

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        self.filled = self.skeleton.copy()
        
        values = [i for i in range(1, len(self.filled)+1)]

        for i, node in enumerate(self.filled.nodes):
            self.filled.nodes[node]['value'] = values[i]

    def draw(self, save: bool = False, path: Optional[Path] = None, show: bool = True, shape: Shape = 'o', color: Color = '#88d7fe', font: Font = 'sans-serif', thickness: Thickness = '1.0') -> None:
        """
        Visualizes the generated directed graph
        
        Parameters
        ----------
        save : bool
            whether or not to save the image
        path : Optional[Path]
            the path to the image
        show : bool
            whether or not to show the image
        shape : Shape
            the shape of the nodes (default is 'o')
        color : Color
            the color of the nodes (default is '#88d7fe' aka sky blue)
        font : Font
            the font of the node labels (default is 'sans-serif')
        thickness : Thickness
            the thickness of the edges (default is '1.0')

        Returns
        -------
        None
        
        Notes
        -----
        The visualization is done using the networkx and matplotlib libraries.
        
        The nodes are labeled with their values.
        
        The graph is drawn using the spring layout.
        
        The graph is displayed using matplotlib.
        """
        if self.skeleton is None or len(self.skeleton.nodes()) == 0:
            raise ValueError("Graph is empty or not generated")
        
        pos = nx.spring_layout(self.filled, seed=42)  # Set seed for reproducibility

        # DPI for the output
        dpi = 100
        
        # Calculate the figure size in inches for a 512x512 pixel image
        figure_size = 512 / dpi  # 5.12 when dpi is 100
        
        # Create a figure with the calculated size
        plt.figure(figsize=(figure_size, figure_size))
        
        labels = {node: self.skeleton.nodes[node].get('value', node) for node in self.skeleton.nodes}
        nx.draw(self.skeleton, pos, with_labels=True, font_weight='bold', node_size=400, node_color=color, node_shape=shape, font_family=font, labels=labels, font_size=10, linewidths=float(thickness), width=1.0, alpha=1.0, edgecolors='black')

        if save:
            plt.savefig(fname=path if path else self.default_file_name, format='png', dpi=dpi)
        if show:
            plt.show()
        
        plt.close()
