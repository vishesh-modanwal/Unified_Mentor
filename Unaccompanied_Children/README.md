# System Capacity & Care Load Analytics for Unaccompanied Children

## 📌 Project Overview

**System Capacity & Care Load Analytics for Unaccompanied Children (UAC)** is a healthcare-system analytics project designed to analyze the movement and care load of unaccompanied children through the U.S. federal care pipeline.

The project analyzes daily operational data covering:

**CBP Custody → Transfer → HHS Care → Discharge**

The primary goal is to transform raw operational counts into meaningful system-level indicators that help identify changes in care load, inflow/outflow imbalance, and periods of potential capacity pressure.

---

## 🎯 Problem Statement

The UAC care system operates as a dynamic pipeline in which children move from CBP custody into HHS care and eventually toward discharge and placement with vetted sponsors.

Although daily operational data is collected, raw counts alone do not provide an integrated view of:

* Total system care load
* Inflow and outflow balance
* Load growth
* Sustained pressure periods
* Periods of relative system relief

This project develops a structured analytical framework to monitor these patterns and support data-driven operational decision-making.

---

## 🎯 Project Objectives

### Primary Objectives

* Quantify daily and cumulative care load across CBP and HHS.
* Analyze the balance between transfers and discharges.
* Identify periods of elevated system pressure.
* Analyze changes in care load over time.

### Secondary Objectives

* Support healthcare staffing and shelter planning.
* Improve operational situational awareness.
* Provide system-level indicators for policymakers and stakeholders.
* Develop an interactive analytics dashboard.
* Translate analytical findings into actionable recommendations.

---

## 📊 Dataset

The project uses daily operational data containing information related to the UAC care pipeline.

### Main Variables

| Variable                                       | Description               |
| ---------------------------------------------- | ------------------------- |
| Date                                           | Reporting date            |
| Children apprehended and placed in CBP custody | Daily intake volume       |
| Children in CBP custody                        | Active CBP care load      |
| Children transferred out of CBP custody        | Flow toward HHS care      |
| Children in HHS Care                           | Active HHS care load      |
| Children discharged from HHS Care              | Children leaving HHS care |

The actual structure, date range, missing values, duplicates, and data-quality characteristics will be documented after the initial dataset audit.

---

## 🔄 Analytical Pipeline

```text
Raw Operational Data
        ↓
Data Ingestion
        ↓
Data Quality Assessment
        ↓
Data Cleaning & Validation
        ↓
Feature Engineering
        ↓
Exploratory Data Analysis
        ↓
KPI Development
        ↓
Trend & Temporal Analysis
        ↓
Pressure & Stress Detection
        ↓
Insights & Recommendations
        ↓
Interactive Streamlit Dashboard
```

---

## 🧮 Key Analytical Metrics

### 1. Total System Load

```text
Total System Load =
CBP Custody + HHS Care
```

Measures the total observed number of children under the combined CBP/HHS care load.

---

### 2. Net Intake Pressure

```text
Net Intake Pressure =
Transfers − Discharges
```

A positive value indicates that transfers into HHS exceed discharges for the reporting period.

A negative value indicates that discharges exceed transfers.

---

### 3. Care Load Growth Rate

Measures the percentage change in system care load relative to the previous reporting period.

```text
Growth Rate =
(Current Load − Previous Load)
/
Previous Load × 100
```

---

### 4. Discharge Offset Ratio

```text
Discharge Offset Ratio =
Discharges / Transfers
```

This measures how much of the incoming transfer volume is offset by discharges.

---

### 5. Rolling Care Load

Rolling averages such as:

* 7-day rolling average
* 14-day rolling average

will be used to distinguish short-term fluctuations from sustained trends.

---

### 6. Pressure Indicator

Potential pressure periods will be identified using combinations of:

* Elevated system load
* Persistent positive net intake pressure
* Rolling load trends
* Sustained duration

The exact thresholds will be determined from the observed dataset rather than arbitrarily imposed before analysis.

---

## 📈 Exploratory Data Analysis

The analysis will investigate:

### Daily Trends

* Daily intake
* CBP custody
* Transfers
* HHS care
* Discharges
* Total system load

### Weekly Trends

* Average load
* Flow volumes
* Net pressure
* Maximum load

### Monthly Trends

* Average system load
* Peak system load
* Transfer volume
* Discharge volume
* Net intake pressure

### Temporal Comparisons

* Yearly trends
* Quarterly trends
* Monthly patterns
* Early vs. late periods

---

## 🚨 Capacity Pressure Analysis

The project does not assume that high observed load automatically means facility overcrowding.

Instead, it identifies **potential system capacity pressure** using observed operational load and flow imbalance.

A typical pressure period may involve:

```text
High System Load
        +
Persistent Positive Net Intake
        +
Sustained Duration
```

Pressure classifications will be defined transparently after examining the actual data distribution.

---

## 🖥️ Streamlit Dashboard

The project will include an interactive Streamlit dashboard with modules such as:

### System Overview

* Total system load
* CBP load
* HHS load
* Net intake pressure
* Growth rate
* Discharge offset ratio

### CBP vs HHS Analysis

* CBP custody trends
* HHS care trends
* Load distribution

### Flow Analysis

* Transfers
* Discharges
* Net intake pressure

### Pressure Analysis

* Rolling averages
* Elevated load periods
* Sustained pressure windows
* Cumulative pressure indicators

### Temporal Analysis

* Daily
* Weekly
* Monthly
* Quarterly
* Yearly views

### User Controls

* Date range selector
* Time granularity selector
* Metric selector
* Rolling-average toggle
* Pressure/stress-period display

---

## 📄 Project Deliverables

The final project will contain:

### 1. Analytical Notebook

Complete Python-based workflow covering:

* Data ingestion
* Data quality
* Cleaning
* Validation
* Feature engineering
* EDA
* KPI analysis
* Pressure detection
* Insights

### 2. Streamlit Dashboard

Interactive web application for system-level care-load monitoring.

### 3. Research Paper

The research paper will document:

* Background
* Problem statement
* Objectives
* Dataset
* Methodology
* Data quality
* Feature engineering
* EDA
* Results
* Pressure analysis
* Recommendations
* Limitations
* Ethical considerations
* Conclusion

### 4. Executive Summary

A concise stakeholder-oriented summary covering:

* Major findings
* Important pressure periods
* Operational implications
* Recommendations

---

## ⚠️ Important Methodological Limitation

The supplied operational dataset does not necessarily contain explicit facility capacity information such as:

* Maximum available beds
* Actual bed capacity
* Staffing capacity
* Facility occupancy limits

Therefore, this project does **not** claim to calculate direct facility capacity utilization.

Instead, it uses observed care load and inflow/outflow imbalance as indicators of **potential system capacity pressure**.

This distinction is important when interpreting the results.

---

## 🔐 Ethical Considerations

Because the project concerns unaccompanied children, analysis should remain focused on aggregated system-level information.

The project should not be used to:

* Identify individual children
* Profile individual children
* Make individual-level decisions
* Infer sensitive personal characteristics
* Make unsupported causal claims

The intended purpose is system-level operational analytics and planning.

---

## 🛠️ Technology Stack

* **Python**
* **Pandas**
* **NumPy**
* **Matplotlib**
* **Seaborn**
* **Plotly**
* **SciPy**
* **Scikit-learn**
* **Streamlit**
* **Jupyter Notebook**

---

## 📁 Project Structure

```text
UAC_System_Capacity_Analytics/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── HHS_Unaccompanied_Alien_Children_Program.csv
│   │
│   ├── processed/
│   │   ├── uac_cleaned.csv
│   │   └── uac_analytics.csv
│   │
│   └── external/
│
├── notebooks/
│   └── UAC_System_Capacity_Analytics.ipynb
│
├── dashboard/
│   └── app.py
│
├── reports/
│   ├── research_paper.md
│   ├── executive_summary.md
│   └── figures/
│
├── outputs/
│   ├── kpi_summary.csv
│   ├── monthly_summary.csv
│   ├── stress_periods.csv
│   └── data_quality_report.csv
│
└── assets/
    ├── dashboard_screenshots/
    └── project_architecture.png
```

---

## 🚀 Installation

Create and activate a virtual environment:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Notebook

Start Jupyter:

```bash
jupyter notebook
```

Open:

```text
notebooks/UAC_System_Capacity_Analytics.ipynb
```

---

## ▶️ Running the Dashboard

After the analytical pipeline is complete:

```bash
streamlit run dashboard/app.py
```

The dashboard will open in the browser.

---

## 📌 Current Project Status

| Phase               | Status     |
| ------------------- | ---------- |
| Project Setup       | 🟢 Started |
| Dataset Audit       | ⏳ Next     |
| Data Cleaning       | ⏳ Pending  |
| Feature Engineering | ⏳ Pending  |
| EDA                 | ⏳ Pending  |
| KPI Development     | ⏳ Pending  |
| Pressure Analysis   | ⏳ Pending  |
| Dashboard           | ⏳ Pending  |
| Research Paper      | ⏳ Pending  |
| Executive Summary   | ⏳ Pending  |
| Final Documentation | ⏳ Pending  |

---

## 🔮 Future Improvements

Potential future extensions include:

* Forecasting future system load
* Anomaly detection
* Automated pressure alerts
* Integration with real-time operational data
* Facility-level capacity data
* Staffing-demand estimation
* Advanced time-series forecasting

---

## 📌 Project Goal

The ultimate goal is to transform raw operational counts into an interpretable, transparent, and decision-oriented analytics framework that helps stakeholders understand UAC care-system load, flow imbalance, and potential periods of sustained pressure.

---

**Project:** System Capacity & Care Load Analytics for Unaccompanied Children

**Domain:** Healthcare Analytics / Public Sector Analytics / Time-Series Analysis / Decision Support
