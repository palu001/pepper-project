
from datetime import datetime
import math

class CinemaMap:
    """Graph-based representation of the cinema layout"""
    
    def __init__(self):
        # Define nodes in the cinema (x, y coordinates in meters)
        self.nodes = {
            'entrance': (0, 0),
            'lobby_center': (-3, 0),
            'box_office': (-3, -2),
            'concession': (-4, -2),
            'bathroom': (-3, 2),
            'hallway_center': (-10, 0),
            'screen1_entrance': (-8, 3),
            'screen1': (-8, 5),
            'screen2_entrance': (-10, 2),
            'screen2': (-10, 4),
            'screen3_entrance': (-12, 2),
            'screen3': (-12, 4),
            'screen4_entrance': (-8, -2),
            'screen4': (-8, -5),
            'screen5_entrance': (-10, -2),
            'screen5': (-10, -4),
            'screen6_entrance': (-12, -2),
            'screen6': (-12, -4),
            'screen7_entrance': (-14, 0),
            'screen7': (-14, -2),
            'screen8_entrance': (-14, 3),
            'screen8': (-14, 5),
            'exit': (-15, 0)
        }

    # Define edges (connections between nodes)
        self.edges = {
            'entrance': ['lobby_center'],
            'lobby_center': ['entrance', 'box_office', 'concession', 'hallway_center','bathroom'],
            'box_office': ['lobby_center','concession'],
            'concession': ['lobby_center','box_office'],
            'bathroom': ['lobby_center'],
            'hallway_center': ['lobby_center',  'screen1_entrance', 'screen2_entrance', 
                                'screen4_entrance', 'screen5_entrance', 'screen7_entrance'],
            'screen1_entrance': ['hallway_center', 'screen1'],
            'screen1': ['screen1_entrance'],
            'screen2_entrance': ['hallway_center', 'screen2', 'screen3_entrance'],
            'screen2': ['screen2_entrance'],
            'screen3_entrance': ['screen2_entrance', 'screen3'],
            'screen3': ['screen3_entrance'],
            'screen4_entrance': ['hallway_center', 'screen4', 'screen5_entrance'],
            'screen4': ['screen4_entrance'],
            'screen5_entrance': ['hallway_center', 'screen4_entrance', 'screen5', 'screen6_entrance'],
            'screen5': ['screen5_entrance'],
            'screen6_entrance': ['screen5_entrance', 'screen6'],
            'screen6': ['screen6_entrance'],
            'screen7_entrance': ['hallway_center', 'screen7', 'screen8_entrance'],
            'screen7': ['screen7_entrance'],
            'screen8_entrance': ['screen7_entrance', 'screen8'],
            'screen8': ['screen8_entrance'],
            'exit': [ 'screen7_entrance'],
        }
        
        # Location mapping for user requests
        self.location_mapping = {
            'bathroom': 'bathroom',
            'restroom': 'bathroom',
            'washroom': 'bathroom',
            'concession': 'concession',
            'concession stand': 'concession',
            'box office': 'box_office',
            'ticket office': 'box_office',
            'entrance': 'entrance',
            'exit': 'exit',
            'screen': 'screen{}'  # Will be formatted with screen number
        }
        
    def get_distance(self, node1, node2):
        """Calculate Euclidean distance between two nodes"""
        x1, y1 = self.nodes[node1]
        x2, y2 = self.nodes[node2]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def find_shortest_path(self, start, end):
        """Find shortest path using Dijkstra's algorithm"""
        if start not in self.nodes or end not in self.nodes:
            return None
        
        # Initialize distances and previous nodes
        distances = {node: float('infinity') for node in self.nodes}
        distances[start] = 0
        previous = {}
        unvisited = set(self.nodes.keys())
        
        while unvisited:
            # Find unvisited node with minimum distance
            current = min(unvisited, key=lambda node: distances[node])
            
            if distances[current] == float('infinity'):
                break
                
            unvisited.remove(current)
            
            if current == end:
                break
                
            # Update distances to neighbors
            for neighbor in self.edges.get(current, []):
                if neighbor in unvisited:
                    distance = distances[current] + self.get_distance(current, neighbor)
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current
        
        # Reconstruct path
        if end not in previous and start != end:
            return None
            
        path = []
        current = end
        while current is not None:
            path.insert(0, current)
            current = previous.get(current)
            
        return path if path[0] == start else None