# CSM Traffic and Fraud Analyst Skill

A specialized Gemini CLI skill for Digital Marketing Managers and CSMs to analyze traffic logs, detect ad-fraud, and validate campaign starts.

## 🚀 Overview

The **CSM Traffic and Fraud Analyst** skill transforms Gemini CLI into an expert assistant for processing large-scale tracking logs. It automates the detection of common anomalies like Vampire Traffic, IP flooding, and implementation errors (e.g., unreplaced cachebuster macros).

## ✨ Features

- **Automated Fraud Check**: Detects bot-like patterns, data center IPs, and unusual traffic spikes.
- **Campaign Start Validation**: Checks if placements are firing correctly according to their planned start dates and monitors for late delivery.
- **Privacy-Aware Analysis**: Accounts for environmental factors like Apple's ITP and privacy settings when evaluating GUID/Cookie data.
- **Multi-Output Reporting**: 
  - Provides a structured Markdown report directly in the chat.
  - Generates detailed, Excel-ready CSV audit files in a timestamped folder for client presentation.
- **Bilingual Support**: Automatically detects and responds in either German (Du-Anrede) or English.

## 🛠️ Installation

1. Clone or download this repository.
2. In your Gemini CLI session, install the skill:
   ```bash
   gemini skills install path/to/csm-traffic-analyst --scope user
   ```
3. Reload your skills:
   ```bash
   /skills reload
   ```

## 📋 Usage

Simply start a conversation with Gemini CLI and ask for an analysis. The skill will greet you and ask for the specific mode.

### Example Commands:
- *"Führe einen Fraud Check für die Example Corp CSV durch."*
- *"Run a Campaign Start Check for the Sample Airline log."*

### Analysis Modes:
- **Fraud Check**: Focuses on "Vampire Traffic" (01:00-05:00), hourly spikes, User-Agent consistency, and IP concentration.
- **Campaign Start Check**: Focuses on placement activity, delivery timing, and CTR plausibility.

## ⚙️ Technical Details

The skill uses a high-performance Python script (`scripts/analyze_traffic.py`) designed to:
- Handle CSV files exceeding 300MB+ through row-by-row processing.
- Automatically detect headers like `guid`, `ip_address`, `event_time`, etc., across different platform layouts.
- Categorize findings into `[High Risk]`, `[Medium Risk]`, or `[Low Risk]`.

## 📂 Output Structure

Every audit creates a dedicated folder named `Audit_[SourceFile]_[Timestamp]/` containing:
- `01_Summary.csv`: High-level metrics.
- `02_Top_IPs.csv`: Distribution of traffic by IP.
- `03_Frequency_Spikes.csv`: Detailed log of rapid-fire requests (>5/min per IP).
- `04_Implementation_Errors.csv`: Samples of unreplaced macros or technical glitches.

---
*Created for automated traffic quality assurance.*
