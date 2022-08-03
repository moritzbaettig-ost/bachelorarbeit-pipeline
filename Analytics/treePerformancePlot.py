from matplotlib import pyplot as plt

infile = r"sec2sectreePerformance.log"
with open(infile) as f:
    f = f.readlines()

reliabilities = []
for line in f:
    reliabilities.append(float(line.split(",")[2].split(":")[1].split("(")[1].split(")")[0]))

i = 1
alerts = 0
reliabilities_normalized = []
for r in reliabilities:
    if r <=0.2:
        alerts = alerts +1
    reliabilities_normalized.append(alerts/i)
    i=i+1

requests = range(1,len(reliabilities_normalized)+1)
plt.plot(requests, reliabilities_normalized)
plt.title("Typing Tree Performance")
plt.xlabel("Requests")
plt.ylabel("Normalized number of Pathalerts")
plt.grid()
plt.show()