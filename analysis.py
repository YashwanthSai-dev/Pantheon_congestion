import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def parse_mm_log(path):
    times, sizes = [], []
    current_time = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '+' in line:
                try:
                    delta_t, size = map(int, line.split('+'))
                    current_time += delta_t
                    times.append(current_time / 1e6)
                    sizes.append(size)
                except:
                    continue
            else:
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    t_us, b = map(int, parts)
                    times.append(t_us / 1e6)
                    sizes.append(b)
                except:
                    continue
    if not times:
        return pd.Series(dtype=float)
    df = pd.DataFrame({'time': times, 'bytes': sizes})
    df.set_index('time', inplace=True)
    tp = pd.Series(df['bytes']).rolling(window=20).sum() * 8 / 1e6
    return tp.dropna()

def parse_events(path):
    times = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                t_us = int(line.split()[0])
                times.append(t_us / 1e6)
            except:
                continue
    return times

def compute_rtt_loss(data_log, ack_log):
    data_times = parse_events(data_log)
    ack_times = parse_events(ack_log)
    if not data_times:
        return np.nan, np.nan, np.nan
    if not ack_times:
        return np.nan, np.nan, 1.0
    n = min(len(data_times), len(ack_times))
    rtts = np.array(ack_times[:n]) - np.array(data_times[:n])
    avg_rtt = float(np.mean(rtts))
    p95_rtt = float(np.percentile(rtts, 95))
    loss = (len(data_times) - len(ack_times)) / float(len(data_times))
    return avg_rtt, p95_rtt, loss

schemes = ['cubic', 'bbr', 'vegas']
profiles = {
    'high_bw_low_lat': '50mbps_10ms',
    'low_bw_high_lat': '1mbps_200ms'
}

for prof in profiles:
    base = "results/{}".format(prof)

    # 1) Throughput plot
    plt.figure()
    for s in schemes:
        tp = parse_mm_log(os.path.join(base, "{}_mm_datalink_run1.log".format(s)))
        plt.plot(tp.index, tp.values, label=s)
    plt.title("Throughput over time ({})".format(prof))
    plt.xlabel("Time (s)")
    plt.ylabel("Mbps")
    plt.legend()
    plt.savefig("{}_throughput.png".format(prof))

    # 2) RTT + loss
    stats = []
    for s in schemes:
        avg, p95, loss = compute_rtt_loss(
            os.path.join(base, "{}_mm_datalink_run1.log".format(s)),
            os.path.join(base, "{}_mm_acklink_run1.log".format(s))
        )
        stats.append((s, avg, p95, loss))
    df = pd.DataFrame(stats, columns=['scheme', 'avg_rtt', 'p95_rtt', 'loss'])
    df.to_csv("{}_stats.csv".format(prof), index=False)
    print("\nStats for {}:\n".format(prof), df)

    # 3) Scatter: throughput vs RTT
    plt.figure()
    avg_tput = [parse_mm_log(os.path.join(base, "{}_mm_datalink_run1.log".format(s))).mean() for s in schemes]
    plt.scatter(df['avg_rtt'], avg_tput)
    for i, s in enumerate(schemes):
        plt.text(df['avg_rtt'][i], avg_tput[i], s)
    plt.xlabel("Avg RTT (s)")
    plt.ylabel("Avg Throughput (Mbps)")
    plt.title("Throughput vs RTT ({})".format(prof))
    plt.savefig("{}_scatter.png".format(prof))

    # 4) Loss over time (optional/bonus)
    plt.figure()
    for s in schemes:
        sent = parse_mm_log(os.path.join(base, "{}_mm_datalink_run1.log".format(s)))
        ack = parse_mm_log(os.path.join(base, "{}_mm_acklink_run1.log".format(s)))
        window = 20
        sent_cnt = sent.rolling(window).sum()
        ack_cnt = ack.rolling(window).sum()
        loss_rate = ((sent_cnt - ack_cnt) / sent_cnt).fillna(0) * 100
        plt.plot(loss_rate.index, loss_rate.values, label=s)
    plt.title("Loss rate over time ({})".format(prof))
    plt.xlabel("Time (s)")
    plt.ylabel("Loss rate (%)")
    plt.legend()
    plt.savefig("{}_loss.png".format(prof))

print("Analysis complete.")
