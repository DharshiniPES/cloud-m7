# CLOUD-M7 Physical Hardware Testbed Specification & Setup Guide

This document describes how to deploy and test the **CLOUD-M7** distributed provenance architecture across real, physical hardware devices.

---

## 1. Physical Hardware Architecture

```
  ┌────────────────────────────────┐         ┌─────────────────────────────────┐         ┌───────────────────────────────┐
  │         EDGE DEVICE(S)         │  Wi-Fi  │           FOG GATEWAY           │   WAN   │          CLOUD TIER           │
  │  • Raspberry Pi 4 / 3B+ / Zero │ ──────► │  • Laptop / Intel NUC / Mini-PC │ ──────► │  • Cloud VM / AWS EC2 / Local │
  │  • Sensors: Temp, Vibration    │  MQTT/  │  • Runs eBPF filter & receiver  │  HTTPS  │  • Fusion Engine & Dashboard  │
  │  • Runs: edge_probe.py         │  HTTP   │  • Novelty 2 & 4 Choke Point    │         │  • Parquet & DuckDB Storage   │
  └────────────────────────────────┘         └─────────────────────────────────┘         └───────────────────────────────┘
```

---

## 2. Hardware Bill of Materials (BOM)

| Role | Recommended Hardware | Alternative / Budget Option |
| :--- | :--- | :--- |
| **Edge Node 1** | Raspberry Pi 4 Model B (2GB/4GB) with Raspberry Pi OS (Debian 64-bit) | Raspberry Pi 3B+ or Pi Zero 2W or any Linux SBC |
| **Edge Node 2** | Raspberry Pi 3B+ or secondary Linux SBC | Virtual Machine (VirtualBox / WSL2) or Docker container |
| **Fog Gateway** | Laptop or Mini-PC running Linux (Ubuntu 22.04 LTS / Debian) | Windows PC running WSL2 with eBPF support |
| **Cloud Server** | Cloud Instance (AWS t3.medium / GCP e2-medium) | Primary laptop running the Streamlit Dashboard |

---

## 3. Step-by-Step Hardware Deployment

### Step A: Configure the Fog Gateway
1. On your central laptop / mini-PC, ensure port `8080` is open on your local Wi-Fi:
   ```bash
   # Find your local Fog Gateway IP address (e.g. 192.168.1.50)
   ip a   # on Linux/Mac
   ipconfig   # on Windows
   ```
2. Start the Fog Gateway ingestion server:
   ```powershell
   python -c "from cloud_m7.hardware.fog_receiver import FogHardwareGatewayServer; import time; s = FogHardwareGatewayServer(port=8080); s.start_background(); time.sleep(3600)"
   ```

### Step B: Configure the Physical Raspberry Pi (Edge Node)
1. Copy `cloud_m7/hardware/edge_probe.py` to the Raspberry Pi:
   ```bash
   scp cloud_m7/hardware/edge_probe.py pi@192.168.1.101:~/
   ```
2. SSH into the Raspberry Pi and start telemetry streaming toward the Fog Gateway IP:
   ```bash
   ssh pi@192.168.1.101
   python3 edge_probe.py --fog-url http://192.168.1.50:8080/telemetry --host-id rpi-lab-sensor-01 --interval 1.5 --count 20
   ```
3. The probe will gather live CPU thermal sensor readings from `/sys/class/thermal/thermal_zone0/temp`, package them into Canonical Schema $\mathcal{E}_i$ tuples, sign them with SHA-256 tamper-proof hashes, and transmit them over Wi-Fi.

### Step C: Attack Injection & Containment Demo
During the test, the probe simulates a malicious firmware injection attempt at cycle 5. The Fog Gateway automatically triggers **Novelty 4 (Active Choke-Point Remediation)** and generates an active `eBPF` or `iptables` drop rule to sever the rogue Pi's connection before it touches the Cloud!

---

## 4. Single-Machine Hardware Emulation (Docker Compose)
If physical Raspberry Pi boards are not available in the lab, you can emulate the exact physical multi-tier network topology on a single machine using the provided Docker Compose file:

```bash
docker-compose -f docker-compose.hardware-testbed.yml up --build
```
This spins up 3 isolated network namespaces:
- `edge-sensor-pi`: Simulating the Raspberry Pi 4 edge probe.
- `fog-gateway`: Simulating the local subnet gateway router.
- `cloud-server`: Simulating the cloud analytics endpoint.
