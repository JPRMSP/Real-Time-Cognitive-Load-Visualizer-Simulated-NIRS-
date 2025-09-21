import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math  # ✅ Added

# ------------------------------------------------------
# Streamlit App Configuration
# ------------------------------------------------------
st.set_page_config(page_title="Cerebral Info Processing & NIRS", layout="wide")

st.title("🧠 Real-Time Cognitive Load Visualizer (Simulated NIRS)")
st.write("""
This demo simulates **cerebral information processing** and its relation with **Near Infrared Spectroscopy (NIRS)**.  
Choose a task to see how **oxygenated (Oxy-Hb)** and **deoxygenated (Deoxy-Hb)** hemoglobin signals behave in real time.
""")

# ------------------------------------------------------
# Sidebar Controls
# ------------------------------------------------------
st.sidebar.header("Simulation Controls")
task = st.sidebar.radio(
    "Choose a stimulus:",
    ["Resting State", "Visual Task", "Language Task", "Motor Task", "Cognitive Test"]
)

duration = st.sidebar.slider("Duration (seconds)", 5, 30, 15)
noise_level = st.sidebar.slider("Noise Level", 0.0, 0.5, 0.1)

start = st.sidebar.button("Start Simulation")

# ------------------------------------------------------
# Hemodynamic Response Function (HRF)
# ------------------------------------------------------
def hrf(t, peak=6, under=16, ratio=0.166):
    """Approximate Hemodynamic Response Function (HRF)"""
    return (
        (t ** peak * np.exp(-t)) / math.factorial(peak)
        - ratio * (t ** under * np.exp(-t)) / math.factorial(under)
    )

# ------------------------------------------------------
# Task Parameters
# ------------------------------------------------------
task_params = {
    "Resting State": {"amp": 0.2, "freq": 0.1},
    "Visual Task": {"amp": 1.0, "freq": 0.25},
    "Language Task": {"amp": 0.8, "freq": 0.2},
    "Motor Task": {"amp": 1.2, "freq": 0.3},
    "Cognitive Test": {"amp": 1.5, "freq": 0.35},
}

# ------------------------------------------------------
# Simulation
# ------------------------------------------------------
if start:
    st.write(f"### Simulating: {task} for {duration} seconds")

    # Time vector
    t = np.linspace(0, duration, duration * 20)  # 20 Hz sampling
    params = task_params[task]

    # HRF + sinusoidal modulation
    base_hrf = hrf(np.linspace(0, 30, len(t)))
    signal = (
        params["amp"] * np.sin(2 * np.pi * params["freq"] * t)
        + np.convolve(np.ones(5) / 5, base_hrf, mode="same")
    )
    signal += noise_level * np.random.randn(len(t))

    # Simulated Oxy-Hb and Deoxy-Hb
    oxy = signal + 0.5 * np.sin(0.1 * np.pi * t)
    deoxy = -0.6 * signal + 0.2 * np.sin(0.1 * np.pi * t)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, oxy, label="Oxy-Hb (Oxygenated Hemoglobin)", color="red")
    ax.plot(t, deoxy, label="Deoxy-Hb (Deoxygenated Hemoglobin)", color="blue")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Concentration Change (a.u.)")
    ax.set_title(f"NIRS-like Signal: {task}")
    ax.legend()
    st.pyplot(fig)

    # Cerebral oxygenation index
    coi = np.mean(oxy) / (np.mean(oxy) + abs(np.mean(deoxy)) + 1e-5)
    st.metric("Cerebral Oxygenation Index", f"{coi*100:.2f}%")

    # Interpretation
    if coi > 0.55:
        st.success("🟢 Brain highly oxygenated → Active processing")
    elif coi > 0.45:
        st.warning("🟡 Moderate oxygenation → Balanced state")
    else:
        st.error("🔴 Low oxygenation → Fatigue / reduced activity")
else:
    st.info("👈 Choose a task and press **Start Simulation** to begin.")
