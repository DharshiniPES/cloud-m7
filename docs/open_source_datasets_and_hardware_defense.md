# CLOUD-M7: Open-Source Tool Integration, Real Datasets, Hardware Setup & Active Attack Defense

**Department of Computer Science & Engineering | PES University**  
**Course Code:** UE24CS320A (B.Tech Capstone Project, Batch 2024–2028)  
**Project:** CLOUD-M7 (Tier-Adaptive Distributed Forensic Provenance across Edge, Fog, and Cloud)  

---

## 1. Open-Source Ecosystem Integration Architecture

Rather than building low-level operating system loggers from scratch, **CLOUD-M7 leverages proven, production-grade open-source components** for each tier. It serves as the **unifying causal intelligence and correlation layer** that fuses their disjoint telemetry into a single, tamper-evident provenance graph.

```
+---------------------------------------------------------------------------------------------------------+
|                                      CLOUD-M7 UNIFIED PROVENANCE LAYER                                   |
|                                                                                                         |
|   [Novelty 1: Iterative Multi-Root] ──► [Novelty 2: Choke Point Cut-Vertices] ──► [Novelty 3: Bridge]   |
|   [Novelty 4: Active Remediation]   ──► [Novelty 5: MITRE ATT&CK Mapping]     ──► [DuckDB + Parquet]    |
+---------------------------------------------------------------------------------------------------------+
                                                     ▲
                                                     │ Canonical Schema Conversion (E_i)
                        +────────────────────────────┼────────────────────────────+
                        │                            │                            │
            +───────────────────────+   +────────────────────────+   +─────────────────────────+
            |       EDGE TIER       |   |        FOG TIER        |   |       CLOUD TIER        |
            +───────────────────────+   +────────────────────────+   +─────────────────────────+
            | • Linux auditd        |   | • Zeek (Bro) IDS       |   | • CamFlow (LSM W3C)     |
            | • eBPF / Tracee       |   | • Eclipse Mosquitto    |   | • Falco (K8s / Sysdig)  |
            | • Sensor sysfs daemon |   | • nftables / iptables  |   | • AWS CloudTrail Logs   |
            | • MicroPython Agent   |   | • Fluent Bit Collector |   | • DuckDB + Parquet Engine|
            +───────────────────────+   +────────────────────────+   +─────────────────────────+
```

### Why Existing Tools Cannot Solve This Alone (The Disconnect):
1. **Linux `auditd` / `eBPF` (Edge):** Emits raw Linux system calls (`sys_clone`, `execve`, `read`, `write`). It has zero concept of what happens once data leaves through a network socket.
2. **`Zeek` / `Mosquitto` (Fog):** Emits network flow logs (`conn.log`) and MQTT publish topics. It sees packets flying across the wire but has no idea which Linux process PID on the sensor created them.
3. **`Falco` / `CamFlow` (Cloud):** Detects container privilege escalations and database anomalies. It sees unauthorized SQL queries but cannot trace them back to a physical camera in another city.
4. **The CLOUD-M7 Solution:** CLOUD-M7 acts as the **Universal Adapter**. It ingests logs from `auditd`, `Zeek`, `Mosquitto`, and `Falco`, normalizes them into the **Canonical Schema $\mathcal{E}_i$**, correlates them over network 5-tuples and causal timestamps, and executes our **5 Research Novelties**.

---

## 2. Benchmark Security Datasets Utilized in CLOUD-M7

CLOUD-M7 is evaluated on **four authoritative, real-world cybersecurity datasets**, representing each tier of the modern distributed computing paradigm:

| Dataset Name | Originating Organization | Target Computing Tier | Native Format | Cyberattack Scenarios Included | Role in CLOUD-M7 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DARPA OpTC** | Defense Advanced Research Projects Agency | **Cloud & Enterprise Hosts** | JSONL (CAR Format) | APT32/OceanLotus, Lateral Movement, PowerShell Injections, Credential Dumping | Ingested via `OptcAdapter` to reconstruct cloud database exfiltration and host-level persistence. |
| **DARPA TC** (THEIA/Cadets) | DARPA Transparent Computing Program | **Fog Gateway & OS Provenance** | CDM JSON (Common Data Model) | BIND DNS Exploits, Backdoor Shells, Memory Injections, Privilege Escalations | Ingested via `TcAdapter` to trace intermediate socket pivots and process lineage at the Fog tier. |
| **UNSW TON_IoT** | Cyber Range Lab, UNSW Canberra | **Edge IoT Sensors & Telemetry** | CSV Telemetry Tables | Modbus Injections, DoS, MQTT Sensor Tampering, Cross-Site Scripting (XSS) | Ingested via `TonIotAdapter` to benchmark high-frequency sensor readings and physical tamper signals. |
| **Aposemat IoT-23** | Stratosphere Lab / Avast | **Edge & Fog Network Traffic** | Zeek `conn.log` (TSV / CSV) | Mirai Botnet, Torii Malware, Kenjiro, IRC C2 Communication, Port Scans | Ingested via `Iot23Adapter` to reconstruct distributed botnet traffic and compromised IoT gateways. |

### Automatic Detection & Normalization via `DatasetNormalizerFactory`
Users do not need to convert files manually. When any raw dataset file is uploaded via the dashboard:
1. `DatasetNormalizerFactory.auto_detect(file_path)` inspects header signatures, keys, and delimiters.
2. The matching adapter converts each raw record into the **Canonical Forensic Schema**:
   $$\mathcal{E}_i = \langle \text{UUID}_i, \tau_i, \text{Tier}_i, \text{HostID}_i, \text{Type}_i, \mathcal{P}_i, \pi_i \rangle$$
3. A cryptographic **SHA-256 integrity hash** $H_i = \text{SHA256}(\dots)$ is minted for forensic non-repudiation.

---

## 3. Active Attack Defense: How Attacks Work & How to Stop Them

### 3.1 The End-to-End Attack Progression
In a typical distributed multi-tier attack:
1. **Edge Intrusion:** Attacker exploits a vulnerable firmware version on a smart camera (`/usr/local/bin/cam_daemon`) via buffer overflow.
2. **Local Persistence:** Attacker drops a malicious script (`tamper_firmware.sh`) and attempts to access the local Fog router.
3. **Fog Pivot (The Choke Point):** The compromised camera sends lateral SSH/MQTT commands to the local Fog Gateway (`fog-gw-01`, IP: `192.168.1.50`).
4. **Cloud Exfiltration:** From the Fog Gateway, the attacker uses compromised API service tokens to execute `SELECT * FROM patient_records` or exfiltrate databases to a remote C2 server.

---

### 3.2 Stopping Attacks at Each Tier (Novelty 4: Active Remediation)

Forensics should not merely document a breach after damage is done; it must **stop the attack in real time**. CLOUD-M7 achieves this using **Zero Blast-Radius Choke-Point Remediation**:

```
+─────────────────────────────────────────────────────────────────────────────────────────+
| NOVELTY 4 REMEDIATION ENGINE: Remediation Priority Score (RPS)                          |
|                                                                                         |
|                  Containment Efficacy (CE)                                              |
|      RPS  =  ───────────────────────────────────                                        |
|              1.0 + lambda * Collateral Disruption (CDI)                                 |
+─────────────────────────────────────────────────────────────────────────────────────────+
```

#### Tier 1: Stopping the Attack at the Edge
* **Mechanism:** Linux `cgroup v2` Freezer and Process Termination.
* **How it works:** Halts the compromised PID on the Raspberry Pi without rebooting the entire device.
* **Generated Command:**
  ```bash
  # Freeze rogue exploit process without affecting sensor drivers
  echo 1 > /sys/fs/cgroup/pids/isolated_attack/cgroup.freeze
  kill -9 <EXPLOIT_PID>
  chmod 000 /usr/local/bin/tamper_firmware.sh
  ```

#### Tier 2: Stopping the Attack at the Fog Gateway (The Articulation Choke Point)
* **Mechanism:** Kernel `nftables` / `iptables` Stateful Socket Drops + `eBPF XDP` Packet Discard.
* **Why this is the most critical intervention point:** Graph cut-vertex analysis (**Novelty 2**) proves that severing this single bottleneck blocks **100% of attack paths** from all compromised edge sensors to the Cloud.
* **Generated Command:**
  ```bash
  # Instant hardware-accelerated socket severing
  iptables -I FORWARD 1 -s 192.168.1.101 -p tcp --dport 8080 -j DROP
  iptables -I INPUT 1 -s 192.168.1.101 -j REJECT --reject-with icmp-port-unreachable

  # Or via eBPF XDP at the network card driver level (sub-microsecond drop)
  xdp-filter load --dev eth0 --mode skb --ip 192.168.1.101
  ```

#### Tier 3: Stopping the Attack at the Cloud Tier
* **Mechanism:** Dynamic Cloud IAM Role Revocation & Security Group Quarantine.
* **Generated Command:**
  ```bash
  # Instantly revoke leaked AWS STS Session Tokens
  aws iam put-user-policy --user-name fog-sync-service --policy-name RevokeAccess --policy-document file://deny-all.json

  # Isolate Cloud Database Security Group to localhost
  aws ec2 modify-security-group-rules --group-id sg-0123456789abcdef0 --security-group-rule SecurityGroupRuleId=sgr-1,SecurityGroupRule='{IpProtocol="-1",CidrIpv4="127.0.0.1/32"}'
  ```

---

## 4. Step-by-Step Hardware Environment Deployment Guide

Follow these steps to set up and demonstrate a physical hardware testbed or run a zero-cost single-machine emulation.

### Hardware Prerequisites (The Physical Lab Setup)
1. **Edge Node:** 1x Raspberry Pi 4 Model B (or Pi 3B+ / Pi Zero 2W) running **Raspberry Pi OS (64-bit Debian)**.
2. **Fog Gateway:** 1x Laptop or Intel NUC running Linux or Windows (with WSL2).
3. **Cloud Node:** Central Laptop / Cloud VM running the CLOUD-M7 Dashboard and Python Bridge.
4. **Network:** Standard Wi-Fi router or Laptop Mobile Hotspot connecting all devices to subnet `192.168.1.0/24`.

---

### Step 1: Prepare the Fog Gateway Server
On your Laptop (acting as the Fog Gateway):
1. Determine your local IP address:
   ```powershell
   ipconfig   # Look for IPv4 Address under Wireless LAN (e.g. 192.168.1.50)
   ```
2. Start the CLOUD-M7 Fog Ingestion Receiver on port `8080`:
   ```powershell
   cd C:\Users\Dharshini\capstone
   .venv\Scripts\python.exe -c "from cloud_m7.hardware.fog_receiver import FogHardwareGatewayServer; import time; s = FogHardwareGatewayServer(port=8080); s.start_background(); print('[FOG GATEWAY] Listening on port 8080...'); time.sleep(86400)"
   ```

---

### Step 2: Configure the Physical Raspberry Pi (Edge Node)
1. Ensure the Raspberry Pi is connected to the same Wi-Fi network. Note its IP (e.g., `192.168.1.101`).
2. Transfer the probe script to the Pi:
   ```bash
   scp C:\Users\Dharshini\capstone\cloud_m7\hardware\edge_probe.py pi@192.168.1.101:~/
   ```
3. SSH into the Raspberry Pi:
   ```bash
   ssh pi@192.168.1.101
   ```
4. Verify temperature sensor availability:
   ```bash
   cat /sys/class/thermal/thermal_zone0/temp
   # Outputs millidegrees Celsius (e.g. 42800 = 42.8°C)
   ```
5. Launch the live Edge Probe:
   ```bash
   python3 edge_probe.py --fog-url http://192.168.1.50:8080/telemetry --host-id rpi-4-sensor-01 --interval 2.0 --count 50
   ```
   *The probe reads CPU thermals, structures each record into Canonical Schema $\mathcal{E}_i$, signs each tuple with SHA-256 HMAC, and transmits it over HTTP.*

---

### Step 3: Inject an Attack on the Hardware
1. In a second SSH terminal on the Raspberry Pi, simulate an unauthorized firmware injection attempt:
   ```bash
   python3 -c "from edge_probe import generate_hardware_event, transmit_telemetry; e = generate_hardware_event(event_type='Process', action='exec', entity='/usr/local/bin/tamper_firmware.sh', is_attack=True, extra_payload={'exploit': 'CVE-2024-XXXX'}, host_id='rpi-4-sensor-01'); transmit_telemetry('http://192.168.1.50:8080/telemetry', [e])"
   ```

---

### Step 4: Observe Real-Time Detection & Containment in the Dashboard
1. Open the high-speed Node.js Dashboard:
   ```
   http://localhost:3001
   ```
2. Navigate to **Tab 9: Hardware Testbed**.
3. Click **"Trigger Live Hardware Telemetry Cycle"** to interrogate live probe readings.
4. Switch to **Tab 1: Causal Graph**:
   * Observe the Raspberry Pi node turn **Red** (Attack Telemetry).
   * Observe the Fog Gateway turn **Gold (★ CHOKE POINT)**.
5. Switch to **Tab 6: Novelty 4 (Remediation)**:
   * View the synthesized `iptables` / `nftables` isolation policy.
   * Click **"Download Containment Script (.sh)"** to obtain the instant defense script.

---

### Step 5: Zero-Cost Hardware Emulation via Docker (No Physical Pi Needed)
If physical hardware is unavailable during review evaluation, execute:
```bash
docker-compose -f docker-compose.hardware-testbed.yml up --build
```
This boots 3 isolated Linux containers mimicking the identical multi-tier hardware topology:
* `edge-sensor-pi`: Emulates Raspberry Pi 4 CPU sensor and firmware daemon.
* `fog-gateway`: Emulates local router running packet inspection on port `8080`.
* `cloud-server`: Emulates AWS cloud ingestion endpoint.
