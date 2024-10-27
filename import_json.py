import matplotlib.pyplot as plt
import numpy as np
import json

with open('output.json', 'r') as f:
    events = json.load(f)


print("1. List events")
print("2. Create event")
print("3. pick an event")

# Main loop
while True:
    # Prompt the user for input
    choice = input("Choose an option  1. List events  2. Create event  3. pick an event: ")

    # List events
    if choice == "1":
        if not events:
            print("No events created yet.")
        else:
            for i, event in enumerate(events):
                print(f"{i+1}.", event, '  ', events[event][0], '  ', events[event][1])

    # Create event
    elif choice == "2":
        title = input("Enter event title: ")
        state = input("Enter event state: ")
        date = input("Enter event date: ")
        events[title] = [state, date, []]
        print("Event created successfully.")

    # Quit
    elif choice == "3":
        print("Exiting program.")
        break

    # Invalid choice
    else:
        print("Invalid choice. Please try again.")

print(events)

with open('output.json', 'w') as f:
    json.dump(events, f)

# Prompt the user to choose an event
while True:
    if not events:
        print("No events created yet.")
        break
    print("Choose an event:")
    event_list = []
    for i, event in enumerate(events):

        print(f"{i+1}.", event, '  ', events[event][0], '  ', events[event][1])
        event_list.append([i, event])
    choice = input("Enter the number of the event: ")
    try:
        event_index = int(choice) -1
        if 0 <= event_index < len(events):
            event = event_list[event_index][1]
            break
        else:
            print("Invalid choice. Please try again.")
    except ValueError:
        print("Invalid choice. Please try again.")


# Print the event details
    print(f"{i+1}.", event, '  ', events[event][0], '  ', events[event][1])

# Prompt the user to input a number between 0 and 1
while True:
    choice = input("Enter probability (a number between 0 and 1): ")
    try:
        number = float(choice)
        if 0 <= number <= 1:
            break
        else:
            print("Invalid choice. Please try again.")
    except ValueError:
        print("Invalid choice. Please try again.")

# Append the number to the event's data list
# print(event)
events[event][2].append(number)

with open('output.json', 'w') as f:
    json.dump(events, f)

# Calculate statistics
mean = np.mean(events[event][2])
std_dev = np.std(events[event][2])
min_val = np.min(events[event][2])
max_val = np.max(events[event][2])

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the mean as a point
ax.plot(0, mean, 'o', color='blue', markersize=10, label='Mean')

# Add error bars for standard deviation
ax.errorbar(0, mean, yerr=std_dev, fmt='none', color='black', capsize=10, label='Standard Deviation')

# Add markers for min and max
ax.plot(0, min_val, marker='_', color='red', markersize=20, label='Min/Max')
ax.plot(0, max_val, marker='_', color='red', markersize=20)

# Add a red square marker at the last element of the data list
ax.plot(0, events[event][2][-1], marker='s', color='red', markersize=10, label='Your guess')

# Customize the plot
ax.set_ylabel('Value')
ax.set_title('Error Bar Plot with Min, Max, Mean, and Standard Deviation')
ax.legend()

# Set y-axis range from 0 to 1
ax.set_ylim(0, 1)

# Remove x-axis ticks
ax.set_xticks([])

# Add a light vertical line to connect min and max
ax.vlines(x=0, ymin=min_val, ymax=max_val, colors='gray', linestyles='--', alpha=0.5)

plt.show()


    