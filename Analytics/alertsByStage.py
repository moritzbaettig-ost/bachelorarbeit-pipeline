from matplotlib import pyplot as plt

infile = r"sec2secAlertsByStage.log"
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

print(filterStage)
print(typingStage)
print(modelStage)

plt.pie([filterStage, typingStage, modelStage], labels=['Filter Stage', 'Typing Stage', 'Model Stage'], autopct='%1.1f%%',explode=(0.1,0.1,0.1))
plt.title("Alerts by Stage")
plt.show()
    #stage.append(float(line.split(",")[2].split(":")[1].split("(")[1].split(")")[0]))
