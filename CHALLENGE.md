# 🏥 VigiSalud V3.5 — #AIChangesMyGame Challenge

> **Predictive Healthcare Pipeline for Intelligent Hospital Demand Planning.**
> Developed by a Traumatologist leveraging AI to transition from reactive firefighting to systemic workflow orchestration.

---

## 📌 Project Overview

**VigiSalud** is a live predictive analytics platform designed to solve one of healthcare's most critical bottlenecks: predictable yet unmanaged patient flows and hospital saturation.

By integrating Machine Learning models into a robust cloud data architecture, VigiSalud transforms scattered, historical consultation records into real-time, actionable risk alerts segmented by geographical zones.

---

## 📈 The Transformation Framework

### 1. BEFORE AI: The Reactive Status Quo

Hospital demand planning has traditionally been manual, slow, and highly stressful. As a traumatologist on the front lines, I faced daily systemic bottlenecks beyond medical control:

- **Saturated ER Shifts:** Unexpected spikes in consultations left medical teams overwhelmed.
- **Delayed Surgeries:** Inefficient resource allocation led to scheduling backlogs.
- **Volatile Resource Management:** Healthcare centers operated blindly, reacting to crises rather than anticipating them.

*My Role:* I was a **"doer"**, working under immense pressure to adapt to an unpredictable and broken administrative system.

### 2. WITH AI: Architecting the Orchestration

Instead of just adapting to systemic flaws, I chose to lead and orchestrate a technical solution. I designed and deployed **VigiSalud V3.5**, moving completely past basic chat interactions into a sophisticated, automated ML pipeline:

- **The Stack:** Deployed a highly scalable predictive pipeline built on **Azure** and **Supabase**.
- **The Core AI Engine:** Integrated advanced Machine Learning models trained to forecast hospital consultations 7 days in advance.
- **High Precision:** Performance is continuously validated, achieving a strict Mean Absolute Error (**MAE**) of **7.5** and a backtesting MAE of **13.4** on 30 real days.
- **Proactive Intelligence:** Raw healthcare data is automatically processed to trigger **Active Risk Alerts** based on critical demand thresholds.
- **Built from a Moto G56:** The entire pipeline was developed and deployed using only a mobile phone (Termux), proving that high-impact AI solutions don't require expensive hardware.

### 3. AFTER AI: Systemic Healthcare Transformation

The implementation of VigiSalud triggers a fundamental shift in professional mindset and operational output:

- **From Firefighter to Orchestrator:** My role evolved into a strategic architect of healthcare efficiency, using data orchestration to manage complex hospital workflows and drive high-level decision-making.
- **Zone-Based Intelligence:** Hospitals can now filter and visualize predictive trends across distinct regions (**Sur, Centro, Norte**).
- **Equitable Operations:** Administrators can anticipate saturation peaks up to a week in advance, allowing them to balance staff guard shifts, optimize resource allocation, and schedule surgical procedures equitably.
- **Empowered Leadership:** AI transcended simple task acceleration, empowering frontline clinicians to actively design the future of healthcare delivery.

---

## 📱 Platform Interface & Analytics

The application features a fully responsive, dark-mode dashboard tailored for quick clinical operations:

- **Live Metrics:** Real-time counters tracking total `Predicciones` and `Alertas Activas`.
- **Predictive Visualizations:** A 7-day interactive line chart comparing regional consultation forecasts to prevent multi-zone saturation.
- **Data Transparency:** Clean tabular logs detailing precise dates, regional impacts, and automated warnings (⚠️) for immediate triage.

🌐 **Live Dashboard:** [VigiSalud v3.5](https://hectory2k.github.io/Vigisalud-dashboard/)
📂 **Source Code:** [GitHub](https://github.com/hectory2k/vigisalud)

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Cloud Infrastructure** | Azure App Service (Free Tier) |
| **Database & Backend** | Supabase (PostgreSQL) |
| **ML Engine** | Python 3.11 + scikit-learn (Random Forest, TimeSeriesSplit) |
| **Automation** | GitHub Actions (daily 6 AM execution) |
| **Alerts** | Telegram Bot API |
| **Dashboard** | Chart.js + GitHub Pages (dark mode) |
| **Dev Environment** | Termux on Moto G56 (fully mobile-built) |
| **AI Assistant** | Ollama + phi3:mini (on-device clinical reports) |
| **Core Metrics** | MAE: 7.5 \| Backtesting: 13.4 \| 7-Day Forecast Window |

---

## 🧠 Key Features

- **14 predictive variables:** temperature, holidays, weekends, vacations, 1/7/14-day lags, rolling mean, GLP-1 risk factor, sarcopenia proxy
- **Automatic daily execution** at 6 AM via GitHub Actions
- **Telegram alerts** with clinical recommendations when thresholds exceeded
- **On-device AI reports** via Ollama (phi3:mini) without internet
- **100% open source** (MIT License)
- **$0 infrastructure cost**

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| MAE (production) | 7.5 consultations/day |
| Backtesting (30 days) | 13.4 consultations/day |
| Training records | 378 |
| Modeled zones | 3 (Norte, Centro, Sur) |
| Features | 14 |
| Daily automation | 100% |

---

*Submission for the Globant & FIFA World Cup 2026 — #AIChangesMyGame Challenge.*
