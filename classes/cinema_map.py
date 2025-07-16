
from datetime import datetime
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

class CinemaMap:
    """Graph-based representation of the cinema layout"""
    
    def __init__(self, scale=0.3):
        # Define nodes in the cinema (x, y coordinates in meters)
        self.current_position="entrance"
        base_nodes= {
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
        self.nodes = {
            name: (x * scale, y * scale)
            for name, (x, y) in base_nodes.items()
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
            'box_office':'box_office',
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
    
    def find_shortest_path(self, end):
        """Find shortest path using Dijkstra's algorithm"""
        start=self.current_position
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
    
    def draw_map_with_path(self, end, bathroom_busy,save_path='cinema_map_path.png'):
        path = self.find_shortest_path(end)
        if not path:
            print("No path found.")
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('#f8f9fa')  # Light background for web

        # Draw all edges (connections)
        for start, neighbors in self.edges.items():
            for neighbor in neighbors:
                x_vals = [self.nodes[start][0], self.nodes[neighbor][0]]
                y_vals = [self.nodes[start][1], self.nodes[neighbor][1]]
                ax.plot(x_vals, y_vals, color='lightgray', linewidth=1, zorder=1)

        # Draw all nodes
        for node, (x, y) in self.nodes.items():
            label = node.replace('_', ' ').title()
            if "Screen" in label and "_" in node:
                label = label.replace(" Entrance", "")

            # Indicate busy bathroom
            if node.lower() == "bathroom" and bathroom_busy:
                color = 'red'
                size = 100
                ax.scatter(x, y, c=color, s=size, marker='X', zorder=6, label='Bathroom Busy')
                ax.text(x + 0.2, y + 0.2, label + " (Busy)", fontsize=7, color='red', zorder=7)
            else:
                color = 'black'
                size = 30
                ax.scatter(x, y, c=color, s=size, zorder=2)
                ax.text(x + 0.2, y + 0.2, label, fontsize=7, color='black', zorder=3)


        # Highlight path
        path_coords = [self.nodes[node] for node in path]
        x_path, y_path = zip(*path_coords)
        ax.plot(x_path, y_path, 'red', linewidth=3, zorder=4, label='Path')

        # Highlight start and end nodes
        start_node = self.current_position
        end_node = end
        sx, sy = self.nodes[start_node]
        ex, ey = self.nodes[end_node]

        ax.scatter(sx, sy, c='green', s=80, label='Start', zorder=5)
        ax.scatter(ex, ey, c='blue', s=80, label='End', zorder=5)

        # Clean and format
        ax.set_title('Cinema Map with Path', fontsize=14)
        ax.axis('equal')
        ax.axis('off')  # Hide axes for a cleaner look
        ax.legend(loc='lower left', fontsize=8)

        # Save for web use
        plt.tight_layout()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_path = os.path.join(base_dir, "tablet/img", save_path)
        plt.savefig(save_path, dpi=150, transparent=True)
        plt.close()
        print("Map saved")
        return path

        