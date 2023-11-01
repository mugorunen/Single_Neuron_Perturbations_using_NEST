# Import necessary libraries
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from network_functions import NetworkAnalyzer
from plotting_functions import PlottingFuncs
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize, LogNorm
from matplotlib.cm import ScalarMappable
from scipy.signal import convolve2d
from scipy.signal import convolve
import networkx as nx
import nest
import nest.raster_plot


simtime = 20000.0  # Simulation time in ms
order = 400

# Define Simulation Parameters
bin_width = 200.0
delay = 1.5  # synaptic delay in ms
g = 5.0  # ratio inhibitory weight/excitatory weight
eta = 2.0  # external rate relative to threshold rate
epsilon = 0.05  # connection probability
NE = 4 * order  # number of excitatory neurons
NI = 1 * order  # number of inhibitory neurons
N_neurons = NE + NI  # number of neurons in total
CE = int(epsilon * NE)  # number of excitatory synapses per neuron
CI = int(epsilon * NI)  # number of inhibitory synapses per neuron
C_tot = int(CI + CE)  # total number of synapses per neuron
# Define Neuron Parameters
tauMem = 20.0  # time constant of membrane potential in ms
theta = 20.0  # membrane threshold potential in mV
neuron_params = {"C_m": 1.0,
                 "tau_m": tauMem,
                 "t_ref": 2.0,
                 "E_L": 0.0,
                 "V_reset": 0.0,
                 "V_m": 0.0,
                 "V_th": theta}
J = 1.4  # postsynaptic amplitude in mV
J_ex = J  # amplitude of excitatory postsynaptic potential
J_in = -g * J_ex  # amplitude of inhibitory postsynaptic potential
nu_th = theta / (J * CE * tauMem)
nu_ex = eta * nu_th
p_rate = 1000.0 * nu_ex * CE / 3

plotting_flag=True

analyzer = NetworkAnalyzer(NE, NI, N_neurons, simtime, bin_width)
m_plot = PlottingFuncs(N_neurons, simtime, bin_width, CE, CI)

# Reset previous simulations
nest.ResetKernel()
# Set the number of threads you want to use
num_threads = 10
# Set the kernel status to change the number of threads
nest.SetKernelStatus({"local_num_threads": num_threads})
# Set connection seed
connection_seed=44
nest.SetKernelStatus({"rng_seed": connection_seed})
dt = 0.1  # the resolution in ms
nest.resolution = dt
nest.print_time = True
nest.overwrite_files = True

print("Building network")
#Define Connection Parameters
conn_params_ex = {"rule": "fixed_indegree", "indegree": CE}
conn_params_in = {"rule": "fixed_indegree", "indegree": CI}
#Define the Positions
pos_ex = nest.spatial.free(pos=nest.random.uniform(min=-2.0, max=2.0), num_dimensions=2)
# Create excitatory neurons, inhibitory neurons, poisson spike generator, and spike recorders
nodes_ex = nest.Create("iaf_psc_delta", NE, params=neuron_params, positions=pos_ex)
nodes_in = nest.Create("iaf_psc_delta", NI, params=neuron_params, positions=pos_ex)
espikes = nest.Create("spike_recorder")
ispikes = nest.Create("spike_recorder")
#Define the Synapses
nest.CopyModel("static_synapse", "excitatory", {"weight": J_ex, "delay": delay})
nest.CopyModel("static_synapse", "inhibitory", {"weight": J_in, "delay": delay})
# Create Connections between populations
nest.Connect(nodes_ex, nodes_ex, conn_params_ex, syn_spec="excitatory")
nest.Connect(nodes_ex, nodes_in, conn_params_ex, syn_spec="excitatory")
nest.Connect(nodes_in, nodes_ex, conn_params_in, "inhibitory")
nest.Connect(nodes_in, nodes_in, conn_params_in, "inhibitory")
noise = nest.Create("poisson_generator", params={"rate": p_rate})
# Connect Noise Generators 
nest.Connect(noise, nodes_ex, syn_spec="excitatory")
nest.Connect(noise, nodes_in, syn_spec="excitatory")
# Connect recorders
nest.Connect(nodes_ex, espikes, syn_spec="excitatory")
nest.Connect(nodes_in, ispikes, syn_spec="excitatory")
ctr, src_id, targets_exc, targets_inh = analyzer.find_src_target_ids(nodes_ex, nodes_in)
# Create Simulator and Connect it
amplitude=160.0
stim_params = {"amplitude": amplitude, "start": 5150.0, "stop": 18150.0}
stimulator = nest.Create("dc_generator", params=stim_params)
# Connect the stimulator to the neuron

nest.Connect(stimulator, nodes_ex[src_id-1])
tt = [i-1 for i in targets_exc]
pp = [i-1 for i in targets_inh]


print('Connectivity_done')
# Start Simulation
print("Simulating")
nest.Simulate(simtime)
# Extract Some Parameters from the Simulation
events_ex = espikes.n_events
events_in = ispikes.n_events
rate_ex = events_ex / simtime * 1000.0 / NE
rate_in = events_in / simtime * 1000.0 / NI
num_synapses_ex = nest.GetDefaults("excitatory")["num_connections"]
num_synapses_in = nest.GetDefaults("inhibitory")["num_connections"]
num_synapses = num_synapses_ex + num_synapses_in
# Extract spikes and plot raster plot
sr1_spikes = espikes.events['senders']
sr1_times = espikes.events['times']
sr2_spikes = ispikes.events['senders']
sr2_times = ispikes.events['times']


# Calculate avg. firing rates of excitatory neurons
avg_firing_exc, spike_times_exc = analyzer.calculate_avg_firing(nodes_ex, simtime, sr1_spikes, sr1_times, 0)
print(avg_firing_exc)
# Calculate avg. firing rates of inhibitory neurons
avg_firing_inh, spike_times_inh = analyzer.calculate_avg_firing(nodes_in, simtime, sr2_spikes, sr2_times, 1)
print(avg_firing_inh)
# Calculate CoV of excitatory neurons
CoV_exc = analyzer.calculate_CoV(spike_times_exc)
# Calculate CoV of inhibitory neurons
CoV_inh = analyzer.calculate_CoV(spike_times_inh)
# Calculating firing rates for both populations
hist_counts_all_exc, bin_centers_exc, avg_hist_counts_exc = analyzer.calculating_firing_rates(targets_exc, src_id, spike_times_exc, 0)
hist_counts_all_inh, bin_centers_inh, avg_hist_counts_inh = analyzer.calculating_firing_rates(targets_inh, src_id, spike_times_inh, 1)
smoothed_data_exc = analyzer.smoothing_kernel(avg_hist_counts_exc)
smoothed_data_inh = analyzer.smoothing_kernel(avg_hist_counts_inh)
print(targets_exc)
print(targets_inh)
#second_exc_neuron_id = targets_exc[10]
second_exc_neuron_id = 1112
#second_exc_neuron_id = 548
nodes_exc_exc_2_away_all, nodes_inh_exc_2_away_all= analyzer.get_nodes_2_nodes_away(ctr, second_exc_neuron_id, targets_exc, nodes_ex, nodes_in, 0)
nodes_exc_exc_2_away = [x for x in nodes_exc_exc_2_away_all if x not in targets_exc]
nodes_inh_exc_2_away = [x for x in nodes_inh_exc_2_away_all if x not in targets_inh]
# Calculating firing rates for both populations
hist_counts_all_exc_exc_second, bin_centers_exc, avg_hist_counts_exc_exc = analyzer.calculating_firing_rates(nodes_exc_exc_2_away, src_id, spike_times_exc, 0)
hist_counts_all_inh_exc_second, bin_centers_inh, avg_hist_counts_inh_exc = analyzer.calculating_firing_rates(nodes_inh_exc_2_away, src_id, spike_times_inh, 1)
#second_inh_neuron_id = targets_inh[5]
#second_inh_neuron_id = 1666
second_inh_neuron_id = 1113
nodes_exc_inh_2_away_all, nodes_inh_inh_2_away_all= analyzer.get_nodes_2_nodes_away(ctr, second_exc_neuron_id, targets_exc, nodes_ex, nodes_in, 0)
nodes_exc_inh_2_away = [x for x in nodes_exc_inh_2_away_all if x not in targets_exc]
nodes_inh_inh_2_away = [x for x in nodes_inh_inh_2_away_all if x not in targets_inh]
# Calculating firing rates for both populations
hist_counts_all_exc_inh_second, bin_centers_exc, avg_hist_counts_exc_inh = analyzer.calculating_firing_rates(nodes_exc_inh_2_away, src_id, spike_times_exc, 0)
hist_counts_all_inh_inh_second, bin_centers_inh, avg_hist_counts_inh_inh = analyzer.calculating_firing_rates(nodes_inh_inh_2_away, src_id, spike_times_inh, 1)
deneme, bin_centers_deneme, avg_deneme = analyzer.calculating_firing_rates([1112, 1113], src_id, spike_times_exc, 0)
if (plotting_flag):
    # Plot of connection of source and target neuron (in our case central neuron ctr)
    m_plot.plot_spatial_connections(nodes_ex, ctr)

    # Plot raster plot
    #m_plot.plot_raster_plot(sr1_spikes, sr1_times, sr2_spikes, sr2_times)
    # Plot CV of excitatory neurons
    m_plot.plot_CV_plot(CoV_exc, 0)
    # Plot CV of inhibitory neurons
    m_plot.plot_CV_plot(CoV_inh, 1)
    # Plot histogram plot of perturbed neuron
    #m_plot.plot_hist_perturbed(spike_times_exc, src_id)
    # Plot average firing rate of excitatory neurons connected to the perturbed neuron
    m_plot.plot_avg_firing_rate(bin_centers_exc, avg_hist_counts_exc, smoothed_data_exc, 0)
    # Plot average firing rate of inhibitory neurons connected to the perturbed neuron
    m_plot.plot_avg_firing_rate(bin_centers_inh, avg_hist_counts_inh, smoothed_data_inh, 1)
    # Plot one example of excitatory neuron connected to the perturbed neuron
    m_plot.plot_example_neuron(bin_centers_exc, deneme[0].T, analyzer.smoothing_kernel(deneme[0].T), 0)
    # Plot one example of inhibitory neuron connected to the perturbed neuron
    m_plot.plot_example_neuron(bin_centers_inh, deneme[1].T, analyzer.smoothing_kernel(deneme[1]).T, 1)




plotting_flag = False
nodes_ex, nodes_in, bin_centers_exc, avg_hist_counts_exc, avg_hist_counts_inh, spike_times_exc, spike_times_inh, avg_hist_counts_exc_exc, avg_hist_counts_inh_exc, avg_hist_counts_exc_inh, avg_hist_counts_inh_inh


avg_hist_exc = avg_hist_counts_exc
avg_hist_inh = avg_hist_counts_inh
avg_hist_exc_diff = np.diff(avg_hist_exc)
avg_hist_inh_diff = np.diff(avg_hist_inh)
avg_hist_exc_max_value = np.max(avg_hist_exc_diff)
avg_hist_exc_max_index = np.argmax(avg_hist_exc_diff)

print("Maximum firing rate at the onset (Exc):", avg_hist_exc[avg_hist_exc_max_index+1])
print("Time value at max value (Exc):", bin_centers_exc[avg_hist_exc_max_index+1])

avg_hist_inh_max_value = np.max(avg_hist_inh_diff)
avg_hist_inh_max_index = np.argmax(avg_hist_inh_diff)

print("Maximum firing rate at the onset (Inh):", avg_hist_inh[avg_hist_inh_max_index+1])
print("Time value at max value (Inh):", bin_centers_exc[avg_hist_inh_max_index+1])



smoothed_data_exc = analyzer.smoothing_kernel(avg_hist_exc)
smoothed_data_inh = analyzer.smoothing_kernel(avg_hist_inh)


# Plot the average firing rate over time
# Excitatory Neurons
m_plot.plot_avg_firing_rate(bin_centers_exc, avg_hist_exc, smoothed_data_exc, 0)
# Inhibitory Neurons
m_plot.plot_avg_firing_rate(bin_centers_exc, avg_hist_inh, smoothed_data_inh, 1)





plt.show()
plt.close()






