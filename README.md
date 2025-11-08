## 🧠 AFIW–ZulfiQode: Agentic Financial, Credit, and Ethical Risk Intelligence Wrapper

### *All Pakistan AI Competition 2025 – Ignite National Technology Fund (NICAT Islamabad)*

---

### 🏅 Competition Badge

<p align="center">
  <img src="https://img.shields.io/badge/🏆%20Finalist-All%20Pakistan%20AI%20Competition%202025-red?style=for-the-badge&logo=google" alt="AI Wrapper Finalist"/>
</p>


---

### ⚙️ Technology Stack Badges

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python" alt="Python" height="60">
  <img src="https://img.shields.io/badge/FastAPI-Framework-green?style=for-the-badge&logo=fastapi" alt="FastAPI" height="60">
  <img src="https://img.shields.io/badge/Grafana-Monitoring-orange?style=for-the-badge&logo=grafana" alt="Grafana" height="60">
  <img src="https://img.shields.io/badge/Prometheus-Metrics-orange?style=for-the-badge&logo=prometheus" alt="Prometheus" height="60">
  <img src="https://img.shields.io/badge/Neo4j-AuraDB-blue?style=for-the-badge&logo=neo4j" alt="Neo4j" height="60">
  <img src="https://img.shields.io/badge/HuggingFace-Deployment-yellow?style=for-the-badge&logo=huggingface" alt="Hugging Face" height="60">
</p>



---

### 📘 Overview

AFIW–ZulfiQode is a next-generation AI-powered system that performs **ethical, credit, and financial risk analysis** through an **Agentic AI architecture** integrated with **econometric modeling**.

It was developed for the **All Pakistan AI Competition 2025**, held at NICAT Islamabad, under the **Ignite National Technology Fund** initiative.

---

### 🧩 Core Architecture

```
Planner → Executor → Verifier → Judge
             ↓
 ✅ Quality Score | ⚠️ Bias Alert | 📊 Confidence Level
```

**Judge Agent** acts as a neutral critic reviewing:

* Summaries for accuracy and hallucination
* Risk scores for justification and bias
* Recommendations for ethical compliance

---

### 🔍 Key Functionalities

* Financial, Credit, and Ethical Risk scoring
* Momentum calculator and 200-day moving average
* PSX API integration (e.g., Hascol data)
* Rumour authentication and tone analysis
* Hallucination detection using LLM vs. Econometric model comparison
* Bias calibration and confidence scoring
* Conversational report generation with voice summary
* Observability dashboard via Prometheus and Grafana

---

### 📊 Observability Metrics

| Metric                       | Description                     |
| ---------------------------- | ------------------------------- |
| `request_latency_seconds`    | Measures API latency            |
| `errors_total`               | Tracks request errors           |
| `hallucination_alerts_total` | Counts hallucination detections |
| `agent_tasks_total`          | Monitors executed agent actions |

---

### 📦 Folder Structure

```
AFIW_ZulfiQode_Final/
├── app/
│   ├── main.py
│   ├── core/
│   ├── agents/
│   ├── data/
│   ├── evaluation/
│   └── models/
├── streamlit_app/
│   └── dashboard.py
├── tests/
│   └── test_app.py
├── requirements.txt
└── README.md
```

---

### ⚡ Run Locally

```bash
uvicorn app.main:app --reload
```

Prometheus → `http://localhost:9090`
Grafana → `http://localhost:3000`
Streamlit → `streamlit run streamlit_app/dashboard.py`

---

### 🧪 Testing

```bash
pytest
```

Output:

```
collected 3 items  
3 passed in X.XXs
```

---

### 🏁 Event Details

| Field            | Information                                                               |
| ---------------- | ------------------------------------------------------------------------- |
| **Event**        | All Pakistan AI Competition 2025                                          |
| **Organizer**    | Ignite – National Technology Fund                                         |
| **Venue**        | NICAT – National Incubation Center for Aerospace Technologies, Rawalpindi |
| **Date**         | 11th November 2025                                                        |
| **Team ID**      | 726                                                                       |
| **Team**         | Mir Global AI Lab                                                         |
| **Project Lead** | Zulfiqar Ali Mir                                                      |

---

### 📞 Contact

📧 **[manager.equity.finance@gmail.com](mailto:manager.equity.finance@gmail.com)**
🌐 **GitHub:** [zulfiqaralimir](https://github.com/zulfiqaralimir)
🏛️ **Organization:** Mir Global AI Lab

