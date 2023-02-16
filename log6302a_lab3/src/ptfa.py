from code_analysis import *
import time


class CFGA:
    def __init__(self):
        self.cfg = None
        self.IN = []
        self.OUT = []
        self.nodeset = None

    def poss(IN, OUT, node, parent):
        return IN[node] or OUT[parent]

    def definit(IN, OUT, node, parent):
        return IN[node] and OUT[parent]

    def ptfa(self, cfg: CFG, func_comp, pattern_set=["Pattern"]):
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