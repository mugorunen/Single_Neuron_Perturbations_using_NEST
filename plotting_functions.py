import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize, LogNorm
from matplotlib.cm import ScalarMappable
import nest

# This script contains functions to plot different behaviors
class PlottingFuncs:
    # Initialization of the values
    def __init__(self, N_neurons, simtime, bin_width, CE, CI):
        self.N_neurons = N_neurons
        self.simtime = simtime
        self.bin_width = bin_width
        self.CE = CE
        self.CI = CI

    #Plotting which neurons to connecting to which other neurons
    def plot_spatial_connections(self, nodes_ex, ctr):
        fig1 = nest.PlotLayer(nodes_ex)
        nest.PlotTargets(
            ctr,
            nodes_ex,
            fig=fig1,
            src_size=250,
            tgt_color="red",
            tgt_size=20,
            mask_color="red",
            probability_cmap="Greens",
        )

        plt.xticks(np.arange(-1.5, 1.55, 0.5))
        plt.yticks(np.arange(-1.5, 1.55, 0.5))
        plt.grid(True)
        plt.axis([-2.0, 2.0, -2.0, 2.0])
        plt.title("Connection targets")

        # Plot Source Neurons of the Center Neuron
        fig2 = nest.PlotLayer(nodes_ex)
        nest.PlotSources(
            nodes_ex,
            ctr,
            fig=fig2,
            src_size=50,
            src_color='green',
            tgt_size=20,
            mask_color="red",
            probability_cmap="Greens",
        )

        plt.xticks(np.arange(-1.5, 1.55, 0.5))
        plt.yticks(np.arange(-1.5, 1.55, 0.5))
        plt.grid(True)
        plt.axis([-2.0, 2.0, -2.0, 2.0])
        plt.title("Connection targets")

    # PLotting of the connectivity matrix
    def plot_connectivity(self, connectivity_matrix):
        # Normalize the values for colormap mapping
        # Plot the array using imshow
        plt.figure()
        plt.imshow(connectivity_matrix, cmap='viridis', interpolation='nearest')
        # Add color scale bar with legend
        colorbar = plt.colorbar()
        colorbar.set_label('Value')

    # Plotting the raster plot
    def plot_raster_plot(self, sr1_spikes, sr1_times, sr2_spikes, sr2_times):
        plt.figure()

        plt.plot(sr1_times, sr1_spikes,
                '.', markersize=1, color='blue', label='Exc')
        plt.plot(sr2_times, sr2_spikes,
                '.', markersize=1, color='orange', label='Inh')
        plt.xlabel('time (ms)')
        plt.ylabel('neuron id')
        plt.legend()

    def plot_CV_plot(self, CoV, neuron_type):
        # Create a histogram plot for excitatory neurons
        plt.figure()
        plt.hist(CoV, bins=30, edgecolor='black')  # Adjust the number of bins as needed
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        if neuron_type==0:
            plt.title("CV of Excitatory Neurons")
        else:
            plt.title("CV of Inhibitory Neurons")


    def plot_hist_perturbed(self, spike_times_exc, src_id):
        spike_times_exc = np.array(spike_times_exc)
        #Plot the histogram of the Perturbed Neuron
        plt.figure()
        # Create a histogram plot for excitatory neurons
        plt.hist(spike_times_exc[src_id-1], bins=int(self.simtime/self.bin_width), edgecolor='black')  # Adjust the number of bins as needed
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title("Histogram of the Stimulated Neuron")

    def plot_avg_firing_rate(self, bin_centers, avg_hist_counts, average_firing_rate, neuron_type):
        plt.figure()
        plt.plot(bin_centers, avg_hist_counts)
        #plt.legend(targets_exc)
        if neuron_type==0:
            plt.title("Avg. Firing Rate of Excitatory Neurons (CE= {}, CI= {})".format(self.CE, self.CI))
        else:
            plt.title("Avg. Firing Rate of Inhibitory Neurons (CE= {}, CI= {})".format(self.CE, self.CI))
        plt.xlabel('Time')
        plt.ylabel('Firing Rate (Hz)')

        # Create a time axis based on the first spiketrain's duration
        time_axis = np.linspace(0, self.simtime, len(average_firing_rate))
    
        # Plot the average firing rate over time
        plt.plot(bin_centers, average_firing_rate, color='blue')
        plt.grid(True)

    # Plot the activity of just one neuron
    def plot_example_neuron(self, bin_centers, hist_count_one_neuron, firing_rates_smoothed_one_neuron, neuron_type):
        plt.figure()
        plt.plot(bin_centers, hist_count_one_neuron)

        if neuron_type==0:
            plt.title("One Excitatory Neuron (CE= {}, CI= {})".format(self.CE, self.CI))
        else:
            plt.title("One Inhibitory Neuron (CE= {}, CI= {})".format(self.CE, self.CI))
        plt.xlabel('Time')
        plt.ylabel('Firing Rate (Hz)')

        # Create a time axis based on the first spiketrain's duration
        time_axis = np.linspace(0, self.simtime, len(firing_rates_smoothed_one_neuron))

        # Plot the average firing rate over time
        plt.plot(time_axis, firing_rates_smoothed_one_neuron, color='blue')
        plt.grid(True)

    def plotting_across_trials(self, bin_centers, smoothed_data, avg_hist, neuron_type):
        plt.figure()
        plt.plot(bin_centers, smoothed_data, color='blue')
        plt.plot(bin_centers, avg_hist)
        if neuron_type==0:
            plt.title('Average of Excitatory Neurons Across Trials')
        else:
            plt.title('Average of Inhibitory Neurons Across Trials')
        plt.grid(True)


        

