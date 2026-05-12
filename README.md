# Barak-AI-Novosibirsk  Intelligent Real Estate Valuation
![alt text](https://img.shields.io/badge/Python-3.9+-blue.svg)

![alt text](https://img.shields.io/badge/CatBoost-Gradient%20Boosting-yellow.svg)

![alt text](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)

![alt text](https://img.shields.io/badge/Machine%20Learning-Regression-brightgreen.svg)
📌 About the Project
RealtyAI is an end-to-end analytical web service designed to predict the market value of apartments in Novosibirsk, Russia. Empowered by state-of-the-art Machine Learning algorithms, it provides users and investors with highly accurate price estimations based on a complex set of architectural and geospatial parameters.
This project covers the full Data Science lifecycle: from realistic synthetic data generation and feature engineering to model training and cloud deployment.
✨ Key Features
🧠 Advanced ML Engine: Powered by CatBoost Regressor, efficiently handling categorical features (e.g., wall materials, renovation types) without the need for manual One-Hot Encoding.
🏗️ Smart Domain Logic: The data generation and prediction pipeline respects real-world constraints (e.g., specific architectural limits and the absence of subway stations in the Akademgorodok district).
📊 Interactive Analytics: Features dynamic Plotly charts demonstrating how property area impacts the final price, holding other variables constant (Partial Dependence analysis).
🗺️ Geospatial Visualization: Integrated interactive maps showing the selected district.
💼 Investor Insights: Provides dynamic business advice and liquidity assessments based on the apartment's characteristics (floor, renovation, subway proximity).
🛠️ Tech Stack
Machine Learning: CatBoost, Scikit-Learn
Data Manipulation: Pandas, NumPy
Web UI & Visualization: Streamlit, Plotly
Deployment: Streamlit Community Cloud
⚙️ How It Works (Under the Hood)
Data Generation (generate_df.py): A custom algorithm generates a dataset of 50,000 realistic records, incorporating market logic (e.g., first/last floor penalties, material premiums, historical building height limits).
Model Training (mainmodel.py): The data is split and trained using Gradient Boosting. The model undergoes evaluation using standard regression metrics (MAE, RMSE, R² Score) and is serialized using joblib.
Web Application (app.py): A responsive, dark-themed Streamlit dashboard serves as the frontend, allowing users to interact with the trained model in real-time.
Developed as part of an academic Data Science & Applied AI project. © 2024
