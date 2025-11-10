FROM python:3.11-slim

WORKDIR /streamlit_app

COPY ./requirements.txt /streamlit_app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /streamlit_app

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

