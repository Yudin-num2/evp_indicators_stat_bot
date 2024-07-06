import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime as dt

def process_data(df_raw):
    data = []
    current_machine = ""
    current_metric = ""
    
    for index, row in df_raw.iterrows():
        line = ' '.join(row.dropna().astype(str).tolist()).strip()
        if index in range(9):
            continue
        else:
            if "ТПА" in line:
                parts = line.split('|')
                machine_name = parts[0].split()[1] 
                machine_number = parts[1].strip().split('-')[1][1]
                current_machine = f"{machine_name} {machine_number}"
            elif not line or "Достаточное количество" in line:
                continue
            elif any(char.isdigit() for char in line.split()[0]):
                date, time, value = line.split(maxsplit=2)
                data.append([current_machine, current_metric, f"{date} {time}", float(value)])
            else:
                current_metric = line.rsplit(maxsplit=1)[0]

                if current_metric == "Давление системы насос - машина (GreenBox)":
                    current_metric = "Давление GreenBox"
                elif current_metric ==  "Количество работающих гнёзд":
                    current_metric = "Гнёзда"
                elif current_metric ==  "Температура масла":
                    current_metric = "t°C масла"
                elif current_metric ==   "Температура на входе формы":
                    current_metric = "t°C на входе формы"
                elif current_metric ==   "Температура на выходе формы":
                    current_metric = "t°C на выходе формы"
    
    return pd.DataFrame(data, columns=["Machine", "Metric", "Timestamp", "Value"])



def plot_metric_for_machine(machine_name, metric_name):

    file_path = "1.xlsx"
    image_path = "1.jpg"
    df_raw = pd.read_excel(file_path, header=None)
    df = process_data(df_raw)
    print(df)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d.%m.%Y %H:%M:%S')

    subset = df[(df['Machine'] == machine_name) & (df['Metric'] == metric_name)]
    if subset.empty:
        print(f"No data found for machine '{machine_name}' and metric '{metric_name}'.")
        return
    
    plt.figure(figsize=(12,6))
    sns.lineplot(data=subset, x='Timestamp', y='Value')
    plt.title(f"{metric_name} | {machine_name}")
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.savefig(image_path, bbox_inches='tight')
    return image_path



