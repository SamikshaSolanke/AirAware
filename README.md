# AirAware
Developing an Algorithm for Air Quality Visualizer and Forecast WebApp to generate granular, real-time, and predictive air quality information

## 1. Introduction
AirAware is a cloud-native platform designed to monitor and forecast **air quality (AQI)** and **weather patterns** across multiple Indian cities. The project provides real-time insights, predictive analytics, and an interactive web interface to help individuals, organizations, and policymakers make data-driven environmental decisions.

---

## 2. Project Overview
- 📡 **Data Ingestion:** Automated ETL pipeline fetching AQI and weather data from multiple public APIs.  
- 📊 **Data Processing & Storage:** Structured storage in AWS RDS (PostgreSQL) and raw data in S3 for durability.  
- 🤖 **Machine Learning Models:**  
  - Time-series forecasting model for predicting AQI trends.  
  - Anomaly detection model for identifying unusual pollution spikes.  
- 🌐 **Web Interface:** Lightweight frontend built using **FastAPI + HTML + CSS**, serving both API endpoints and visual dashboards.  
- ☁️ **Scalability:** Built with serverless components (Lambda, NAT Gateway, S3) to handle **50k+ daily records** and scale automatically with demand.  

---

## 3. Tech Stack & Purpose

| Technology | Purpose |
|------------|---------|
| **AWS Lambda** | Serverless ingestion of AQI/Weather data, ensuring scalability and cost-efficiency. |
| **AWS RDS (PostgreSQL)** | Centralized storage for structured and queryable datasets. |
| **AWS S3** | Durable storage for raw + processed datasets and ML model artifacts. |
| **AWS SageMaker** | Training and deployment of ML models for AQI forecasting and anomaly detection. |
| **Python (FastAPI, pandas, statsmodels, scikit-learn, psycopg2)** | API development, data ingestion, transformation, and model development. |
| **HTML + CSS** | Lightweight frontend for dashboards and user interaction. |

---
