import argparse
import json
import random
import numpy as np
import multiprocessing as mp
import ctypes

ID_MAP_SUFFIX = '-id_map.json'
CLASS_MAP_SUFFIX = '-class_map.json'
G_SUFFIX = '-G.json'
FEATS_SUFFIX = '-feats.npy'
NUM_FEATURES = 100
NUM_CLASSES = 121

def node_worker(pid, num_processes, num_nodes, num_features, num_classes, feature_data):
    cmf = open('tmp/%d-class_map.json' % pid, 'w')
    gnf = open('tmp/%d-G_node.json' % pid, 'w')
    node_data = {}
    for i in range(1 + pid, num_nodes, num_processes):
        node_data["test"] = (i > 0.8 * num_nodes)
        node_data["id"] = i
        node_data["feature"] = [random.random() for _ in range(num_features)]
        node_data["val"] = (i > 0.65 * num_nodes and i <= 0.8 * num_nodes )
        node_data["label"] = [random.randint(0, 1) for _ in range(num_classes)]
        cmf.write(', \"%d\": %s' % (i, json.dumps(node_data["label"])))
        for j in range(num_features):
            feature_data[i*num_features + j] = node_data["feature"][j]
        gnf.write(', %s' % json.dumps(node_data))
    cmf.close()
    gnf.close()

def edge_worker(pid, num_processes, num_nodes, num_edges):
    gef = open('tmp/%d-G_edge.json' % pid, 'w')
    edge_data = {}
    for i in range(pid, num_nodes, num_processes):
        for j in range(num_edges):
            edge_data["test_removed"] = False
            edge_data["train_removed"] = (i > 0.8 * num_nodes)
            edge_data["target"] = random.randint(0, num_nodes - 1)
            edge_data["source"] = i
            gef.write(', %s' % json.dumps(edge_data))
    gef.close()

def main():
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('--nodes', default=1000)
    parser.add_argument('--edges', default=10)
    parser.add_argument('--prefix', default='data')
    parser.add_argument('--processes', default=mp.cpu_count())
    args = parser.parse_args()
    args.nodes = int(args.nodes)
    args.edges = int(args.edges)
    args.processes = int(args.processes)
    id_map_file = open(args.prefix + ID_MAP_SUFFIX, 'w')
    id_map_file.write('{"0": 0')
    for i in range(1, args.nodes):
        id_map_file.write(', \"%d\": %d' % (i, i))
    id_map_file.write('}')
    id_map_file.close()
    class_map_first = open('tmp/class_map_first.json', 'w')
    feats_file = open(args.prefix + FEATS_SUFFIX, 'wb')
    g_file_first = open('tmp/G_first.json', 'w')
    class_map_first.write('{')
    g_file_first.write('{"directed": false, "graph": {"name": "disjoint_union( ,  )"}, "nodes": [')
    node_data = {}
    node_data["test"] = False
    node_data["id"] = 0
    node_data["feature"] = [random.random() for _ in range(NUM_FEATURES)]
    node_data["val"] = False
    node_data["label"] = [random.randint(0, 1) for _ in range(NUM_CLASSES)]
    class_map_first.write('\"0\": ')
    json.dump(node_data["label"], class_map_first)
    json.dump(node_data, g_file_first)
    class_map_first.close()
    g_file_first.close()
    
    manager = mp.Manager()
    pool = mp.Pool(args.processes + 1)
    feature_data = manager.Array('d', [0] * (args.nodes * NUM_FEATURES), lock=False)
    for i in range(NUM_FEATURES):
        feature_data[i] = node_data["feature"][i]
    jobs = []
    for i in range(args.processes):
        job = pool.apply_async(node_worker, (i, args.processes, args.nodes, NUM_FEATURES, NUM_CLASSES, feature_data))
        jobs.append(job)
    for job in jobs: 
        job.get()
    pool.close()
    pool.join()
    class_map_second = open('tmp/class_map_second.json', 'w')
    class_map_second.write('}')
    class_map_second.close()

    g_file_second = open('tmp/G_second.json', 'w')
    g_file_second.write('], \"links\": [')
    edge_data = {}
    edge_data["test_removed"] = False
    edge_data["train_removed"] = False
    edge_data["target"] = random.randint(0, args.nodes - 1)
    edge_data["source"] = 0
    json.dump(edge_data, g_file_second)
    g_file_second.close()

    manager2 = mp.Manager()
    pool = mp.Pool(args.processes + 1)
    jobs = []
    for i in range(args.processes):
        job = pool.apply_async(edge_worker, (i, args.processes, args.nodes, args.edges))
        jobs.append(job)

    np.save(feats_file, np.asarray(feature_data).reshape((args.nodes, NUM_FEATURES)))
    feats_file.close()
    for job in jobs: 
        job.get()
    pool.close()
    pool.join()
    
    g_file_third = open('tmp/G_third.json', 'w')
    g_file_third.write(']}')
    g_file_third.close()
    

if __name__ == "__main__":
    main()
