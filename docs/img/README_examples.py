import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import neurokit2 as nk


# =============================================================================
# Simulate physiological signals
# =============================================================================

# Generate synthetic signals
ecg = nk.ecg_simulate(duration=10, heart_rate=70)
rsp = nk.rsp_simulate(duration=10, respiratory_rate=15)
eda = nk.eda_simulate(duration=10, n_scr=3)
emg = nk.emg_simulate(duration=10, n_bursts=2)

# Visualise biosignals
data = pd.DataFrame({"ECG": ecg,
                     "RSP": rsp,
                     "EDA": eda,
                     "EMG": emg})
nk.signal_plot(data, subplots=True)


# Save it
data = pd.DataFrame({"ECG": nk.ecg_simulate(duration=10, heart_rate=70, noise=0),
                     "RSP": nk.rsp_simulate(duration=10, respiratory_rate=15, noise=0),
                     "EDA": nk.eda_simulate(duration=10, n_scr=3, noise=0),
                     "EMG": nk.emg_simulate(duration=10, n_bursts=2, noise=0)})
plot = data.plot(subplots=True, layout=(4, 1), color=['#f44336', "#2196F3", "#9C27B0", "#FF9800"])
fig = plt.gcf()
fig.set_size_inches(10, 6, forward=True)
fig.savefig("README_simulation.png", dpi=300, h_pad=3)

# =============================================================================
# Electrodermal Activity (EDA) processing
# =============================================================================

# Generate 10 seconds of EDA signal (recorded at 250 samples / second) with 2 SCR peaks
eda = nk.eda_simulate(duration=10, sampling_rate=250, n_scr=2, drift=0.1)

# Process it
signals, info = nk.eda_process(eda, sampling_rate=250)

# Visualise the processing
nk.eda_plot(signals, sampling_rate=None)

# Save it
plot = nk.eda_plot(signals, sampling_rate=None)
plot.set_size_inches(10, 6, forward=True)
plot.savefig("README_eda.png", dpi=300, h_pad=3)

# =============================================================================
# Cardiac activity (ECG) processing
# =============================================================================

# Generate 15 seconds of ECG signal (recorded at 250 samples / second)
ecg = nk.ecg_simulate(duration=15, sampling_rate=250, heart_rate=70, random_state=333)

# Process it
signals, info = nk.ecg_process(ecg, sampling_rate=250)

# Visualise the processing
nk.ecg_plot(signals, sampling_rate=250)

# Save it
plot = nk.ecg_plot(signals, sampling_rate=250)
plot.set_size_inches(10, 6, forward=True)
plot.savefig("README_ecg.png", dpi=300, h_pad=3)

# =============================================================================
# Respiration (RSP) processing
# =============================================================================

# Generate one minute of RSP signal (recorded at 250 samples / second)
rsp = nk.rsp_simulate(duration=60, sampling_rate=250, respiratory_rate=15)

# Process it
signals, info = nk.rsp_process(rsp, sampling_rate=250)

# Visualise the processing
nk.rsp_plot(signals, sampling_rate=250)

# Save it
plot = nk.rsp_plot(signals, sampling_rate=250)
plot.set_size_inches(10, 6, forward=True)
plot.savefig("README_rsp.png", dpi=300, h_pad=3)

# =============================================================================
# Electromyography (EMG) processing
# =============================================================================

# Generate 10 seconds of EMG signal (recorded at 250 samples / second)
emg = nk.emg_simulate(duration=10, sampling_rate=250, n_bursts=3)

# Process it
signals, _ = nk.emg_process(emg, sampling_rate=250)

# Visualise the processing
nk.emg_plot(signals, sampling_rate=250)

# Save it
plot = nk.emg_plot(signals, sampling_rate=250)
plot.set_size_inches(10, 6, forward=True)
plot.savefig("README_emg.png", dpi=300, h_pad=3)
