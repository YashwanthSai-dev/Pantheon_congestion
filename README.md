
# Pantheon Congestion Control Experiment

This repository contains the steps and results of running congestion control protocol experiments using the [Pantheon](https://github.com/StanfordSNR/pantheon) framework. The experiments were conducted for evaluating Cubic, BBR, and Vegas protocols under two network conditions:

1. **High Bandwidth, Low Latency**
2. **Low Bandwidth, High Latency**

##  Setup Environment

###  System Configuration
- OS: Ubuntu-based system
- Python version: Python 2.7.15 (via Conda environment `py2`)
- Tools installed:
  - `git`, `python2`, `pip`, `cmake`, `mahimahi`, `iptables`, `sysctl`

###  Conda Environment Setup
```bash
source ~/miniconda/etc/profile.d/conda.sh
conda activate py2
```

##  Running the Experiment

### Step 1: Clean previous runs
```bash
sudo pkill -9 mm-delay mm-link mm-tunnelserver mm-tunnelclient python2
rm -rf ~/pantheon/tmp/*
rm -rf ~/pantheon/results/low_bw_high_lat/*
```

### Step 2: Launch Pantheon test
```bash
python src/experiments/test.py local \
  --schemes "cubic bbr vegas" \
  --uplink-trace emulated/trace/1mbps_200ms.trace \
  --downlink-trace emulated/trace/1mbps_200ms.trace \
  --data-dir results/low_bw_high_lat
```

> Note: Tunnel connection errors were fixed by manually starting `mm-tunnelserver` and `mm-tunnelclient` in different terminals.

### Step 3: Analyzing Results
```bash
python src/analysis/analyze.py --data-dir results/low_bw_high_lat
```

### Step 4: Generate Plots and Reports
```bash
python src/analysis/plot.py --data-dir results/low_bw_high_lat
python src/analysis/report.py --data-dir results/low_bw_high_lat
```

##  Final Outputs

Generated output is located in the `results/low_bw_high_lat` and `results/high_bw_low_lat` directories. Key files:
- Throughput and delay plots (`*_throughput_run1.png`, `*_delay_run1.png`)
- Log files (`*_run1.log`)
- Summary reports (`pantheon_summary.pdf`, `pantheon_perf.json`, `pantheon_metadata.json`)

##  Fixes and Patches Applied

- **YAML loader fix** in `utils.py`:
  ```python
  yaml.load(config, Loader=yaml.SafeLoader)
  ```
- **Added `subprocess_wrappers.py`** import path fix in `utils.py`
  ```python
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  ```

- **Patched Python 2 compatibility issues**:
  - Replaced `str, unicode` with `basestring` (for Python 2)
  - Replaced `Loader` argument only when `yaml.SafeLoader` is available

##  Completed Tests

-  High Bandwidth Low Latency: `results/high_bw_low_lat`
-  Low Bandwidth High Latency: `results/low_bw_high_lat`

##  Note

If Mahimahi blocks external pings (e.g. 8.8.8.8), use the following to fix:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -F
sudo iptables -F
sudo iptables -t nat -A POSTROUTING -o <interface> -j MASQUERADE
sudo iptables -A FORWARD -i <interface> -o mahimahi -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i mahimahi -o <interface> -j ACCEPT
```

Use `ip route | grep default` to find your correct interface.

---



