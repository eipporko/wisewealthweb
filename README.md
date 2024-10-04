# WiseWealthWeb

WiseWealthWeb is an interactive web application that allows users to visualize financial projections for investments and savings. Built with Streamlit, WiseWealthWeb provides a user-friendly interface for defining financial parameters, projecting growth over time, and viewing detailed charts of projected savings and investment performance. The tool is ideal for individuals who wish to make informed financial decisions by visualizing future growth of their investments and savings.

## Features
- User-defined parameters for monthly contributions, savings and investment rates.
- Configurable number of investment funds with customizable annual returns.
- Detailed financial projections, including total savings, investment growth, and potential taxes.
- Interactive charts showing the evolution of savings and investments over time.

## Installation
To run WiseWealthWeb locally, follow these steps:

1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/WiseWealthWeb.git
   cd WiseWealthWeb
   ```

2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Run the application:
   ```sh
   streamlit run app.py
   ```

After running the above command, a new browser window or tab should open with the WiseWealthWeb application, accessible at `http://localhost:8501`.

## Deployment
To deploy WiseWealthWeb, you can use various platforms that support Streamlit, such as:

### Streamlit Cloud
1. Push your project to GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and log in.
3. Select your GitHub repository and deploy.

### Docker
You can also use Docker to containerize the application for deployment:

1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY . /app
   RUN pip install -r requirements.txt
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py"]
   ```

2. Build and run the Docker image:
   ```sh
   docker build -t wisewealthweb .
   docker run -p 8501:8501 wisewealthweb
   ```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

