import matplotlib.pyplot as plt
import numpy as np

def plot_hist_helper(path):
    # An "interface" to matplotlib.axes.Axes.hist() method
    plt.figure()
    data = np.load(f'{path}/resnpy.npy', allow_pickle=True)
    n, bins, patches = plt.hist(x=data, bins=np.linspace(0, 100, 20))
    plt.title("Test MACE")
    plt.ylim(0, 20000)
    plt.xlabel("MACE")
    plt.ylabel("Frequency")
    plt.savefig(f"{path}/hist.png")
    plt.close()

    plt.figure()
    flow_data = np.load(f'{path}/flownpy.npy', allow_pickle=True)
    max_val = np.max(flow_data)
    n, bins, patches = plt.hist(x=flow_data, bins=np.linspace(0, max_val, 50))
    plt.title(f"Test Flow (Max: {max_val:.2f})")
    # n, bins, patches = plt.hist(x=flow_data, bins=np.linspace(0, 100, 20))
    # plt.title("Test Flow")
    plt.ylim(0, 20000)
    plt.xlabel("Flow")
    plt.ylabel("Frequency")
    plt.savefig(f"{path}/flowhist.png")
    plt.close()

if __name__ == '__main__':
    path = "/home/liuxp/Documents/Projects/STHN_clean/test/local_he/1536_one_stage/satellite_0_thermalmapping_135-2025-12-22_07-07-33"
    plot_hist_helper(path)