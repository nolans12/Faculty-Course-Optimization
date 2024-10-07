# Faculty Course Optimization

## Project Overview

This project implements an algorithm to optimize faculty course assignments based on their preferences while adhering to Teaching Credit (TC) constraints. The algorithm uses linear programming to maximize overall faculty satisfaction.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [File Structure](#file-structure)
6. [Algorithm Description](#algorithm-description)
7. [Output](#output)
8. [Contributing](#contributing)
9. [License](#license)

## Requirements

- Python 3.7+
- pandas
- numpy
- pulp
- matplotlib

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/nolans12/Faculty-Course-Optimization/
   ```

2. Navigate to the project directory:
   ```
   cd faculty-course-optimization
   ```

3. Install the required packages:
   ```
   pip install pandas numpy pulp matplotlib
   ```

## Usage

1. Prepare your input files:
   - `inputs/faculty_w_TC.csv`: Faculty information with TC requirements, MANUAL INPUT
   - `inputs/courses_w_TC.csv`: Course information with TC allocations, MANUAL INPUT
   - `inputs/Teaching Survey.csv`: Teaching faculty survey responses, csv output
   - `inputs/Tenure Survey.csv`: Tenure faculty survey responses, csv output

2. Run the main script:
   ```
   python main.py
   ```

3. Check the `outputs/` directory for results.

## File Structure

- `main.py`: Main script to run the optimization
- `data_processing_funcs.py`: Functions for processing input data
- `post_run_data_funcs.py`: Functions for generating output and visualizations
- `inputs/`: Directory containing input CSV files
- `outputs/`: Directory for output files
- `LaTeX Writeup/`: Directory containing LaTeX documentation

## Algorithm Description

The algorithm uses a mixed-integer linear programming approach to optimize faculty course assignments. It considers the following:

1. Faculty preferences for courses (1-5 or 1-8 scale)
2. Teaching Credit (TC) requirements for faculty
3. TC allocations for courses
4. Multiple section options for some courses
5. Team-taught (split) courses

The objective function minimizes the total cost of assignments, where cost is calculated based on faculty preferences. Constraints ensure that TC requirements are met for both faculty and courses.

For a detailed mathematical formulation, refer to the LaTeX document in the `LaTeX Writeup/` directory.

## Output

The program generates the following outputs, which are all called in the `post_run_data_funcs.py` file:

1. `outputs/faculty_preferences.csv`: CSV file containing all faculty preferences
2. `outputs/course_assignments.csv`: CSV file with the optimized course assignments
3. A bar plot showing the distribution of assignment preferences
