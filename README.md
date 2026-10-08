## 📥 Download & Play
**[👉 Click here to download the standalone Windows .exe and Linux versions!](https://github.com/Doobiesn4x/chromatic-planes/releases/latest)**

*(No installation required. Just extract the .zip and double click the game!)*

Chromatic Planes: The Hadwiger-Nelson Explorer
Chromatic Planes is a procedural puzzle game and citizen-science discovery engine built in Python. It turns one of mathematics' most famous unsolved geometry puzzles—the Hadwiger-Nelson problem—into an interactive, AI-judged coloring book.

(Note: Add one of your F12 screenshots here!)

🧩 The Mathematical Mystery
The Hadwiger-Nelson problem asks a deceptively simple question: What is the minimum number of colors needed to paint the infinite Euclidean plane so that no two points exactly a distance of 1.0 apart share the same color?

For 68 years, mathematicians knew the answer had to be 4, 5, 6, or 7.

In 2018, computer scientist Aubrey de Grey built a massive 1,581-node unit-distance graph that proved it requires at least 5 colors.

Today, the true answer is still unknown. It is either 5, 6, or 7.

🎮 The Gameplay Loop
This game procedurally generates random unit-distance graphs ("Mandalas"). As the game grows the graph, a background Boolean Satisfiability (SAT) Solver instantly calculates the mathematical minimum number of colors needed to paint it (The Par).

Paint the Mandala: Use your palette to color the nodes.

Obey the Law of Distance: If you paint two connected dots the same color, the edge turns red, indicating a unit-distance conflict.

Beat the Par: If you successfully color the entire graph without conflicts, you "Solve" it. If you manage to do it using only the AI's minimum calculated colors, you achieve a MASTERPIECE and log your score in the Visual Gallery Archive.

The Ultimate Goal: If the procedural generator ever spits out a Mandala, and the SAT solver calculates a Par of 6, you will have literally solved an 80-year-old math problem.

🛠 Features
Infinite Procedural Generation: Every level is a unique geometric shape that grows larger and more complex as you progress.

Real-time SAT Solving: Powered by python-sat (Glucose 4.2), the game algorithmically proves the exact chromatic number of the graph as soon as it is generated.

Visual Gallery Archive: The game automatically takes thumbnails of your Masterpieces and ranks them by size. You can export these to PNG files from the Gallery.

Academic DIMACS Export: Press E to instantly export the current graph into a standard .col file. If you find a 6-chromatic graph, you have the raw mathematical data ready to submit to supercomputers or academic journals.

💻 Controls
Left Click: Paint node / Select color

Right Click (Hold): Pan camera

Scroll Wheel: Zoom in/out

C: Clear all colors

R: Reroll the current level (generate a new shape at the same depth)

SPACE: Generate next level (only available after a successful solve)

F12: Take a screenshot (saved to /data/screenshots/)

E: Export raw mathematical graph data (saved to /data/exports/)

ESC: Return to Main Menu

🚀 Installation & Running
Option 1: Standalone Executable (Windows & Linux)
Go to the Actions tab or the Releases page of this repository to download the pre-compiled standalone executable. No installation required!

Option 2: Run from Source
If you want to run the python script directly or modify the code:

Bash
# 1. Clone the repository
git clone https://github.com/doobiens4x/chromatic-planes.git
cd chromatic-planes

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game!
python main.py
🏗 Technology Stack
Engine: Pygame (Hardware-accelerated 2D rendering)

Geometry Math: NumPy (Vector math, coordinate rotation, unit-distance checking)

Algorithmic Proofs: PySAT (Glucose 4.2 Boolean Satisfiability solver)
