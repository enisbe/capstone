FROM python:3.7.2

RUN pip install --upgrade pip

WORKDIR /app

COPY /streamlit_gui/requirements.txt .

RUN pip install --no-cache-dir -r  requirements.txt 


COPY /streamlit_gui/recession_graph.py .
COPY /streamlit_gui/app.py .
COPY /streamlit_gui/forecast.py .

COPY /streamlit_gui/common /app/common  

ENV PORT=
 
CMD streamlit run app.py --server.port=${PORT}  --browser.serverAddress="0.0.0.0"