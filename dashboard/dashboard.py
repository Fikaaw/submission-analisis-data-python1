import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime

sns.set(style='whitegrid')
plt.style.use('default')
# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_casual_register_df(df):
    casual_year_df = df.groupby("yr")["casual"].sum().reset_index()
    casual_year_df.columns = ["yr", "total_casual"]
    reg_year_df = df.groupby("yr")["registered"].sum().reset_index()
    reg_year_df.columns = ["yr", "total_registered"]  
    casual_register_df = casual_year_df.merge(reg_year_df, on="yr")
    return casual_register_df

def create_monthly_df(df):
    monthly_df = df.groupby(by=["mnth","yr"]).agg({
        "cnt": "sum"
    }).reset_index() 
    return monthly_df

def create_hourly_df(df):
    hourly_df = df.groupby(by=["hr","yr"]).agg({
        "cnt": "sum"
    }).reset_index() 
    return hourly_df

def create_hourly_weekday_heatmap(df):
    heatmap_df = df.groupby(['weekday', 'hr'])['cnt'].mean().reset_index()
    heatmap_df = heatmap_df.pivot(index='weekday', columns='hr', values='cnt')
    return heatmap_df

def create_byholiday_df(df):
    holiday_df = df.groupby(by=["holiday","yr"]).agg({
        "cnt": "sum"
    }).reset_index() 
    return holiday_df

def create_byworkingday_df(df):
    workingday_df = df.groupby(by=["workingday","yr"]).agg({
        "cnt": "sum"
    }).reset_index() 
    return workingday_df

def create_byseason_df(df):
    season_df = df.groupby(by=["season","yr"]).agg({
        "cnt": "sum"
    }).reset_index() 
    return season_df

def create_byweather_df(df):
    weather_df = df.groupby(by=["weathersit","yr"]).agg({
        "cnt": "sum"
    }).reset_index() 
    return weather_df

# Load cleaned data
day_clean_df = pd.read_csv("dashboard/bike_day.csv")
hour_df = pd.read_csv("dataset/hour.csv")

# Filter data
day_clean_df["dteday"] = pd.to_datetime(day_clean_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
min_date = day_clean_df["dteday"].min()
max_date = day_clean_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo 
    st.image("dashboard/logo.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_clean_df[(day_clean_df["dteday"] >= str(start_date)) & 
                       (day_clean_df["dteday"] <= str(end_date))]

second_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                       (hour_df["dteday"] <= str(end_date))]


# # Menyiapkan berbagai dataframe
casual_register_df = create_casual_register_df(main_df)
monthly_df = create_monthly_df(main_df)
hourly_df = create_hourly_df(second_df)
holiday_df = create_byholiday_df(main_df)
workingday_df = create_byworkingday_df(main_df)
season_df = create_byseason_df(main_df)
weather_df = create_byweather_df(main_df)
hourly_df = hourly_df.replace({
    "yr": {0: 2011, 1: 2012}
})

st.header('Bike Sharing Dashboard 🚵')
# Menampilkan Bagaimana tren terakhir terkait jumlah pengguna baru dengan pengguna casual dalam beberapa tahun terakhir
st.subheader('Total Casual Vs Total Registered')
fig, ax = plt.subplots()
index = casual_register_df["yr"]
bar_width = 0.35
p1 = ax.bar(index, casual_register_df["total_casual"], bar_width, label="Total Casual", color="b")
p2 = ax.bar(index + bar_width, casual_register_df["total_registered"], bar_width, label="Total Registered", color="g")
ax.set_xlabel("Year")
ax.set_ylabel("Jumlah")
ax.set_title("Total Casual vs Total Registered by Year")
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(casual_register_df["yr"])
ax.legend()
for p in p1 + p2:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2., height + 1, str(int(height)), ha="center")
plt.tight_layout()
st.pyplot(plt.gcf())


# pola yang terjadi pada jumlah total penyewaan sepeda berdasarkan bulan 
st.subheader("Pola Total Penyewaan Sepeda Berdasarkan Bulan")
fig, ax = plt.subplots()
sns.lineplot(data=monthly_df, x="mnth", y="cnt", hue="yr", palette="pastel", marker="o")
plt.xlabel("Urutan Bulan")
plt.ylabel("Jumlah")
plt.title("Jumlah total sepeda yang disewakan berdasarkan Bulan dan tahun")
plt.legend(title="Tahun", loc="upper right")  
plt.xticks(ticks=monthly_df["mnth"], labels=monthly_df["mnth"])
plt.tight_layout()
for line in ax.lines:
    for x, y in zip(line.get_xdata(), line.get_ydata()):
        plt.text(x, y, '{:.0f}'.format(y), color="white", ha="center", fontsize=8).set_backgroundcolor("gray")
st.pyplot(fig)

# pola yang terjadi pada jumlah total penyewaan sepeda berdasarkan Jam
st.subheader("Pola Total Penyewaan Sepeda Berdasarkan Jam")
fig, ax = plt.subplots()
sns.lineplot(data=hourly_df, x="hr", y="cnt", hue="yr", palette="pastel", marker="o")
plt.xlabel("Urutan Jam")
plt.ylabel("Jumlah")
plt.title("Jumlah total sepeda yang disewakan berdasarkan Jam dan tahun")
plt.legend(title="Tahun", loc="upper right")  
plt.xticks(ticks=hourly_df["hr"], labels=hourly_df["hr"])
plt.tight_layout()
st.pyplot(fig)

# heatmap untuk Pola Jam vs Hari
st.subheader("Pola Penyewaan: Jam vs Hari")
heatmap_data = create_hourly_weekday_heatmap(second_df)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, 
            cmap='YlOrRd', 
            annot=True, 
            fmt='.0f', 
            cbar_kws={'label': 'Jumlah Rata-rata Penyewaan'})

plt.title('Rata-rata Penyewaan Berdasarkan Jam dan Hari')
plt.xlabel('Jam')
plt.ylabel('Hari')
st.pyplot(fig)

# Tambahkan keterangan
with st.expander('Keterangan Hari'):
    st.write("""
    - 0: Minggu
    - 1: Senin
    - 2: Selasa
    - 3: Rabu
    - 4: Kamis
    - 5: Jumat
    - 6: Sabtu
    """)

# pola yang terjadi pada jumlah total penyewaan sepeda berdasarkan Hari Libur dan Hari Kerja
st.subheader("Total Penyewaan Sepeda Berdasarkan Hari Libur dan Hari Kerja")
col_holiday, col_workingday = st.columns([1, 1])
with col_holiday:
    fig, ax = plt.subplots()
    sns.barplot(data=holiday_df, x="holiday", y="cnt", hue="yr", palette="viridis")
    plt.ylabel("Jumlah")
    plt.title("Jumlah total sepeda yang disewakan berdasarkan hari Libur")
    plt.legend(title="Tahun", loc="upper right")  
    for container in ax.containers:
        ax.bar_label(container, fontsize=8, color='white', weight='bold', label_type='edge')
    plt.tight_layout()
    st.pyplot(fig)
with col_workingday:
    fig, ax = plt.subplots()
    sns.barplot(data=workingday_df, x="workingday", y="cnt", hue="yr", palette="viridis")
    plt.ylabel("Jumlah")
    plt.title("Jumlah total sepeda yang disewakan berdasarkan hari Kerja")
    plt.legend(title="Tahun", loc="upper right")  
    for container in ax.containers:
        ax.bar_label(container, fontsize=8, color='white', weight='bold', label_type='edge')
    plt.tight_layout()
    st.pyplot(fig)
        
# pola yang terjadi pada jumlah total penyewaan sepeda berdasarkan Musim
st.subheader("Total Penyewaan Sepeda Berdasarkan Musim")
fig, ax = plt.subplots()
sns.barplot(data=season_df, x="season", y="cnt", hue="yr", palette="viridis")
plt.ylabel("Jumlah")
plt.title("Jumlah total sepeda yang disewakan berdasarkan Musim")
plt.legend(title="Tahun", loc="upper right")  
for container in ax.containers:
    ax.bar_label(container, fontsize=8, color='white', weight='bold', label_type='edge')
plt.tight_layout()
st.pyplot(fig)
with st.expander('Keterangan'):
    st.write(
        """
        `Winter`: Musim Dingin  
        `Summer`: Musim Panas  
        `Springer`: Musim Semi  
        `Fall`: Musim Gugur
        """
    )
    
# Distribusi Penyewaan Berdasarkan Musim
st.subheader("Distribusi Penyewaan Berdasarkan Musim")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    season_dist = main_df.groupby('season')['cnt'].sum()
    plt.pie(season_dist, labels=['Winter', 'Spring', 'Summer', 'Fall'],
            autopct='%1.1f%%', colors=sns.color_palette("husl", 4))
    plt.title('Distribusi Penyewaan per Musim')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    weather_dist = main_df.groupby('weathersit')['cnt'].sum()
    plt.pie(weather_dist, labels=['Clear', 'Mist', 'Light Rain/Snow'],
            autopct='%1.1f%%', colors=sns.color_palette("husl", 3))
    plt.title('Distribusi Penyewaan per Kondisi Cuaca')
    st.pyplot(fig)

# pola yang terjadi pada jumlah total penyewaan sepeda berdasarkan Cuaca
st.subheader("Total Penyewaan Sepeda Berdasarkan Cuaca")
fig, ax = plt.subplots()
sns.barplot(data=weather_df, x="weathersit", y="cnt", hue="yr", palette="viridis")
plt.ylabel("Jumlah")
plt.title("Jumlah total sepeda yang disewakan berdasarkan Cuaca")
plt.legend(title="Tahun", loc="upper right")  
for container in ax.containers:
    ax.bar_label(container, fontsize=8, color='white', weight='bold', label_type='edge')
plt.tight_layout()
st.pyplot(fig)
with st.expander('Keterangan'):
    st.write(
        """
        `1`: Clear, Few clouds, Partly cloudy, Partly cloudy
        
        `2`: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist
        
        `3`: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds
        """
    )

# Tambahkan di bagian bawah dashboard
st.subheader("Download Data")
col1, col2 = st.columns(2)

with col1:
    csv = main_df.to_csv(index=False)
    st.download_button(
        label="Download Data Harian",
        data=csv,
        file_name="bike_sharing_daily.csv",
        mime="text/csv"
    )

with col2:
    csv_hourly = second_df.to_csv(index=False)
    st.download_button(
        label="Download Data Per Jam",
        data=csv_hourly,
        file_name="bike_sharing_hourly.csv",
        mime="text/csv"
    )

st.caption("Copyright "+ str(datetime.date.today().year) + " " + "[Ida Sri Afiqah](https://id.linkedin.com/in/ida-sri-afiqah-29047b1b0 'Ida Sri Afiqah | LinkedIn')")