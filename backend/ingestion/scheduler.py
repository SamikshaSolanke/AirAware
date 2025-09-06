from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", days=14)
def fetch_data():
    print("⏳ Running AQI & Weather fetch jobs...")
    subprocess.run(["python", "fetch_aqi.py"])
    subprocess.run(["python", "fetch_weather.py"])
    print("Jobs completed!")


if __name__ == "__main__":
    print("Scheduler started (runs every 14 days)...")
    scheduler.start()
