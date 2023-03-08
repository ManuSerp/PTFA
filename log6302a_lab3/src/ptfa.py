from code_analysis import *
import time


class CFGA:
    def __init__(self):
        self.cfg = None
        self.IN = []
        self.OUT = []
        self.nodeset = None

    def reset(self):
        self.cfg = None
        self.IN = []
        self.OUT = []
        self.nodeset = None

    def poss(IN, OUT, node, parent):
        return IN[node] or OUT[parent]

    def definit(IN, OUT, node, parent):
        IN[node] = True
        return IN[node] and OUT[parent]

    def ptfa_reaching(self, cfg: CFG, func_comp, pattern_set=["Pattern"]):
        self.reset()
        t1 = time.time()
        # init
        self.cfg = cfg
        nodeid = self.cfg.get_node_ids()
        self.IN = [False] * len(nodeid)
        self.OUT = [False] * len(nodeid)
        self.oldOUT = [False] * len(nodeid)
        self.nodeset = nodeid
        changes = True
        # loop
        while changes:
            changes = False
            for node in self.nodeset:
                parents = self.cfg.get_any_parents(node)
                for parent in parents:
                    self.IN[node] = func_comp(self.IN, self.OUT, node, parent)
                self.oldOUT[node] = self.OUT[node]
                if self.cfg.get_type(node) in pattern_set:
                    self.OUT[node] = True
                else:
                    self.OUT[node] = self.IN[node]
                if self.oldOUT[node] != self.OUT[node]:
                    changes = True

        result = []
        for i in range(len(self.nodeset)):
            if self.OUT[i]:
                result.append(self.nodeset[i])
        t2 = time.time()-t1
        return result, t2

    def poss_ptfa_efficient_reaching(self, cfg: CFG, pattern_set=["Pattern"]):
        t1 = time.time()
        self.reset()
        # init
        self.cfg = cfg
        nodeid = self.cfg.get_node_ids()
        self.IN = [False] * len(nodeid)
        self.OUT = [False] * len(nodeid)
        self.nodeset = nodeid
        visited = []
        worklist = []
        visited.append(self.nodeset[0])
        visited.extend(self.cfg.get_func_entry_nodes())
        worklist.append(self.nodeset[0])
        worklist.extend(self.cfg.get_func_entry_nodes())
        # loop
        while len(worklist) > 0:
            node = worklist.pop(0)

            self.OUT[node] = (self.cfg.get_type(
                node) in pattern_set) or self.IN[node]
            for child in self.cfg.get_any_children(node):
                propagate_flag = (
                    (self.OUT[node] > self.IN[child]) or (not child in visited))
                if propagate_flag:
                    self.IN[child] = self.OUT[node]
                    visited.append(child)
                    worklist.append(child)

        result = []
        for i in range(len(self.nodeset)):
            if self.OUT[i]:
                result.append(self.nodeset[i])
        t2 = time.time()-t1
        return result, t2

    def poss_ptfa_efficient_reachable(self, cfg: CFG, pattern_set=["Pattern"]):
        t1 = time.time()
        self.reset()
        # init
        self.cfg = cfg
        nodeid = self.cfg.get_node_ids()
        self.IN = [False] * len(nodeid)
        self.OUT = [False] * len(nodeid)
        self.nodeset = nodeid
        visited = []
        worklist = []
        exits = []
        for node in nodeid:
            if self.cfg.get_type(node) == "Exit":
                exits.append(node)

        visited.extend(exits)
        worklist.extend(exits)
        # loop
        while len(worklist) > 0:
            node = worklist.pop(0)
            self.IN[node] = (self.cfg.get_type(
                node) in pattern_set) or self.OUT[node]
            for parent in self.cfg.get_any_parents(node):
                propagate_flag = (
                    (self.IN[node] > self.OUT[parent]) or (not parent in visited))
                if propagate_flag:
                    self.OUT[parent] = self.IN[node]
                    visited.append(parent)
                    worklist.append(parent)

        result = []

        for i in range(len(self.nodeset)):
            if self.IN[i] and i in visited:
                result.append(self.nodeset[i])
        t2 = time.time()-t1
        return result, t2

    def def_ptfa_efficient_reaching(self, cfg: CFG, pattern_set):
        t1 = time.time()
        self.reset()
        # init
        self.cfg = cfg

        nodeid = self.cfg.get_node_ids()
        self.IN = [True] * (len(nodeid)+nodeid[0])
        self.OUT = [True] * (len(nodeid)+nodeid[0])
        self.nodeset = nodeid
        visited = []
        worklist = []
        self.IN[0] = False
        visited.append(self.nodeset[0])
        visited.extend(self.cfg.get_func_entry_nodes())

        worklist.append(self.nodeset[0])
        worklist.extend(self.cfg.get_func_entry_nodes())
        # loop
        while len(worklist) > 0:
            node = worklist.pop(0)

            self.OUT[node] = (
                node in pattern_set) or self.IN[node]
            for child in self.cfg.get_any_children(node):
                propagate_flag = (
                    (self.OUT[node] < self.IN[child]) or (not child in visited))
                if propagate_flag:
                    self.IN[child] = self.OUT[node]
                    visited.append(child)
                    worklist.append(child)

        result = []
        for i in range(len(self.nodeset)):
            if self.OUT[self.nodeset[i]] and self.nodeset[i] in visited:
                result.append(self.nodeset[i])
        t2 = time.time()-t1
        return result, t2

    def def_ptfa_efficient_reachable(self, cfg: CFG, pattern_set):
        t1 = time.time()
        self.reset()
        # init
        self.cfg = cfg
        nodeid = self.cfg.get_node_ids()
        self.IN = [True] * (len(nodeid)+nodeid[0])
        self.OUT = [True] * (len(nodeid)+nodeid[0])
        self.nodeset = nodeid
        visited = []
        worklist = []
        exits = []
        for node in nodeid:
            if self.cfg.get_type(node) == "Exit":
                exits.append(node)

        for node in exits:
            self.OUT[node] = False
        visited.extend(exits)
        worklist.extend(exits)
        # loop
        while len(worklist) > 0:

            node = worklist.pop(0)
            self.IN[node] = (
                node in pattern_set) or self.OUT[node]

            for parent in self.cfg.get_any_parents(node):

                propagate_flag = (
                    (self.IN[node] < self.OUT[parent]) or (not parent in visited))
                if propagate_flag:
                    self.OUT[parent] = self.IN[node]
                    visited.append(parent)
                    worklist.append(parent)

        print(self.IN[58], " ", self.OUT[58])

        result = []

        for i in range(len(self.nodeset)):

            if self.IN[self.nodeset[i]] and self.nodeset[i] in visited:
                result.append(self.nodeset[i])
        t2 = time.time()-t1
        return result, t2


if __name__ == '__main__':

    cfgreader = CFGReader()

    cfg = cfgreader.read_cfg("../tp/perf/graph1.cfg.json")
    cfga = CFGA()
    print("Temps graph 1 :"+str(cfga.ptfa(cfg, CFGA.poss)[1])+" pour 100 patterns")

    cfg = cfgreader.read_cfg("../tp/perf/graph2.cfg.json")
    cfga = CFGA()
    print("Temps graph 2 :"+str(cfga.ptfa(cfg, CFGA.poss)[1])+" pour 1000 patterns")

    cfg = cfgreader.read_cfg("../tp/perf/graph3.cfg.json")
    cfga = CFGA()
    print("Temps graph 3 :"+str(cfga.ptfa(cfg, CFGA.poss)[1])+" pour 10000 patterns")

    cfg = cfgreader.read_cfg("../tp/perf/graph4.cfg.json")
    cfga = CFGA()
    print("Temps graph 4 :"+str(cfga.ptfa(cfg, CFGA.poss)[1])+" pour 100000 patterns")
    
  

    # fopenfclose
    cfg = cfgreader.read_cfg("../tp/part_1/file1.php.cfg.json")
    cfga = CFGA()
    nodes = cfg.get_node_ids()
    fopens = []
    pattern = []
    for node in nodes:
        if cfg.get_image(node) == "fopen":
            fopens.append(node)
        if cfg.get_image(node) == "fclose":
            pattern.append(node)

    reachable = cfga.def_ptfa_efficient_reachable(cfg, pattern)

    for fopen in fopens:
        if fopen not in reachable:
            print(f"fopen {fopen} is not reachable by a fclose")


# mysql

    cfg = cfgreader.read_cfg("../tp/part_2/wp-db.php.cfg.json")
    cfga = CFGA()
    nodes = cfg.get_node_ids()
    mysql = []
    pattern = []
    for node in nodes:
        if cfg.get_image(node) == "mysql_query":
            mysql.append(node)
        if cfg.get_image(node) == "has_cap":
            pattern.append(node)

    print(mysql)
    reaching = cfga.def_ptfa_efficient_reaching(cfg, pattern)
    line_to_protect = []
    for sql in mysql:
        if sql not in reaching:
            print(
                f"sql query {cfg.get_position(sql)} is not protected by a has_cap")
            if cfg.get_position(sql):
                line_to_protect.append(cfg.get_position(sql)[0])

    print(line_to_protect)

    f = open("./code_protected.php", "w+")
    g = open("../tp/part_2/wp-db.php", "r")
    lines = g.readlines()
    for i, line in enumerate(lines):
        if i+1 in line_to_protect:
            f.write("if ( has_cap( 'use_db' ) )\n"+line)
        else:
            f.write(line)

    f.close()

