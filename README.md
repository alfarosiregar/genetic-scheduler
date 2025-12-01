# Genetic Scheduler

A Python-based application leveraging genetic algorithms to automate and optimize course scheduling.

## Key Features & Benefits

*   **Automated Scheduling:** Automatically generates class schedules based on provided data.
*   **Optimization:** Utilizes a genetic algorithm to optimize schedules, minimizing conflicts and maximizing preferences.
*   **Data Input:** Allows easy input of course, professor, and room availability data.
*   **User-Friendly Interface:** Uses Streamlit for an intuitive and interactive user experience.
*   **Conflict Resolution:** Aims to resolve scheduling conflicts by intelligently adjusting schedules.
*   **Visualization:** Displays generated schedules in a clear and understandable format.

## Prerequisites & Dependencies

Before running the application, ensure you have the following installed:

*   **Python:** Version 3.6 or higher.
*   **pip:** Python package installer.

Install the required Python packages:

```bash
pip install streamlit pandas openpyxl Pillow
```

## Installation & Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/alfarosiregar/genetic-scheduler.git
    cd genetic-scheduler
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt #If you create a requirement.txt in the main directory with all packages mentioned above
    ```

3.  **Prepare your data:**

    *   Ensure your course data is in the format expected by the application.  See the `mnt/db/Databases.xlsx` and `mnt/db/Kromosom.xlsx` files for example formats. Pay close attention to `config/settings.py` and the `COLUMN_MAPPING` dictionary for specifics on column placement.
    *   Place your data files in the `mnt/db/` directory.

4.  **Run the application:**

    ```bash
    streamlit run app.py
    ```

    This will start the Streamlit application in your web browser.

## Usage Examples

1.  **Data Input:**
    *   Use the sidebar to input or select course and professor data. The application will load data from the specified Excel files.
    *   Select the desired options for each field, such as "Nama Dosen", "Mata Kuliah", etc.

2.  **Running the Genetic Algorithm:**
    *   After inputting the required data, initiate the genetic algorithm using the button in the main app.
    *   The application will then display the initial population, fitness evaluation results, and the optimized schedule.

3.  **Viewing Results:**
    *   The application displays the results of the genetic algorithm, including the initial population, evaluation metrics, and the best-generated schedule.
    *   Visual representations and tables are used to present the schedule in a clear and concise manner.

## Configuration Options

The application's behavior can be configured through the `config/settings.py` file:

*   `DATABASE_PATH`: Path to the Excel file containing course data (`mnt/db/Databases.xlsx`).
*   `KROMOSOM_PATH`: Path to the Excel file containing chromosome data (`mnt/db/Kromosom.xlsx`).
*   `IMAGE_PATH`: Path to the image file used in the application (`mnt/img/schedule_image.jpg`).
*   `COLUMN_MAPPING`: A dictionary that maps column names to their indices in the `Databases.xlsx` file.  Ensure that the values match the location of the columns in your excel sheets.

## Contributing Guidelines

Contributions are welcome! Here's how you can contribute:

1.  **Fork the repository.**
2.  **Create a new branch** for your feature or bug fix.
3.  **Make your changes** and commit them with clear, concise messages.
4.  **Test your changes** thoroughly.
5.  **Submit a pull request** with a detailed description of your changes.

## License Information

This project has no specified license. All rights are reserved by the owner.

## Acknowledgments

*   The Streamlit library for providing a simple way to create interactive web applications with Python.
*   The Pandas library for providing powerful data manipulation and analysis tools.
*   The Openpyxl library for reading and writing Excel files.
*   The Pillow library for working with images.
