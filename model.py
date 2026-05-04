from sklearn.ensemble import RandomForestClassifier

# Training Data:
# [latency, packet_loss, bandwidth]

X = [
    [20, 0, 1000],
    [30, 1, 900],
    [40, 0, 850],

    [150, 5, 400],
    [180, 10, 300],
    [220, 8, 250],

    [999, 100, 0],
    [900, 95, 20],

    [120, 15, 350],
    [170, 20, 280]
]

y = [
    "Normal",
    "Normal",
    "Normal",

    "Slow",
    "Slow",
    "Slow",

    "No Internet",
    "No Internet",

    "Congestion",
    "Congestion"
]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)