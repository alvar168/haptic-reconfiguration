from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Mock Arduino Server Running!"

@app.route("/S1")
def activate_s1():
    print("Mock: Solenoid 1 Activated")
    return "Solenoid 1 Activated"

@app.route("/S2")
def activate_s2():
    print("Mock: Solenoid 2 Activated")
    return "Solenoid 2 Activated"

@app.route("/S3")
def activate_s3():
    print("Mock: Solenoid 3 Activated")
    return "Solenoid 3 Activated"

@app.route("/OFF")
def deactivate():
    print("Mock: All Solenoids Deactivated")
    return "Solenoids Deactivated"

@app.route("/PRESSURE")
def read_pressure():
    import random
    fake_pressure = round(random.uniform(0.5, 5.0), 2)  # Simulate a voltage reading
    print(f"Mock: Pressure Sensor Reading = {fake_pressure}V")
    return str(fake_pressure)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
