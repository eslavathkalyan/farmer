import random
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import time

processes = ['P1', 'P2', 'P3', 'P4']
resources = ['R1', 'R2', 'R3']

class Monitor:
    def __init__(self):
        self.allocations = {p: [] for p in processes}
        self.requests = {p: [] for p in processes}
        self.resource_owner = {r: None for r in resources}
        self.data = []

    def request_resource(self, process, resource):
        if self.resource_owner[resource] is None:
            self.allocations[process].append(resource)
            self.resource_owner[resource] = process
        else:
            self.requests[process].append(resource)
        self.log(process, resource)

    def release_resource(self, process, resource):
        if resource in self.allocations[process]:
            self.allocations[process].remove(resource)
            self.resource_owner[resource] = None

    def log(self, process, resource):
        row = {
            'Process': process,
            'Requested': resource,
            'Allocated': self.resource_owner[resource] == process,
            'Timestamp': time.time()
        }
        self.data.append(row)

    def get_dataframe(self):
        return pd.DataFrame(self.data)

class DeadlockDetector:
    def __init__(self, monitor):
        self.monitor = monitor
        self.wait_for_graph = nx.DiGraph()

    def build_graph(self):
        self.wait_for_graph.clear()
        for p in processes:
            for r in self.monitor.requests[p]:
                holder = self.monitor.resource_owner[r]
                if holder:
                    self.wait_for_graph.add_edge(p, holder)

    def detect_deadlock(self):
        try:
            cycles = list(nx.simple_cycles(self.wait_for_graph))
            return cycles if cycles else None
        except Exception as e:
            print("Detection error:", e)
            return None

    def resolve_deadlock(self, cycles):
        print("Deadlock Detected:", cycles)
        for cycle in cycles:
            victim = random.choice(cycle)
            print(f"Terminating {victim} to break the deadlock.")
            for r in list(self.monitor.allocations[victim]):
                self.monitor.release_resource(victim, r)
            self.monitor.requests[victim].clear()
            self.monitor.allocations[victim] = []

def visualize(graph):
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.title("Wait-For Graph")
    plt.show()

def simulate_data():
    data = []
    for _ in range(200):
        p = random.choice(processes)
        r = random.choice(resources)
        allocated = random.choice([True, False])
        data.append({'Process': p, 'Requested': r, 'Allocated': allocated})
    return pd.DataFrame(data)

def train_predictor(data):
    data['Allocated'] = data['Allocated'].astype(int)
    data['Process'] = data['Process'].astype('category').cat.codes
    data['Requested'] = data['Requested'].astype('category').cat.codes

    X = data[['Process', 'Requested']]
    y = data['Allocated']
    clf = RandomForestClassifier()
    clf.fit(X, y)
    return clf

def main():
    monitor = Monitor()
    detector = DeadlockDetector(monitor)

    print("Simulating resource allocation...")
    for _ in range(30):
        proc = random.choice(processes)
        res = random.choice(resources)
        monitor.request_resource(proc, res)
        time.sleep(0.1)

        detector.build_graph()
        cycles = detector.detect_deadlock()
        if cycles:
            detector.resolve_deadlock(cycles)
            visualize(detector.wait_for_graph)

    print("\nFinal Log:")
    df = monitor.get_dataframe()
    print(df.tail())

    print("\nTraining prediction model...")
    training_data = simulate_data()
    model = train_predictor(training_data)
    sample = pd.DataFrame([{'Process': 1, 'Requested': 2}])
    prediction = model.predict(sample)
    print("AI Prediction for sample:", "Will Allocate" if prediction[0] else "May Cause Deadlock")

if __name__ == "__main__":
    main()
