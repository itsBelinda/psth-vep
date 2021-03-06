# -*- coding: utf-8 -*-
"""
obp_tests.py
"""
#%% Imports

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
plt.rcParams['axes.grid'] = True


#%% Get the data

# filepath = '../data/data0804/'
# data = np.loadtxt(filepath+'raw.dat')
data = np.loadtxt('../data/sample_07_04.dat')
fs= 1000 # Hz
resolution = 24 # bits
N = len(data)
T = 1/fs
bin_size = fs/N 
y1 = data[:,1]
t = data[:,0] 
faxis = np.linspace(0,fs-bin_size,len(y1))

# convert data
vmin = -1.325
vmax = +1.325
xmax = (2**24 -1)

# Choose data set to work with and convert to voltage
if np.max(y1) > vmax:
    #for raw data: 
    y = ((y1 * (vmax-vmin) / xmax ) + vmin) 
    t = t/1000
else:
    y = y1 #for raw data: ((y1 * (vmax-vmin) / xmax ) + vmin) 



#%% Convert voltage to mmHg


ambientV = 0.710#0.675 # from calibration
mmHg_per_kPa = 7.5006157584566 # from literature
kPa_per_V = 50 # 20mV per 1kPa / 0.02 or * 50 - from sensor datasheet
corrFact = 2.50 # from calibration

ymmHg = (y - ambientV)  * mmHg_per_kPa * kPa_per_V * corrFact 


#%% Filter design
#
## 50 Hz notch filter
#f0 = 48.0
#f1 = 52.0
#sos50 = signal.butter(6, [f0/fs*2,f1/fs*2], 'bandstop', output='sos')
#filt50 = iir_filter.IIR_filter(sos50)

# 5 Hz LP filter
f5 = 10
bLP, aLP = signal.butter(4, f5/fs*2, 'lowpass')
yfLP = signal.lfilter(bLP, aLP, ymmHg)

# 0.5 Hz HP filter
f05 = 0.5
bHP, aHP = signal.butter(4, f05/fs*2, 'highpass')
yfHP = signal.lfilter(bHP, aHP, yfLP)


#%% Filter display

# Plot filter

fig_filters, (h_freq, h_phase) = plt.subplots(2, 1, num='Filter')
#fig_filters.subplots_adjust(hspace=.5)
#fig_filters.suptitle('Averaging and Noise Filter', fontsize=16)

h_freq.set_title('Magnitude Spectrum: ')
h_freq.set_ylabel('Magnitude (dB)')
h_freq.set_xlabel('Frequency (Hz)')
#h_freq.set_ylim(-50, 1)


#b, a = signal.butter(6, [48/fs*2,52/fs*2], 'bandstop')
#wf, hf = signal.freqz(b, a)
#h_freq.plot(wf / np.pi / 2 * fs, (np.abs(hf)), 'b', label='50 Hz')

wf, hf = signal.freqz(bLP, aLP)
h_freq.plot(wf / np.pi / 2 * fs, 20*np.log10(np.abs(hf)), 'r', label='LP 10 Hz')

wf, hf = signal.freqz(bHP, aHP)
h_freq.plot(wf / np.pi / 2 * fs, 20*np.log10(np.abs(hf)), 'b', label='HP 0.5 Hz')
h_freq.legend()
plt.show()

    

wLP, gdLP = signal.group_delay((bLP, aLP))
wHP, gdHP = signal.group_delay((bHP, aHP))

h_phase.plot(wLP / np.pi / 2 * fs, gdLP, 'r', label='LP 10 Hz' )
h_phase.plot(wHP / np.pi / 2 * fs, gdHP, 'b', label='HP 0.5 Hz' )
plt.ylabel('Group delay [samples]')
plt.xlabel('Frequency [Hz]')

# group_delay = -diff(unwrap(angle(hf))) / diff(wf)
#%% Plot full signals
fig_timeSignal, (time_filt, time_LP, time_HP) = plt.subplots(3,1,
                sharex=True,sharey=False,num='mmHg Signal')
fig_timeSignal.subplots_adjust(hspace=0)

time_filt.plot(t,ymmHg, 'b', label='raw')
#time_filt.plot(t2/1000,y2P, 'r', label='raw')
time_LP.plot(t,yfLP, 'r', label='LP')
time_HP.plot(t,yfHP, 'g', label='HP')

time_filt.legend()
time_LP.legend()
time_HP.legend()

fig_timeSignal.suptitle('Blood Pressure', fontsize=20) 
time_filt.set_ylabel('mmHg', fontsize=16)
time_LP.set_ylabel('mmHg', fontsize=16)
time_HP.set_ylabel('detla/mmHg', fontsize=16)
time_HP.set_xlabel('Time (s)', fontsize=16)
time_LP.set_xlim(0, max(t))
time_HP.set_ylim(-3, 3)
plt.get_current_fig_manager().window.showMaximized()
 


#%% Plot frequency spectrum

y_F = np.fft.fft(ymmHg)
y_F_show = abs(y_F)#20 * np.log10(abs(y_F))
yLP_F = np.fft.fft(yfLP)
yLP_F_show = abs(yfLP)#20 * np.log10(abs(yLP_F))
yHP_F = np.fft.fft(yfHP)
yHP_F_show = abs(yfHP)#20 * np.log10(abs(yHP_F))

fig_specSignal, (spec_orig,
                spec_LP,
                spec_HP) = plt.subplots(3,
                                          1,
                                          sharex=True,
                                          sharey=True,
                                          num='Frequency Spectrum')
fig_specSignal.subplots_adjust(hspace=0.05)
fig_specSignal.suptitle(
    'Single-sided Magnitude Spectrum '
    'Frequency Domain (fs=1 kHz)',
    fontsize=12)
plt.get_current_fig_manager().window.showMaximized()


spec_orig.plot(faxis[0:(int(len(y_F) / 2)) + 1],
              y_F_show[0:(int(len(y_F) / 2)) + 1],
              'b',
              label='raw')

spec_LP.plot(faxis[0:(int(len(y_F) / 2)) + 1],
              yLP_F_show[0:(int(len(y_F) / 2)) + 1],
              'r',
              label='LP filtered (10 Hz)')
spec_HP.plot(faxis[0:(int(len(y_F) / 2)) + 1],
              yHP_F_show[0:(int(len(y_F) / 2)) + 1],
              'g',
              label='HP filtered (0.5 Hz)')

spec_orig.legend()
spec_LP.legend()
spec_HP.legend()

spec_orig.set_ylabel('Magnitude (abs)', fontsize=12)
spec_LP.set_ylabel('Magnitude (abs)', fontsize=12)
spec_HP.set_ylabel('Magnitude (abs)', fontsize=12)
spec_HP.set_xlabel('Frequency [Hz]', fontsize=12)
spec_orig.set_ylim(-1, 50)
spec_orig.set_xlim(0, 15)

#%% Print out data

plt.show()
