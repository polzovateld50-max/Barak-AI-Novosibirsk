import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Загружаем данные
df = pd.read_csv('novosibirsk_flats_v47.csv')

# 1. ГИСТОГРАММА ЦЕН
plt.figure(figsize=(10, 6))
sns.histplot(df['Цена_руб'] / 1_000_000, kde=True, color='blue')
plt.title('Distribution of Apartment Prices in Novosibirsk')
plt.xlabel('Price (Million RUB)')
plt.ylabel('Frequency')
plt.savefig('price_dist.png') # Сохранится как картинка для презы
plt.show()

# 2. МАТРИЦА КОРРЕЛЯЦИИ
# Нужно перевести текст в цифры только для этого графика
df_numeric = df.copy()
for col in ['Район', 'Ремонт', 'Материал_стен']:
    df_numeric[col] = pd.factorize(df_numeric[col])[0]

plt.figure(figsize=(12, 10))
mask = np.triu(np.ones_like(df_numeric.corr(), dtype=bool))
sns.heatmap(df_numeric.corr(), mask=mask, annot=True, fmt=".2f", cmap='coolwarm')
plt.title('Correlation Matrix of Features')
plt.savefig('correlation.png') # Сохранится как картинка для презы
plt.show()