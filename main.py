'''
    File name:      main.py
    Author:         Spyros Acheimastos
    Date created:   18/10/2021
    Last modified:  10/11/2021
    Python version: 3.7.7
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

if not os.path.exists('plots_Cp'):
    os.makedirs('plots_Cp')


def save_plot(save_name):
    plt.savefig(f'plots_Cp/{save_name}.png', dpi=100, transparent=False, bbox_inches='tight')
    # plt.savefig(f'Plots_tiff/{save_name}.tiff', dpi=100, transparent=False, bbox_inches='tight')


def read_fluent_xy(file_name, x, y):
    data = pd.read_csv(file_name, names=[x, y], header=None, delimiter = '\t',
                       skiprows=4, skipfooter=1, engine='python', dtype=np.float32)
    return data.sort_values(by=[x])


def read_airfoil(file_name, y_axis):
    data = pd.read_csv(file_name, delimiter = ',', dtype=np.float32)
    x_scale = 0.001
    # Crude shortcut instead of making two y-axes 
    y_scale = (y_axis[0] - y_axis[1]) * x_scale * 1.1
    data['X'] *= x_scale
    data['Y'] *= y_scale    
    return data
    
    
def unitless(data, x, y):
    x_min = data[x].iloc[0]
    x_max = data[x].iloc[-1]
    length = x_max - x_min
    data[x] = (data[x] - x_min)/length
    return data

def keys_and_titles():
    data_keys = []
    plot_titles = {}
    for phase_a, phase_b in zip(('p1', 'p2'), ('One-Phase', 'Two-Phase')):
        for aoa in ('0', '20'):
            for loc in ('25', '75'):
                data_keys.append(f'cp_{phase_a}_a{aoa}_{loc}')
                plot_titles[data_keys[-1]] = f'$C_{{P}}$ at {loc}% of the wing ({phase_b}, $α={aoa}^ο$)'
    return data_keys, plot_titles
    
    
def main():
    # Inputs
    colors = ['black', 'royalblue', 'forestgreen', 'crimson']
    legends = ['Airfoil', 'Unstr.', 'Mosaic', 'Struct.']  
    airfoil_file = 'data/airfoil/eppler_420.csv'
    y_axis = [-1.6, 1.1]
    x, y = 'x', 'cp'
    
    # Parameters for plots
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['font.size'] = 16
    plt.rcParams['lines.markersize'] = 3
    plt.rcParams['lines.markeredgewidth'] = 2.5
    # plt.rcParams['lines.markeredgecolor'] = 'k'
    # plt.rcdefaults()
       
    data_keys, plot_titles = keys_and_titles()
    airfoil_data = read_airfoil(airfoil_file, y_axis)
    
    # Create the main dictionaries
    airfoil = {'color': colors[0], 'legend': legends[0], 'X': airfoil_data['X'], 'Y': airfoil_data['Y']}
    unstr = {'color': colors[1], 'legend': legends[1]}
    mosaic = {'color': colors[2], 'legend': legends[2]}
    struct = {'color': colors[3], 'legend': legends[3]}
    
    for data_key in data_keys:
        # Read .xy Files
        unstr[data_key] = read_fluent_xy(f'data/unstructured/{data_key}.xy', x, y)
        mosaic[data_key] = read_fluent_xy(f'data/mosaic/{data_key}.xy', x, y)
        struct[data_key] = read_fluent_xy(f'data/structured/{data_key}.xy', x, y)

        # Make x-axis unitless (x/c)
        unstr[data_key] = unitless(unstr[data_key], x, y)
        mosaic[data_key] = unitless(mosaic[data_key], x, y)
        struct[data_key] = unitless(struct[data_key], x, y)

    # Make all the Plots
    for data_key in data_keys:
        plt.figure(figsize=(7,6), dpi=100)
        
        plt.plot(airfoil['X'], airfoil['Y'], c = airfoil['color'], label=airfoil['legend'], zorder=0) 
        plt.scatter(unstr[data_key][x], unstr[data_key][y], c = unstr['color'], label = unstr['legend'])
        plt.scatter(mosaic[data_key][x], mosaic[data_key][y], c = mosaic['color'], label = mosaic['legend'])
        plt.scatter(struct[data_key][x], struct[data_key][y], c = struct['color'], label = struct['legend'])
    
        plt.title(plot_titles[data_key])
        plt.xlabel('$x/c$ (-)')
        plt.ylabel('$C_{P}$ (-)')
        plt.ylim(y_axis)
        plt.tick_params(axis='both',bottom=True, top=True, left=True, right=True, direction='in', which='major')
        plt.grid(linestyle='--', linewidth=1, alpha=0.8)
        plt.gca().invert_yaxis()   
        plt.legend(loc='upper right')
        plt.show
    
        save_plot(data_key)
       

if __name__ == "__main__":
    main()