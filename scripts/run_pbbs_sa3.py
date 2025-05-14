import m5
from m5.objects import *

import argparse

class L1ICache(Cache):
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 8
    tgts_per_mshr = 20
    size='4kB'

class L1DCache(Cache):
    assoc = 2
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 8
    tgts_per_mshr = 20
    size='4kB'


parser = argparse.ArgumentParser()
parser.add_argument(
    '-a', '--binary_args',
    default='',
    help='Command-line arguments to pass to the binary (default: random_10k_int)'
)
args = parser.parse_args()
binary_args = args.binary_args


# System creation
system = System()

## gem5 needs to know the clock and voltage
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '75MHz'
system.clk_domain.voltage_domain = VoltageDomain() # defaults to 1V

## Create a crossbar so that we can connect main memory and the CPU (below)
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

## Use timing mode for memory modelling
system.mem_mode = 'timing'

# CPU Setup
system.cpu = X86O3CPU()
system.cpu.branchPred = LocalBP(localPredictorSize=2048, localCtrBits=4)


## This is needed when we use x86 CPUs
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports


# Cache setup
system.cpu.l1d = L1DCache()
system.cpu.l1d.mem_side = system.membus.cpu_side_ports
system.cpu.l1d.cpu_side = system.cpu.dcache_port

system.cpu.l1i = L1ICache()
system.cpu.l1i.mem_side = system.membus.cpu_side_ports
system.cpu.l1i.cpu_side = system.cpu.icache_port



# Memory setup
system.mem_ctrl = MemCtrl()
system.mem_ctrl.port = system.membus.mem_side_ports

## A memory controller interfaces with main memory; create it here
system.mem_ctrl.dram = DDR3_1600_8x8()

## A DDR3_1600_8x8 has 8GB of memory, so setup an 8 GB address range
address_ranges = [AddrRange('8GB')]
system.mem_ranges = address_ranges
system.mem_ctrl.dram.range = address_ranges[0]

# Process setup
process = Process()

## Use a full path to the binary

process.executable = '/u/csc368h/winter/pub/workloads/pbbsbench/benchmarks/suffixArray/serialDivsufsort/SA'
process.cmd = [process.executable] + binary_args.split()

## The necessary gem5 calls to initialize the workload and its threads
system.workload = SEWorkload.init_compatible(process.executable)
system.cpu.workload = process
system.cpu.createThreads()

# Start the simulation
root = Root(full_system=False, system=system) # must assign a root

m5.instantiate() # must be called before m5.simulate

print(f"\nBeginning simulation with X86O3CPU, running {process.executable} {binary_args} ...")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}"
      .format(m5.curTick(), exit_event.getCause()))