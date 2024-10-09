import io
import re
import matplotlib.pyplot as plt
import base64
import numpy as np

def extract_nutrition_data(response_text: str) -> dict:
    # Initializing the nutrition data dictionary
    data = {
        "calories": 0,
        "carbohydrates": 0,
        "protein": 0,
        "fats": 0
    }
    
    # Regex patterns to capture the nutritional values with potential whitespace variations
    calorie_pattern = re.compile(r"總熱量估計為.*?(\d+\.?\d*)\s*大卡")
    carb_pattern = re.compile(r"總碳水估計為.*?(\d+\.?\d*)\s*克")
    protein_pattern = re.compile(r"總蛋白質估計為.*?(\d+\.?\d*)\s*克")
    fat_pattern = re.compile(r"總脂肪估計為.*?(\d+\.?\d*)\s*克")

    # Find the calorie valuefats
    match = calorie_pattern.search(response_text)
    if match:
        data["calories"] = float(match.group(1))

    # Find the carbohydrate value
    match = carb_pattern.search(response_text)
    if match:
        data["carbohydrates"] = float(match.group(1))

    # Find the protein value
    match = protein_pattern.search(response_text)
    if match:
        data["protein"] = float(match.group(1))

    # Find the fat value
    match = fat_pattern.search(response_text)
    if match:
        data["fats"] = float(match.group(1))

    return data

def create_nutrition_chart(data: dict) -> str:
    # Define the data for the pie chart
    labels = ['Carbs', 'Protein', 'Fats']
    sizes = [data['carbohydrates'], data['protein'], data['fats']]  # gram values
    colors = ['#ffcc00', '#ff6666', '#66b3ff']  # Colors for pie chart
    explode = (0.1, 0.1, 0.1)  # Exploding the slices to enhance the 3D effect

    # Total calories (sum of the sizes for simplicity)
    total_calories = data["calories"]

    # Create the figure and axis, and set the background color
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#2e3b4e')  # Set background color

    # Create the pie chart with a shadow effect
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                      autopct='%1.1f%%', startangle=140, shadow=True)

    # Set the percentage colors to match the pie chart slice colors
    for i, autotext in enumerate(autotexts):
        autotext.set_color(colors[i])

    # Remove labels from pie chart itself
    for text in texts:
        text.set_text("")

    # Add custom labels to the left of the pie chart
    ax.text(-1.95, 0.5, "CARBS", fontsize=14, fontweight='bold', color=colors[0], ha='left')
    ax.text(-1.95, 0.35, f"{sizes[0]}g", fontsize=18, fontweight='bold', color=colors[0], ha='left')

    ax.text(-1.95, 0, "PROTEIN", fontsize=14, fontweight='bold', color=colors[1], ha='left')
    ax.text(-1.95, -0.15, f"{sizes[1]}g", fontsize=18, fontweight='bold', color=colors[1], ha='left')

    ax.text(-1.95, -0.5, "FATS", fontsize=14, fontweight='bold', color=colors[2], ha='left')
    ax.text(-1.95, -0.65, f"{sizes[2]}g", fontsize=18, fontweight='bold', color=colors[2], ha='left')

    # Calculate total grams to determine percentages
    total_grams = sum(sizes)

    # Calculate the position (x, y) for each wedge's centroid and add percentage values inside the pie chart
    for i, (wedge, size) in enumerate(zip(wedges, sizes)):
        # Angle for the center of each wedge
        angle = (wedge.theta2 + wedge.theta1) / 2

        # Compute the x and y position for the text (slightly inward from the wedge center)
        x = np.cos(np.radians(angle)) * 0.7  # 0.7 scales the distance to center the text
        y = np.sin(np.radians(angle)) * 0.7

        # Calculate the percentage for the current slice
        percentage = (size / total_grams) * 100

        # Add the percentage inside the wedges
        ax.text(x, y, f'{percentage:.1f}%', ha='center', va='center', fontsize=14, color='white', fontweight='bold')

    # Add total calories at the top of the figure
    ax.text(0, 1.3, f'{total_calories} Cal', ha='center', va='center', fontsize=20, fontweight='bold', color='white')

    # Set the aspect ratio to be equal, so the pie chart is a circle
    ax.set_aspect('equal')

    # Convert plot to PNG image and encode to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return img_base64