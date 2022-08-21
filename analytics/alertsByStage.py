#%%
from matplotlib import pyplot as plt

infile = r"honeypotAlertsByStage.log"
with open(infile) as f:
    f = f.readlines()

filterStage = 0
typingStage = 0
modelStage = 0
for line in f:
    if line.split(":")[4].find("Filter") != -1:
        filterStage = filterStage + 1
    elif line.split(":")[4].find("Typing") != -1:
        typingStage = typingStage + 1
    elif line.split(":")[4].find("Model") != -1:
        modelStage = modelStage + 1
not_detected = 53


print("Filter Stage "+str(filterStage))
print("Typing Stage "+str(typingStage))
print("Model Stage "+str(modelStage))

plt.pie([filterStage, typingStage, not_detected, modelStage], labels=['Filter Stage', 'Typing Stage', 'Not Detected', 'Model Stage'], autopct='%1.1f%%',explode=(1,1,1,0), colors=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c'])
plt.title("Alerts by Stage")
plt.show()
    #stage.append(float(line.split(",")[2].split(":")[1].split("(")[1].split(")")[0]))

# %%
