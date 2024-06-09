import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# Load the data
df = pd.read_csv('flights.csv')

# Filter the necessary columns
main_columns = ['origin', 'dest', 'distance', 'air_time', 'name']
df1 = df[main_columns]

# Create a graph from the DataFrame
gf = nx.from_pandas_edgelist(df1, source='origin', target='dest', edge_attr=True)

def find_dijkstra_path():
    source = source_entry.get().strip().upper()
    target = target_entry.get().strip().upper()
    if source in gf.nodes and target in gf.nodes:
        try:
            path = nx.dijkstra_path(gf, source=source, target=target, weight='air_time')
            total_weight = nx.dijkstra_path_length(gf, source=source, target=target, weight='air_time')
            display_results(path, total_weight)
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path found between these airports.")
    else:
        messagebox.showerror("Error", "Invalid source or target airport.")

def find_astar_path():
    source = source_entry.get().strip().upper()
    target = target_entry.get().strip().upper()
    if source in gf.nodes and target in gf.nodes:
        threading.Thread(target=run_astar, args=(source, target)).start()
    else:
        messagebox.showerror("Error", "Invalid source or target airport.")

def run_astar(source, target):
    try:
        path = nx.astar_path(gf, source=source, target=target, heuristic=lambda u, v: 0, weight='air_time')
        total_weight = nx.astar_path_length(gf, source=source, target=target, heuristic=lambda u, v: 0, weight='air_time')
        display_results(path, total_weight)
    except nx.NetworkXNoPath:
        messagebox.showerror("Error", "No path found between these airports.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def find_floyd_warshall_path():
    source = source_entry.get().strip().upper()
    target = target_entry.get().strip().upper()
    if source in gf.nodes and target in gf.nodes:
        try:
            pred, dist = nx.floyd_warshall_predecessor_and_distance(gf, weight='air_time')
            if dist[source][target] < float('inf'):
                path = reconstruct_path(pred, source, target)
                total_weight = dist[source][target]
                display_results(path, total_weight)
            else:
                messagebox.showerror("Error", "No path found between these airports.")
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path found between these airports.")
        except KeyError as e:
            messagebox.showerror("Error", f"KeyError: {e} not found in predecessor dictionary.")
    else:
        messagebox.showerror("Error", "Invalid source or target airport.")

def reconstruct_path(pred, source, target):
    path = []
    if source == target:
        path.append(source)
        return path
    if target not in pred[source]:
        raise KeyError(f"{target} not reachable from {source}")
    current = target
    while current != source:
        if current not in pred[source]:
            raise KeyError(f"No predecessor for {current} from {source}")
        path.insert(0, current)
        current = pred[source][current]
    path.insert(0, source)
    return path

def find_bidirectional_dijkstra_path():
    source = source_entry.get().strip().upper()
    target = target_entry.get().strip().upper()
    if source in gf.nodes and target in gf.nodes:
        try:
            path = nx.bidirectional_dijkstra(gf, source=source, target=target, weight='air_time')
            total_weight = path[0]
            path = path[1]
            display_results(path, total_weight)
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No path found between these airports.")
    else:
        messagebox.showerror("Error", "Invalid source or target airport.")

def display_results(path, total_weight):
    result_label.config(text=f"Shortest Path: {' -> '.join(path)}\nTotal Air Time: {total_weight:.2f} minutes")

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(gf)
    nx.draw_networkx_nodes(gf, pos, node_size=500)
    nx.draw_networkx_edges(gf, pos, alpha=0.5)
    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    nx.draw_networkx_edges(gf, pos, edgelist=path_edges, edge_color='g', width=3)
    nx.draw_networkx_labels(gf, pos)
    
    canvas = FigureCanvasTkAgg(plt.gcf(), master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def initialize():
    global source_entry, target_entry, result_label

    for widget in root.pack_slaves():
        widget.destroy()

    heading = tk.Label(root, text="FLIGHT ROUTE OPTIMIZATION", bg='#2596be', fg='white', font=('Arial', 18, 'bold'))
    heading.pack(pady=10)

    frame = tk.Frame(root, bg='lightblue')
    frame.pack(pady=10, padx=10, fill='x')

    tk.Label(frame, text="Source Airport:", bg='lightblue', font=('Arial', 8)).pack(pady=2)
    source_entry = tk.Entry(frame, font=('Arial', 8))
    source_entry.pack(pady=2)

    tk.Label(frame, text="Target Airport:", bg='lightblue', font=('Arial', 8)).pack(pady=2)
    target_entry = tk.Entry(frame, font=('Arial', 8))
    target_entry.pack(pady=2)

    create_button(frame, "Find Shortest Path (Dijkstra)", find_dijkstra_path).pack(pady=3)
    create_button(frame, "Find Shortest Path (A*)", find_astar_path).pack(pady=3)
    create_button(frame, "Find Shortest Path (Floyd-Warshall)", find_floyd_warshall_path).pack(pady=3)
    create_button(frame, "Find Shortest Path (Bidirectional Dijkstra)", find_bidirectional_dijkstra_path).pack(pady=3)
    create_button(frame, "Refresh", initialize).pack(pady=10)

    result_label = tk.Label(root, text="", font=("Arial", 10), bg='lightblue')
    result_label.pack(pady=10, padx=10, fill='x')

def create_button(frame, text, command):
    button = tk.Button(frame, text=text, command=command, bg='white', fg='black', font=('Arial', 8), relief='raised', bd=2)
    button.bind("<Enter>", lambda e: button.config(bg='lightgrey'))
    button.bind("<Leave>", lambda e: button.config(bg='white'))
    button.bind("<ButtonPress-1>", lambda e: button.config(bg='darkgrey'))
    button.bind("<ButtonRelease-1>", lambda e: button.config(bg='lightgrey'))
    return button

root = tk.Tk()
root.title("Flight Optimization")
root.geometry("800x600")

# Set background color
root.configure(bg='#2596be')

initialize()
root.mainloop()



